import 'package:flutter/material.dart';
import 'package:stotra_manjari/core/languages.dart';
import '../core/project_repository.dart';
import '../core/project_models.dart';
import 'volumes_list_screen.dart';

class ProjectBrowserScreen extends StatefulWidget {
  final ProjectSummary project;

  const ProjectBrowserScreen({super.key, required this.project});

  @override
  State<ProjectBrowserScreen> createState() => _ProjectBrowserScreenState();
}

class _ProjectBrowserScreenState extends State<ProjectBrowserScreen> {
  ProjectMetadata? _metadata;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMetadata();
  }

  Future<void> _loadMetadata() async {
    try {
      final repo = ProjectRepository();
      final metadata = await repo.loadMetadata(widget.project.id); // ✅ FIXED
      setState(() => _metadata = metadata);
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.project.title)),
      body: _error != null
          ? Center(child: Text("❌ Failed: $_error"))
          : _metadata == null
          ? const Center(child: CircularProgressIndicator())
          : VolumesListScreen(
        projectId: widget.project.id,   // ✅ pass projectId
        metadata: _metadata!,           // ✅ pass ProjectMetadata
        lang: currentLang.value,        // ✅ pass language
      ),
    );
  }
}
