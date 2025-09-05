import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'secrets.dart';

/// Map internal lang codes → natural language for OpenAI
const langPrompts = {
  'en': 'English',
  'sa': 'English', // Sanskrit verses → explain in English by default
  'ta': 'Tamil',
  'te': 'Telugu',
  'ka': 'Kannada',
  'ma': 'Malayalam',
  'be': 'Bengali',
  'gu': 'Gujarati',
};

Future<String?> fetchMeaningFromAI(String sloka, String lang) async {
  try {
    final targetLang = langPrompts[lang] ?? 'English';

    final response = await http.post(
      Uri.parse("https://api.openai.com/v1/chat/completions"),
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer $openAiApiKey",
      },
      body: jsonEncode({
        "model": "gpt-4o-mini", // cheap + fast
        "messages": [
          {
            "role": "system",
            "content":
            "You are a Sanskrit scripture teacher. "
                "Provide a short, clear meaning of each verse in $targetLang. "
                "Do not prefix with phrases like 'This means...' or 'The verse translates to...'. "
                "Write the meaning directly, one or two sentences max."
          },
          {
            "role": "user",
            "content": sloka,
          }
        ],
        "max_tokens": 200,
        "temperature": 0.7,
      }),
    );

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      final content = decoded["choices"]?[0]?["message"]?["content"];
      return content?.trim();
    } else {
      debugPrint("⚠️ OpenAI API error: ${response.statusCode} ${response.body}");
      return null;
    }
  } catch (e, st) {
    debugPrint("⚠️ OpenAI exception: $e\n$st");
    return null;
  }
}

Future<List<String?>> fetchMeaningsForChapter(
    List<String> slokas, String lang) async {
  if (slokas.isEmpty) return [];

  final targetLang = langPrompts[lang] ?? 'English';

  try {
    // Build a numbered list for the prompt
    final numbered = slokas.asMap().entries.map((e) {
      final idx = e.key + 1;
      return "$idx. ${e.value}";
    }).join("\n");

    final response = await http.post(
      Uri.parse("https://api.openai.com/v1/chat/completions"),
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer $openAiApiKey",
      },
      body: jsonEncode({
        "model": "gpt-4o-mini",
        "messages": [
          {
            "role": "system",
            "content": "You are a Sanskrit scripture teacher. "
                "Given a numbered list of verses, reply with the same numbers "
                "and their short, clear meanings in $targetLang. "
                "One line per verse. Do not merge verses. "
                "Avoid prefacing with extra text."
          },
          {
            "role": "user",
            "content": numbered,
          }
        ],
        "max_tokens": 2000,
        "temperature": 0.7,
      }),
    );

    if (response.statusCode == 200) {
      final decoded = jsonDecode(response.body);
      final content = decoded["choices"]?[0]?["message"]?["content"];

      if (content == null) return List.filled(slokas.length, null);

      // Split by lines and strip numbers
      final lines = const LineSplitter().convert(content.trim());
      final results = <String?>[];

      for (var i = 0; i < slokas.length; i++) {
        final expectedNum = "${i + 1}.";
        final rawLine = (i < lines.length) ? lines[i].trim() : "";
        final cleaned = rawLine.startsWith(expectedNum)
            ? rawLine.substring(expectedNum.length).trim()
            : rawLine;
        results.add(cleaned.isEmpty ? null : cleaned);
      }

      return results;
    } else {
      debugPrint("⚠️ OpenAI API error: ${response.statusCode} ${response.body}");
      return List.filled(slokas.length, null);
    }
  } catch (e, st) {
    debugPrint("⚠️ OpenAI exception: $e\n$st");
    return List.filled(slokas.length, null);
  }
}
