import 'config.dart';

/// Utility to normalize paths (avoid double slashes)
String _joinPath(String root, String leaf) {
  if (root.endsWith('/')) {
    return '$root$leaf';
  } else {
    return '$root/$leaf';
  }
}

class MetadataPath {
  /// Marketplace-level metadata
  static String projects() =>
      _joinPath(baseProjectsRoot, "metadata.json");

  /// Per-project metadata
  static String project(String projectId) =>
      _joinPath(baseProjectsRoot, "$projectId/metadata.json");

  /// Per-volume metadata
  static String volume(String projectId, String volumeId) =>
      _joinPath(baseProjectsRoot, "$projectId/volumes/$volumeId/metadata.json");

  /// Per-chapter metadata
  static String chapter(String projectId, String volumeId, String chapterId) =>
      _joinPath(baseProjectsRoot,
          "$projectId/volumes/$volumeId/chapters/$chapterId/metadata.json");
}
