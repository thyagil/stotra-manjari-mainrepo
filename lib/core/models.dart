import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'config.dart';  // 👈 brings in baseProjectsRoot

import 'io_helpers.dart';
import 'url_paths.dart';
import 'ui_settings.dart';

/// ========== PROJECT SUMMARY ==========
class ProjectSummary {
  final String id;
  final String title;
  final String subtitle;
  final String thumbnail;
  final String banner;     // 👈 NEW
  final bool isPremium;
  final bool featured;

  ProjectSummary({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.thumbnail,
    required this.banner,   // 👈 NEW
    required this.isPremium,
    this.featured = false
  });

  factory ProjectSummary.fromJson(Map<String, dynamic> json) {
    final projectId = json['id'] as String? ?? '';

    final coverPath = resolveProjectImage(
      projectId: projectId,
      relativePath: json['cover'] as String?,
    );

    final thumbPath = resolveProjectImage(
      projectId: projectId,
      relativePath: json['thumbnail'] as String?,
    );
    final bannerPath = resolveProjectImage(
      projectId: projectId,
      relativePath: json['banner'] as String?,
    );

    return ProjectSummary(
      id: projectId,
      title: json['title'] as String? ?? '',
      subtitle: json['subtitle'] as String? ?? '',
      thumbnail: thumbPath.isNotEmpty ? thumbPath : coverPath,
      banner: bannerPath.isNotEmpty ? bannerPath : coverPath,
      isPremium: (json['monetization']?['isPremium'] as bool?) ?? false,
      featured: json['featured'] as bool? ?? false,   // 👈 safe fallback
    );
  }
}


/// ========== PROJECT METADATA ==========
class ProjectMetadata {
  final String id;
  final String title;
  final String description;
  final String type; // "volumeBased" or "single"
  final List<VolumeSummary> volumes;

  // Optional fields
  final List<String> categories;
  final List<String> languages;
  final List<Contributor> contributors;
  final List<AudioSample> audioSamples;
  final bool isPremium;
  final String cover;
  final String banner;

  ProjectMetadata({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.volumes,
    this.categories = const [],
    this.languages = const [],
    this.contributors = const [],
    this.audioSamples = const [],
    this.isPremium = false,
    this.cover = "",
    this.banner = "",
  });

  factory ProjectMetadata.fromJson(Map<String, dynamic> json) {
    final projectId = json['id'] as String? ?? json['code'] as String? ?? '';

    return ProjectMetadata(
      id: projectId,
      title: json['title'] as String? ?? '',
      description: json['description'] as String? ?? '',
      type: json['type'] as String? ?? 'volumeBased',
      volumes: (json['volumes'] as List<dynamic>? ?? [])
          .map((v) => VolumeSummary.fromJson({
        ...v as Map<String, dynamic>,
        'projectId': projectId, // ✅ inject parent projectId
          }))
          .toList(),
      categories: (json['categories'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
      languages: (json['languages'] as List<dynamic>? ?? [])
          .map((e) => e.toString())
          .toList(),
      contributors: (json['contributors'] as List<dynamic>? ?? [])
          .map((c) => Contributor.fromJson(c as Map<String, dynamic>))
          .toList(),
      audioSamples: (json['audioSamples'] as List<dynamic>? ?? [])
          .map((a) => AudioSample.fromJson(a as Map<String, dynamic>))
          .toList(),
      isPremium: (json['monetization']?['isPremium'] as bool?) ?? false,

      cover: resolveProjectImage(
        projectId: projectId,
        relativePath: json['cover'] as String? ?? '',
      ),
      banner: resolveProjectImage(
        projectId: projectId,
        relativePath: json['banner'] as String? ?? '',
      ),
    );
  }
}

/// ========== VOLUME METADATA ==========
class VolumeMetadata {
  final String id;
  final String title;
  final int index;
  final int chapters;
  final int state; // 0=hidden, 1=coming soon, 2=enabled
  final List<ChapterSummary> chaptersList;

  VolumeMetadata({
    required this.id,
    required this.title,
    required this.index,
    required this.chapters,
    required this.state,
    required this.chaptersList,
  });

  factory VolumeMetadata.fromJson(Map<String, dynamic> json) {
    return VolumeMetadata(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      index: json['index'] as int? ?? 0,
      chapters: json['chapters'] as int? ?? 0,
      state: json['state'] as int? ?? 2,
      chaptersList: (json['chaptersList'] as List<dynamic>? ?? [])
          .map((c) => ChapterSummary.fromJson(c as Map<String, dynamic>))
          .toList(),
    );
  }

  bool get isEnabled => state == 2;
  bool get isComingSoon => state == 1;
  bool get isHidden => state == 0;
}

/// ========== CHAPTER METADATA ==========
class ChapterMetadata {
  final String id;
  final String? volumeId; // optional
  final String title;
  final int index;
  final int state;
  final String description;
  final int? verses; // optional placeholder

  ChapterMetadata({
    required this.id,
    required this.volumeId,
    required this.title,
    required this.index,
    required this.state,
    required this.description,
    this.verses,
  });

  factory ChapterMetadata.fromJson(Map<String, dynamic> json) {
    return ChapterMetadata(
      id: json['id'] as String? ?? '',
      volumeId: json['volumeId'] as String?,
      title: json['title'] as String? ?? '',
      index: json['index'] as int? ?? 0,
      state: json['state'] as int? ?? 2,
      description: json['description'] as String? ?? '',
      verses: json['verses'] as int?,
    );
  }

  bool get isEnabled => state == 2;
  bool get isComingSoon => state == 1;
  bool get isHidden => state == 0;
}

/// ========== SUPPORTING SUMMARY CLASSES ==========
class VolumeSummary {
  final int index;
  final String id;
  final String title;   // 👈 renamed from name → title
  final int chapters;
  final int state;
  final String cover; // ✅ add this

  VolumeSummary({
    required this.index,
    required this.id,
    required this.title,
    required this.chapters,
    required this.state,
    this.cover = "", // ✅ default empty string
  });

  factory VolumeSummary.fromJson(Map<String, dynamic> json) {
    final projectId = json['projectId'] as String? ?? "";

    return VolumeSummary(
      index: json['index'] as int? ?? 0,
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      chapters: json['chapters'] as int? ?? 0,
      state: json['state'] as int? ?? 2,
      cover: resolveProjectImage(              // 👈 important
        projectId: projectId,
        relativePath: json['cover'] as String?,
      ),
    );
  }

}

class ChapterSummary {
  final int index;
  final String id;
  final String title;
  final int? verses;
  final int state;

  ChapterSummary({
    required this.index,
    required this.id,
    required this.title,
    this.verses,
    required this.state,
  });

  factory ChapterSummary.fromJson(Map<String, dynamic> json) {
    return ChapterSummary(
      index: json['index'] as int? ?? 0,
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      verses: json['verses'] as int?,
      state: json['state'] as int? ?? 2,
    );
  }
}

class Contributor {
  final String role;
  final String name;

  Contributor({required this.role, required this.name});

  factory Contributor.fromJson(Map<String, dynamic> json) {
    return Contributor(
      role: json['role'] as String? ?? '',
      name: json['name'] as String? ?? '',
    );
  }
}

class AudioSample {
  final String title;
  final String url;

  AudioSample({required this.title, required this.url});

  factory AudioSample.fromJson(Map<String, dynamic> json) {
    return AudioSample(
      title: json['title'] as String? ?? '',
      url: json['url'] as String? ?? '',
    );
  }
}

/// ========== VERSE LINE ==========
class VerseLine {
  final String id;
  final int startMs;
  final int endMs;
  final String text;
  final Map<String, String> meanings;
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
}

/// ========== CHAPTER (Player-Ready) ==========
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

  static Future<Chapter> fromMetadata({
    required String projectId,
    required String volumeId,
    required ChapterMetadata metadata,
    required String language,
  }) async {
    final chapterId = metadata.id;

    final versesPath = buildVersesPath(
      projectId: projectId,
      volumeId: volumeId,
      chapterId: chapterId,
      lang: language,
    );
    final durationsPath = buildDurationsPath(
      projectId: projectId,
      volumeId: volumeId,
      chapterId: chapterId,
    );
    final meaningsPath = buildMeaningsPath(
      projectId: projectId,
      volumeId: volumeId,
      chapterId: chapterId,
      lang: language,
    );

    final versesText = await loadTextFile(versesPath);
    final durationsText = await loadTextFile(durationsPath);

    String meaningsText = "";
    if (UISettings.meaningsInVerseLang || language == "en") {
      try {
        meaningsText = await loadTextFile(meaningsPath);
      } catch (e) {
        debugPrint("⚠️ No meanings at $meaningsPath ($e)");
      }
    }

    return _parseFromStrings(
      id: metadata.id,
      title: metadata.title,
      language: language,
      versesText: versesText,
      meaningsText: meaningsText,
      durationsText: durationsText,
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
    print("📥 versesText length = ${versesText.length}");
    print("📥 First 200 chars of versesText:\n${versesText.substring(0, versesText.length.clamp(0, 200))}");

    final allVerseLines = const LineSplitter().convert(stripBom(versesText));
    print("📥 allVerseLines count = ${allVerseLines.length}");

    int startIndex =
    allVerseLines.indexWhere((line) => line.trim() == "--END METADATA");
    if (startIndex == -1) startIndex = -1;
    print("📥 startIndex = $startIndex");

    final verseLines = allVerseLines
        .skip(startIndex + 1)
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    print("📥 verseLines count = ${verseLines.length}");

    final allMeaningLines = const LineSplitter().convert(stripBom(meaningsText));
    int mStartIndex =
    allMeaningLines.indexWhere((line) => line.trim() == "--END METADATA");
    if (mStartIndex == -1) mStartIndex = -1;

    final meaningLines = allMeaningLines
        .skip(mStartIndex + 1)
        .map((e) => e.trimRight())
        .where((e) => e.isNotEmpty)
        .toList();

    final durationLines = const LineSplitter()
        .convert(stripBom(durationsText))
        .map((e) => e.trim())
        .where((e) => e.isNotEmpty)
        .toList();

    final timings = <(int, int)>[];
    for (var i = 0; i < durationLines.length; i++) {
      final row = durationLines[i];
      if (i == 0 && row.toLowerCase().startsWith("offset,duration")) continue;
      final parts = row.split(',');
      if (parts.length < 2) continue;
      final start = _parseTimeToMs(parts[0]);
      final dur = _parseTimeToMs(parts[1]);
      if (start == null || dur == null) continue;
      timings.add((start, start + dur));
    }

    final lines = <VerseLine>[];
    for (var i = 0; i < verseLines.length; i++) {
      final verse = verseLines[i];
      final meaning = i < meaningLines.length ? meaningLines[i] : "";
      int startMs =
      (i < timings.length) ? timings[i].$1 : (i == 0 ? 0 : lines.last.endMs);
      int endMs =
      (i < timings.length) ? timings[i].$2 : startMs + 2000;

      lines.add(VerseLine(
        id: '${i + 1}',
        startMs: startMs,
        endMs: endMs,
        text: verse,
        meanings: {
          if (meaning.isNotEmpty) (language == "en" ? "en" : language): meaning,
        },
      ));
    }

    return Chapter(id: id, title: title, language: language, lines: lines);
  }

  static int? _parseTimeToMs(String raw) {
    final v = raw.trim().replaceAll('"', '').replaceAll("'", '');
    final frac = RegExp(r'^(\d+)\s*/\s*(\d+)\s*s?$').firstMatch(v);
    if (frac != null) {
      final num = int.parse(frac.group(1)!);
      final den = int.parse(frac.group(2)!);
      if (den == 0) return null;
      return ((num * 1000) / den).round();
    }
    final secs = RegExp(r'^(\d+)\s*s$').firstMatch(v);
    if (secs != null) return int.parse(secs.group(1)!) * 1000;
    if (RegExp(r'^\d+$').hasMatch(v)) return int.parse(v);
    return null;
  }
}
