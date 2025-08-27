import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;

/// Try to load a meanings JSON file from assets.
/// Returns a list of strings (empty if file missing or malformed).
Future<List<String>> tryLoadMeaningsJson(String assetPath) async {
  try {
    final raw = await rootBundle.loadString(assetPath, cache: false);
    final parsed = jsonDecode(raw);
    if (parsed is List) {
      return parsed.map((e) => e.toString()).toList();
    }
    return const [];
  } catch (e) {
    // File not found or invalid JSON
    return const [];
  }
}

Future<String> loadStringOrThrow(String path) async {
  try {
    return await rootBundle.loadString(path, cache: false);
  } catch (e) {
    throw Exception('Asset missing or unreadable: $path ($e)');
  }
}

Future<bool> assetExists(String path) async {
  try {
    await rootBundle.load(path);
    return true;
  } catch (_) {
    return false;
  }
}

String stripBom(String s) {
  const bom = '\uFEFF';
  return s.startsWith(bom) ? s.substring(1) : s;
}