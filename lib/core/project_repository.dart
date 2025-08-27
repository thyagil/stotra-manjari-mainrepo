import 'dart:convert';
import 'package:http/http.dart' as http;

import 'config.dart';            // for baseUrl
import 'project_models.dart';    // ProjectSummary, ProjectMetadata

/// Repository to load stotra projects & their metadata from the server
class ProjectRepository {
  /// Load list of available projects from stotras.json
  Future<List<ProjectSummary>> loadProjects() async {
    final url = "$baseUrl/stotras.json";
    final response = await http.get(Uri.parse(url));

    if (response.statusCode != 200) {
      throw Exception("❌ Failed to load projects list from $url");
    }

    final data = jsonDecode(response.body);

    // support both `{ "projects": [ ... ] }` or bare list `[ ... ]`
    final List<dynamic> rawList =
    (data is Map<String, dynamic>) ? data["projects"] : data;

    return rawList.map((e) => ProjectSummary.fromJson(e)).toList();
  }

  /// Load full metadata for a single project from metadata.json
  Future<ProjectMetadata> loadMetadata(String projectId) async {
    final url = "$baseUrl/$projectId/metadata/metadata.json";
    final response = await http.get(Uri.parse(url));

    if (response.statusCode != 200) {
      throw Exception("❌ Failed to load metadata for $projectId from $url");
    }

    final data = jsonDecode(response.body);
    return ProjectMetadata.fromJson(data);
  }
}
