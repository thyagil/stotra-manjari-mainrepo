import 'config.dart';

/// All chapter-level resources are convention-based:
/// - verses.txt
/// - meanings.txt
/// - durations.csv
/// - audio.m4a (or audio.mp3)

String buildVersesPath({
  required String projectId,
  required String volumeId,
  required String chapterId,
  required String lang,
}) {
  return "$baseProjectsRoot/$projectId/volumes/$volumeId/chapters/$chapterId/lang/$lang/verses.txt";
}

String buildMeaningsPath({
  required String projectId,
  required String volumeId,
  required String chapterId,
  required String lang,
}) {
  return "$baseProjectsRoot/$projectId/volumes/$volumeId/chapters/$chapterId/lang/$lang/meanings.txt";
}

String buildDurationsPath({
  required String projectId,
  required String volumeId,
  required String chapterId,
}) {
  return "$baseProjectsRoot/$projectId/volumes/$volumeId/chapters/$chapterId/durations.csv";
}

String buildAudioPath({
  required String projectId,
  required String volumeId,
  required String chapterId,
  String format = "m4a",
}) {
  return "$baseProjectsRoot/$projectId/volumes/$volumeId/chapters/$chapterId/audio.$format";
}

/// ==================== IMAGE PATHS ====================

/// Builds path for project-level images (cover, banner, etc.)
String buildProjectImagePath({
  required String projectId,
  required String fileName, // e.g. "cover.jpg" or "banner.jpg"
}) {
  final url = "$baseProjectsRoot/$projectId/images/$fileName";
  print("🖼️ buildProjectImagePath → $url");
  return url;
}

/// Builds path for volume-level images if you want separate volume covers later
String buildVolumeImagePath({
  required String projectId,
  required String volumeId,
  required String fileName,
}) {
  final url = "$baseProjectsRoot/$projectId/volumes/$volumeId/images/$fileName";
  print("🖼️ buildVolumeImagePath → $url");
  return url;
}

String resolveRelativePath({
  required String basePath,     // e.g. "projects/"
  required String relativePath, // e.g. "ramayanam_sriramghanapatigal/images/cover.jpg"
}) {
  if (relativePath.startsWith("http")) {
    print("🖼️ resolveRelativePath → already absolute: $relativePath");
    return relativePath;
  }
  final url = "$baseProjectsRoot/$relativePath";
  print("🖼️ resolveRelativePath(base=$basePath) → $url");
  return url;
}

String resolveProjectImage({
  required String projectId,
  String? relativePath,
}) {
  if (relativePath == null || relativePath.isEmpty) {
    return '';
  }
  if (relativePath.startsWith('http')) {
    return relativePath; // already a full URL
  }

  // ✅ If relativePath already has projectId, don’t add it again
  if (relativePath.startsWith(projectId)) {
    return "$baseProjectsRoot/$relativePath";
  }

  // ✅ Otherwise, prefix with projectId
  return "$baseProjectsRoot/$projectId/$relativePath";
}

