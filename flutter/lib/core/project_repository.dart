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
    if (data is! List) throw FormatException("❌ Expected list for marketplace.json");

    return data
        .map((projJson) => ProjectSummary.fromJson(projJson as Map<String, dynamic>))
        .toList();
  }

  /// 🔹 Full project details
  Future<ProjectMetadata> loadProjectMetadata(String projectId) async {
    final data = await _loadJson(MetadataPath.project(projectId));
    return ProjectMetadata.fromJson(data);
  }

  /// 🔹 Get a specific volume directly from project metadata
  VolumeSummary? loadVolumeMetadata(ProjectMetadata project, String volumeId) {
    try {
      return project.volumes.firstWhere((v) => v.id == volumeId);
    } catch (_) {
      return null;
    }
  }

  /// 🔹 Get a specific chapter directly from project metadata
  ChapterSummary? loadChapterMetadata(
      ProjectMetadata project, String volumeId, String chapterId) {
    final volume = loadVolumeMetadata(project, volumeId);
    if (volume == null) return null;

    try {
      return volume.chaptersList.firstWhere((c) => c.id == chapterId);
    } catch (_) {
      return null;
    }
  }
}


