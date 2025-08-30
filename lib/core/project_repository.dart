import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'dart:io';

import 'config.dart';
import 'models.dart';
import 'metadata_paths.dart';

class ProjectRepository {

  Future<dynamic> _loadJson(String url) async {
    print("📥 Fetching $url");
    final response = await http.get(Uri.parse(url));
    if (response.statusCode != 200) {
      throw Exception("❌ Failed to load $url (status ${response.statusCode})");
    }
    try {
      return jsonDecode(response.body);
    } catch (e) {
      throw Exception("❌ Failed to parse JSON from $url: $e");
    }
  }

  /// 🔹 For Marketplace – lightweight summaries
  Future<List<ProjectSummary>> loadProjects() async {
    final data = await _loadJson(MetadataPath.projects());
    final rawList = (data is Map<String, dynamic>) ? data["projects"] : data;
    return (rawList as List<dynamic>).map((e) {
      final meta = ProjectMetadata.fromJson(e);
      return ProjectSummary(
        id: meta.id,
        title: meta.title,
        subtitle: meta.description, // or subtitle if available
        thumbnail: meta.cover,
        banner: meta.banner,
        isPremium: meta.isPremium,
        featured: (e["featured"] as bool?) ?? false, // 👈 ADD THIS
      );
    }).toList();
  }

  /// 🔹 Full project details (for ProjectBrowserScreen)
  Future<ProjectMetadata> loadProjectMetadata(String projectId) async {
    final data = await _loadJson(MetadataPath.project(projectId));
    return ProjectMetadata.fromJson(data);
  }

  /// 🔹 Volume-level metadata
  Future<VolumeMetadata> loadVolumeMetadata(String projectId, String volumeId) async {
    final data = await _loadJson(MetadataPath.volume(projectId, volumeId));
    return VolumeMetadata.fromJson(data);
  }

  /// 🔹 Chapter-level metadata
  Future<ChapterMetadata> loadChapterMetadata(
      String projectId, String volumeId, String chapterId) async {
    final data =
    await _loadJson(MetadataPath.chapter(projectId, volumeId, chapterId));
    return ChapterMetadata.fromJson(data);
  }
}
