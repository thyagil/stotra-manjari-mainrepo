// lib/screens/project_browser_screen.dart
import 'package:flutter/material.dart';
import '../core/languages.dart';
import '../core/project_repository.dart';
import '../core/models.dart';
import '../core/ui_settings.dart';
import 'volumes_list_screen.dart';
import 'chapters_list_screen.dart';
import 'player_screen.dart';

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
    final smColors = activeTheme.smColors;
    final project = widget.project;

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            project.title,
            style: TextStyle(
              color: smColors.projectBrowserTitle,
              fontWeight: FontWeight.w700,
              fontSize: 20,
            ),
          ),
          backgroundColor: smColors.versePlayerControlColor, // ✅ gold appbar
          centerTitle: true,
          elevation: 2,
        ),
        body: _error != null
            ? Center(child: Text("❌ Failed: $_error"))
            : _metadata == null
            ? const Center(child: CircularProgressIndicator())
            : Column(
          children: [
            // 🔹 Banner
            Container(
              height: 200,
              margin: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.25),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              clipBehavior: Clip.hardEdge,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Hero(
                    tag: "project-${project.id}",
                    child: Image.network(
                      project.banner.isNotEmpty
                          ? project.banner
                          : project.cover,
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
                  Positioned(
                    bottom: 12,
                    right: 12,
                    child: FloatingActionButton(
                      mini: true,
                      backgroundColor: _metadata!.isPremium
                          ? Colors.grey
                          : smColors.versePlayerControlColor,
                      onPressed: _metadata!.isPremium
                          ? null
                          : () {
                        final metadata = _metadata!;
                        switch (metadata.format) {
                          case "volume":
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => VolumesListScreen(
                                  projectId: project.id,
                                  metadata: metadata,
                                  lang: currentLang.value,
                                ),
                              ),
                            );
                            break;

                          case "chapter":
                            final volume = metadata.volumes.first;
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => ChaptersListScreen(
                                  projectId: project.id,
                                  volume: volume,
                                  lang: currentLang.value,
                                ),
                              ),
                            );
                            break;

                          case "standalone":
                            final volume = metadata.volumes.first;
                            final chapter = volume.chaptersList.first;
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => PlayerScreen(
                                  projectId: project.id,
                                  volumeId: volume.id,
                                  chapterMeta: chapter,
                                  language: currentLang.value,
                                ),
                              ),
                            );
                            break;

                          default:
                            debugPrint("⚠️ Unknown format: ${metadata.format}");
                        }
                      },

                      child: Icon(
                        _metadata!.isPremium
                            ? Icons.lock
                            : Icons.play_arrow,
                        color: smColors.projectBrowserTitle,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // 🔹 Title + Subtitle
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    project.title,
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: smColors.projectBrowserTitle,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    project.subtitle,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: smColors.projectBrowserSubtitle,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // 🔹 Elevated Card Tabs
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.grey.shade200, // ✅ light strip behind all tabs
                borderRadius: BorderRadius.circular(12),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.15),
                    blurRadius: 6,
                    offset: const Offset(0, 3),
                  ),
                ],
              ),
              child: TabBar(
                labelStyle: const TextStyle(
                  fontWeight: FontWeight.w700,
                  fontSize: 16,
                ),
                unselectedLabelStyle: const TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 15,
                ),
                labelColor: smColors.projectBrowserTitle,
                unselectedLabelColor: smColors.projectBrowserSubtitle,

                indicatorSize: TabBarIndicatorSize.tab,
                indicator: BoxDecoration(
                  color: smColors.versePlayerControlColor, // ✅ gold active pill
                  borderRadius: BorderRadius.circular(12),
                ),

                // 👇 adds subtle background for inactive tabs
                overlayColor: MaterialStateProperty.all(Colors.transparent),
                tabs: const [
                  Tab(text: "Overview"),
                  Tab(text: "Details"),
                  Tab(text: "Preview"),
                ],
              ),
            ),

            // 🔹 Tab Content
            Expanded(
              child: TabBarView(
                children: [
                  _buildOverviewTab(project, _metadata!),
                  _buildDetailsTab(_metadata!),
                  _buildPreviewTab(_metadata!),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewTab(ProjectSummary project, ProjectMetadata metadata) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Text(metadata.description,
          style: const TextStyle(fontSize: 15, height: 1.4)),
    );
  }

  Widget _buildDetailsTab(ProjectMetadata metadata) {
    final smColors = activeTheme.smColors;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (metadata.categories.isNotEmpty) ...[
            const Text("Categories:",
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
            Wrap(
              spacing: 8,
              children: metadata.categories
                  .map((c) => Chip(
                label: Text(c),
                backgroundColor:
                smColors.marketplaceChipUnselectedColor,
                labelStyle: TextStyle(
                    color: smColors.marketplaceChipTextUnselectedColor),
              ))
                  .toList(),
            ),
            const SizedBox(height: 12),
          ],
          if (metadata.languages.isNotEmpty)
            Text("Languages: ${metadata.languages.join(", ")}"),
          if (metadata.contributors.isNotEmpty) ...[
            const SizedBox(height: 12),
            const Text("Contributors:",
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
            ...metadata.contributors.map(
                  (c) => Text("${c.role}: ${c.name}",
                  style: const TextStyle(fontSize: 14)),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPreviewTab(ProjectMetadata metadata) {
    final smColors = activeTheme.smColors;
    if (metadata.audioSamples.isEmpty) {
      return const Center(child: Text("No previews available"));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: metadata.audioSamples.length,
      itemBuilder: (context, index) {
        final sample = metadata.audioSamples[index];
        return Card(
          color: smColors.chapterCardBkColor,
          margin: const EdgeInsets.symmetric(vertical: 8),
          child: ListTile(
            leading: Icon(Icons.play_circle_fill,
                color: smColors.versePlayerControlColor),
            title: Text(
              sample.title,
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: smColors.chapterCardTitleColor,
              ),
            ),
            subtitle: const Text("Tap to play preview"),
          ),
        );
      },
    );
  }
}
