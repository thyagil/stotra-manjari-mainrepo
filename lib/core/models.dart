import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class VolumeInfo {
  final int index; // 1..6
  final String name;
  final int chapterCount;
  const VolumeInfo(this.index, this.name, this.chapterCount);
}

// ========== VERSE LINE ==========
class VerseLine {
  final String id;
  final int startMs;
  final int endMs;
  final String text;

  /// Meanings stored per language, e.g. {"en": "Meaning in English", "ta": "அர்த்தம்"}
  final Map<String, String> meanings;

  /// Track whether a meaning has been requested (per language)
  final Set<String> requestedLangs;

  VerseLine({
    required this.id,
    required this.startMs,
    required this.endMs,
    required this.text,
    Map<String, String>? meanings,
    Set<String>? requestedLangs,
  })  : meanings = meanings ?? {},
        requestedLangs = requestedLangs ?? {};

  String? meaningFor(String lang) => meanings[lang];

  void setMeaning(String lang, String value) {
    meanings[lang] = value;
    requestedLangs.add(lang);
  }

  VerseLine copyWith({
    String? id,
    int? startMs,
    int? endMs,
    String? text,
    Map<String, String>? meanings,
    Set<String>? requestedLangs,
  }) {
    return VerseLine(
      id: id ?? this.id,
      startMs: startMs ?? this.startMs,
      endMs: endMs ?? this.endMs,
      text: text ?? this.text,
      meanings: meanings ?? Map.of(this.meanings),
      requestedLangs: requestedLangs ?? Set.of(this.requestedLangs),
    );
  }
}

// ========== CHAPTER ==========
class Chapter {
  final String id;
  final String title;
  final String language; // e.g. "sa"
  final List<VerseLine> lines;

  Chapter({
    required this.id,
    required this.title,
    required this.language,
    required this.lines,
  });

  /* ------------------------ fromNetwork ------------------------ */
  static Future<Chapter> fromNetwork({
    required String id,
    required String title,
    required String language,
    required String textUrl,
    required String meaningsUrl,
    required String durationsUrl,
    bool loadMeanings = true,
  }) async {
    // --- Verses ---
    final textRes = await http.get(Uri.parse(textUrl));
    if (textRes.statusCode != 200) {
      throw Exception("Failed to load verses from $textUrl");
    }

    // --- Durations ---
    final durationsRes = await http.get(Uri.parse(durationsUrl));
    if (durationsRes.statusCode != 200) {
      throw Exception("Failed to load durations from $durationsUrl");
    }

    // --- Meanings (only if enabled, and only English for now) ---
    String meaningsText = "";
    if (loadMeanings && language == "en") {
      try {
        final meaningsRes = await http.get(Uri.parse(meaningsUrl));
        if (meaningsRes.statusCode == 200) {
          meaningsText = meaningsRes.body;
        } else {
          debugPrint("⚠️ No meanings file at $meaningsUrl, starting empty.");
        }
      } catch (e) {
        debugPrint("⚠️ Could not fetch meanings: $e");
      }
    }

    return _parseFromStrings(
      id: id,
      title: title,
      language: language,
      versesText: textRes.body,
      meaningsText: meaningsText,
      durationsText: durationsRes.body,
    );
  }

  static Chapter _parseFromStrings({
    required String id,
    required String title,
    required String language,
    required String versesText,
    required String meaningsText,
    required String durationsText,
  }) {
    // --- Verses ---
    final allVerseLines = const LineSplitter().convert(stripBom(versesText));
    int startIndex = allVerseLines.indexWhere((line) => line.trim() == "--END METADATA");
    if (startIndex == -1) startIndex = -1;

    final verseLines = allVerseLines
        .skip(startIndex + 1)
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    // --- Meanings ---
    final allMeaningLines = const LineSplitter().convert(stripBom(meaningsText));
    int mStartIndex = allMeaningLines.indexWhere((line) => line.trim() == "--END METADATA");
    if (mStartIndex == -1) mStartIndex = -1;

    final meaningLines = allMeaningLines
        .skip(mStartIndex + 1)
        .map((e) => e.trimRight())
        .where((e) => e.isNotEmpty)
        .toList();

    // --- Durations ---
    final durationLines = const LineSplitter()
        .convert(stripBom(durationsText))
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    final timings = <(int startMs, int endMs)>[];
    for (var i = 0; i < durationLines.length; i++) {
      final row = durationLines[i];
      if (i == 0 && row.toLowerCase().startsWith("offset,duration")) {
        continue; // skip header
      }
      final parts = row.split(',');
      if (parts.length < 2) continue;
      final start = _parseTimeToMs(parts[0]);
      final dur = _parseTimeToMs(parts[1]);
      if (start == null || dur == null) continue;
      timings.add((start, start + dur));
    }

    // --- Merge ---
    final lines = <VerseLine>[];
    for (var i = 0; i < verseLines.length; i++) {
      final verse = verseLines[i];
      final meaning = i < meaningLines.length ? meaningLines[i] : "";

      int startMs = 0;
      int endMs = 0;
      if (i < timings.length) {
        (startMs, endMs) = timings[i];
      } else {
        startMs = (i == 0) ? 0 : lines.last.endMs;
        endMs = startMs + 2000;
      }

      lines.add(
        VerseLine(
          id: '${i + 1}',
          startMs: startMs,
          endMs: endMs,
          text: verse,
          meanings: {
            if (meaning.isNotEmpty) (language == "en" ? "en" : language): meaning,
          },
        ),
      );
    }

    return Chapter(
      id: id,
      title: title,
      language: language,
      lines: lines,
    );
  }

  static String stripBom(String s) {
    const bom = '\uFEFF';
    return s.startsWith(bom) ? s.substring(1) : s;
  }

  static int? _parseTimeToMs(String raw) {
    final v = raw.trim().replaceAll('"', '').replaceAll("'", '');

    final frac = RegExp(r'^(\d+)\s*/\s*(\d+)\s*s?$');
    final m1 = frac.firstMatch(v);
    if (m1 != null) {
      final num = int.parse(m1.group(1)!);
      final den = int.parse(m1.group(2)!);
      if (den == 0) return null;
      return ((num * 1000) / den).round();
    }

    final secs = RegExp(r'^(\d+)\s*s$').firstMatch(v);
    if (secs != null) return int.parse(secs.group(1)!) * 1000;

    if (RegExp(r'^\d+$').hasMatch(v)) return int.parse(v);

    return null;
  }
}
