import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'models.dart';
import 'io_helpers.dart';
import 'url_builder.dart';

/// Loads chapter descriptions for a given project + volume
Future<List<String>> loadChapterDescriptions({
  required String projectId,
  required int volumeIndex,
}) async {
  final url = chapterDescriptionsUrl(projectId, volumeIndex);

  try {
    final response = await http.get(Uri.parse(url));
    if (response.statusCode != 200) {
      debugPrint('⚠️ No descriptions file at $url, using defaults.');
      return const [];
    }

    var raw = Chapter.stripBom(response.body);
    final lines = const LineSplitter()
        .convert(raw)
        .map((e) {
      final t = e.trim();
      if (t.isEmpty) return '';
      final parts = t.split(':');
      return parts.length > 1 ? parts.sublist(1).join(':').trim() : t;
    })
        .where((e) => e.isNotEmpty)
        .toList();

    return lines;
  } catch (e) {
    debugPrint('⚠️ Failed to load descriptions at $url: $e');
    return const [];
  }
}

/// 🔹 All paths now take projectId as parameter

String txtPath(String projectId, String lang, int v, int c) =>
    buildVersesUrl(
      projectId: projectId,
      volumeId: "volume${v.toString().padLeft(2, '0')}",
      chapterId: "chapter${c.toString().padLeft(2, '0')}",
      lang: lang,
    );

String meaningsPath(String projectId, String lang, int v, int c) =>
    buildMeaningsUrl(
      projectId: projectId,
      volumeId: "volume${v.toString().padLeft(2, '0')}",
      chapterId: "chapter${c.toString().padLeft(2, '0')}",
      lang: lang,
    );

String durationsPath(String projectId, int v, int c) =>
    buildDurationsUrl(
      projectId: projectId,
      volumeId: "volume${v.toString().padLeft(2, '0')}",
      chapterId: "chapter${c.toString().padLeft(2, '0')}",
    );

String audioPreferred(String projectId, int v, int c, {String format = "m4a"}) =>
    buildAudioUrl(
      projectId: projectId,
      volumeId: "volume${v.toString().padLeft(2, '0')}",
      chapterId: "chapter${c.toString().padLeft(2, '0')}",
      format: format,
    );

String audioFallback(String projectId, int v, int c, {String format = "mp3"}) =>
    buildAudioUrl(
      projectId: projectId,
      volumeId: "volume${v.toString().padLeft(2, '0')}",
      chapterId: "chapter${c.toString().padLeft(2, '0')}",
      format: format,
    );
