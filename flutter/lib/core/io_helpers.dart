import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'config.dart';

/// Load text from either local assets or remote URL, depending on [useLocal].
Future<String> loadTextFile(String pathOrUrl) async {
  try {
    // If it's clearly an http/https URL → always fetch over network
    if (pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")) {
      final res = await http.get(Uri.parse(pathOrUrl));
      if (res.statusCode == 200) {
        return utf8.decode(res.bodyBytes); // force UTF-8
      }
      throw Exception("❌ HTTP ${res.statusCode} for $pathOrUrl");
    }

    // Otherwise: load as Flutter bundled asset
    return await rootBundle.loadString(pathOrUrl, cache: false);
  } catch (e) {
    throw Exception("❌ Could not load $pathOrUrl ($e)");
  }
}



/// Try to load a meanings JSON file from assets.
Future<List<String>> tryLoadMeaningsJson(String assetPath) async {
  try {
    final raw = await rootBundle.loadString(assetPath, cache: false);
    final parsed = jsonDecode(raw);
    if (parsed is List) {
      return parsed.map((e) => e.toString()).toList();
    }
    return const [];
  } catch (_) {
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
