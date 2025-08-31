// lib/screens/project_marketplace.dart
import 'package:auto_size_text/auto_size_text.dart';
import 'package:flutter/material.dart';
import '../core/project_repository.dart';
import '../core/models.dart';
import '../screens/project_browser_screen.dart';
import '../core/ui_settings.dart'; // 👈 for activeTheme.smColors

class ProjectMarketplaceScreen extends StatefulWidget {
  const ProjectMarketplaceScreen({super.key});

  @override
  State<ProjectMarketplaceScreen> createState() => _ProjectMarketplaceScreenState();
}

class _ProjectMarketplaceScreenState extends State<ProjectMarketplaceScreen> {
  late Future<List<ProjectSummary>> _projectsFuture;
  String selectedCategory = "All";

  final List<String> categories = [
    "All",
    "Audio-books",
    "E-books",
    "Music Albums",
  ];

  @override
  void initState() {
    super.initState();
    _projectsFuture = ProjectRepository().loadProjects();
  }

  @override
  Widget build(BuildContext context) {
    final smColors = activeTheme.smColors;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          "Stotra Manjari", // ✅ Title case
          style: TextStyle(
            color: smColors.versePlayerControlTextColor,
            fontWeight: FontWeight.w700,
            fontSize: 20,
          ),
        ),
        centerTitle: true,
        backgroundColor: smColors.versePlayerControlColor,
        elevation: 4,

      ),
      body: FutureBuilder<List<ProjectSummary>>(
        future: _projectsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Text(
                "❌ Failed to load projects: ${snapshot.error}",
                style: TextStyle(color: smColors.marketplaceCardTitleColor),
              ),
            );
          }

          final projects = snapshot.data ?? [];
          if (projects.isEmpty) {
            return Center(
              child: Text(
                "No projects available",
                style: TextStyle(color: smColors.marketplaceCardTitleColor),
              ),
            );
          }

          final featured = projects.where((p) => p.featured).toList();
          final filteredProjects = selectedCategory == "All"
              ? projects
              : projects; // TODO: filter when categories are wired

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 🔹 Featured Carousel
                SizedBox(
                  height: 260,
                  child: PageView.builder(
                    controller: PageController(viewportFraction: 0.95),
                    itemCount: featured.length,
                    itemBuilder: (context, index) {
                      final project = featured[index];
                      return _buildFeaturedCard(context, project, index);
                    },
                  ),
                ),

                const SizedBox(height: 12),

                // 🔹 Category Chips
                SizedBox(
                  height: 40,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: categories.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 6),
                    itemBuilder: (context, index) {
                      final cat = categories[index];
                      final isSelected = cat == selectedCategory;

                      return ChoiceChip(
                        label: Text(
                          cat,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: isSelected
                                ? smColors.marketplaceChipTextSelectedColor
                                : smColors.marketplaceChipTextUnselectedColor,
                          ),
                        ),
                        selected: isSelected,
                        onSelected: (_) {
                          setState(() => selectedCategory = cat);
                        },
                        selectedColor: smColors.marketplaceChipSelectedColor,
                        backgroundColor: smColors.marketplaceChipUnselectedColor,
                        checkmarkColor: smColors.marketplaceChipTextSelectedColor,
                        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                        shape: StadiumBorder(
                          side: BorderSide(
                            color: isSelected
                                ? smColors.marketplaceChipSelectedColor
                                : smColors.marketplaceChipUnselectedColor,
                            width: 1,
                          ),
                        ),
                      );
                    },
                  ),
                ),

                const SizedBox(height: 12),

                // 🔹 Projects Grid
                Padding(
                  padding: const EdgeInsets.fromLTRB(12, 0, 12, 12), // ✅ no top padding
                  child: GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: filteredProjects.length,
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 6,
                      crossAxisSpacing: 6,
                      mainAxisExtent: 320,
                    ),
                    itemBuilder: (context, index) {
                      final project = filteredProjects[index];
                      return _buildProjectCard(context, project);
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildFeaturedCard(BuildContext context, ProjectSummary project, int index) {
    final imageUrl = project.banner.isNotEmpty ? project.banner : project.thumbnail;

    return GestureDetector(
      onTap: () => _openProject(project),
      child: Hero(
        tag: "project-${project.id}",
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
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
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: AspectRatio(
              aspectRatio: 16 / 9, // ✅ lock to banner ratio (1920x1080)
              child: Image.network(
                imageUrl,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => const Icon(
                  Icons.broken_image,
                  size: 80,
                  color: Colors.grey,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }



  Widget _buildProjectCard(BuildContext context, ProjectSummary project) {
    final smColors = activeTheme.smColors;

    return GestureDetector(
      onTap: () => _openProject(project),
      child: Hero(
        tag: "project-${project.id}-grid",
        child: Card(
          elevation: 8,
          shadowColor: Colors.black.withOpacity(0.25), // ✅ softer shadow
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          clipBehavior: Clip.antiAlias,
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  smColors.marketplaceCardBkColor,
                  smColors.marketplaceCardBkColor.withOpacity(0.92), // subtle depth
                ],
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // 🔹 Thumbnail
                Stack(
                  children: [
                    AspectRatio(
                      aspectRatio: 3 / 4,
                      child: Image.network(
                        project.thumbnail,
                        fit: BoxFit.cover,
                        width: double.infinity,
                        errorBuilder: (_, __, ___) => Icon(
                          Icons.book,
                          size: 60,
                          color: smColors.marketplaceCardSubtitleColor,
                        ),
                      ),
                    ),
                    Positioned(
                      bottom: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: const BoxDecoration(
                          color: Colors.black54,
                          shape: BoxShape.circle,
                        ),
                        child: Icon(
                          project.isPremium ? Icons.lock : Icons.lock_open,
                          color: project.isPremium ? Colors.red : Colors.green,
                          size: 18,
                        ),
                      ),
                    ),
                  ],
                ),

                // 🔹 Title
                Padding(
                  padding: const EdgeInsets.only(top: 6, left: 8, right: 8),
                  child: Text(
                    project.title,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                      color: smColors.marketplaceCardTitleColor,
                    ),
                  ),
                ),

                // 🔹 Subtitle
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  child: Text(
                    project.subtitle,
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                      color: smColors.marketplaceCardSubtitleColor,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }


  void _openProject(ProjectSummary project) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => ProjectBrowserScreen(project: project)),
    );
  }
}
