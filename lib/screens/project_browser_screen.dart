// lib/screens/project_browser_screen.dart
// ✅ This is the BROWSER screen (detail for a single project)

import 'package:flutter/material.dart';
import '../core/languages.dart';
import '../core/project_repository.dart';
import '../core/models.dart';
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
      final metadata = await repo.loadProjectMetadata(widget.project.id);
      setState(() => _metadata = metadata);
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final project = widget.project;

    // 🔹 Debug snapshot
    print("🟤 ProjectBrowserScreen.build called");
    debugPrint("🎨 Browser Theme snapshot:");
    debugPrint("  scaffoldBackground = ${theme.scaffoldBackgroundColor}");
    debugPrint("  cardColor          = ${theme.cardColor}");
    debugPrint("  primary            = ${theme.colorScheme.primary}");
    debugPrint("  onPrimary          = ${theme.colorScheme.onPrimary}");
    debugPrint("  secondary          = ${theme.colorScheme.secondary}");
    debugPrint("  surface            = ${theme.colorScheme.surface}");
    debugPrint("  onSurface          = ${theme.colorScheme.onSurface}");

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(project.title),
          backgroundColor: theme.appBarTheme.backgroundColor,
        ),
        body: _error != null
            ? Center(child: Text("❌ Failed: $_error"))
            : _metadata == null
            ? const Center(child: CircularProgressIndicator())
            : Column(
          children: [
            // 🔹 Top Hero Image
            SizedBox(
              height: 180,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Hero(
                    tag: "project-${project.id}",
                    child: Image.network(
                      project.thumbnail,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => const Icon(
                        Icons.book,
                        size: 80,
                        color: Colors.brown,
                      ),
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [
                          Colors.black.withOpacity(0.5),
                          Colors.transparent
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            // 🔹 Title + Subtitle
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(project.title,
                      style: theme.textTheme.titleLarge),
                  const SizedBox(height: 4),
                  Text(project.subtitle,
                      style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface
                              .withOpacity(0.6))),
                ],
              ),
            ),
            // 🔹 Tabs
            TabBar(
              labelColor: theme.colorScheme.primary,
              unselectedLabelColor: theme.colorScheme.onSurface,
              indicatorColor: theme.colorScheme.secondary,
              tabs: const [
                Tab(text: "Overview"),
                Tab(text: "Contents"),
                Tab(text: "Audio"),
              ],
            ),
            // 🔹 Tab Content
            Expanded(
              child: TabBarView(
                children: [
                  _buildOverviewTab(context, project, _metadata!),
                  VolumesListScreen(
                    projectId: project.id,
                    metadata: _metadata!,
                    lang: currentLang.value,
                  ),
                  _buildAudioTab(context, _metadata!),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewTab(
      BuildContext context, ProjectSummary project, ProjectMetadata metadata) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (metadata.description.isNotEmpty) ...[
            Text(metadata.description, style: theme.textTheme.bodyMedium),
            const SizedBox(height: 12),
          ],
          if (metadata.categories.isNotEmpty)
            Wrap(
              spacing: 8,
              children: metadata.categories
                  .map((c) => Chip(
                label: Text(c),
                backgroundColor: theme.colorScheme.secondaryContainer,
                labelStyle:
                TextStyle(color: theme.colorScheme.onSecondary),
              ))
                  .toList(),
            ),
          const SizedBox(height: 12),
          if (metadata.languages.isNotEmpty)
            Row(
              children: [
                const Icon(Icons.language, size: 20),
                const SizedBox(width: 6),
                Text("Available in: ${metadata.languages.join(", ")}",
                    style: theme.textTheme.bodySmall),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildAudioTab(BuildContext context, ProjectMetadata metadata) {
    final theme = Theme.of(context);

    if (metadata.audioSamples.isEmpty) {
      return Center(
          child:
          Text("No audio samples available", style: theme.textTheme.bodyMedium));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: metadata.audioSamples.length,
      itemBuilder: (context, index) {
        final sample = metadata.audioSamples[index];
        return Card(
          margin: const EdgeInsets.symmetric(vertical: 8),
          child: ListTile(
            leading: Icon(Icons.play_circle_fill,
                color: theme.colorScheme.secondary),
            title: Text(sample.title),
            subtitle: Text(sample.url),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text("▶️ Play: ${sample.title}")),
              );
            },
          ),
        );
      },
    );
  }
}
