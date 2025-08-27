import 'package:flutter/material.dart';
import '../core/project_repository.dart';
import '../core/project_models.dart';
import 'project_browser_screen.dart';

/// Marketplace screen showing all available stotra projects
class ProjectMarketplaceScreen extends StatefulWidget {
  const ProjectMarketplaceScreen({super.key});

  @override
  State<ProjectMarketplaceScreen> createState() => _ProjectMarketplaceScreenState();
}

class _ProjectMarketplaceScreenState extends State<ProjectMarketplaceScreen> {
  late Future<List<ProjectSummary>> _projectsFuture;

  @override
  void initState() {
    super.initState();
    _projectsFuture = ProjectRepository().loadProjects(); // loads stotras.json
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Stotra Manjari Marketplace")),
      body: FutureBuilder<List<ProjectSummary>>(
        future: _projectsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("❌ Failed to load projects: ${snapshot.error}"));
          }
          final projects = snapshot.data ?? [];
          if (projects.isEmpty) {
            return const Center(child: Text("No projects available"));
          }

          return ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: projects.length,
            itemBuilder: (context, i) {
              final project = projects[i];
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 3,
                child: ListTile(
                  leading: ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      project.thumbnail,
                      fit: BoxFit.cover,
                      width: 60,
                      height: 60,
                      errorBuilder: (context, _, __) =>
                      const Icon(Icons.book, size: 40, color: Colors.brown),
                    ),
                  ),
                  title: Text(
                    project.title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  subtitle: Text(
                    project.subtitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  trailing: project.isPremium
                      ? const Icon(Icons.lock, color: Colors.red)
                      : const Icon(Icons.lock_open, color: Colors.green),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ProjectBrowserScreen(project: project),
                      ),
                    );
                  },
                ),
              );
            },
          );
        },
      ),
    );
  }
}
