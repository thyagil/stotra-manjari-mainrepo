// lib/screens/project_marketplace.dart
import 'package:auto_size_text/auto_size_text.dart';
import 'package:flutter/material.dart';
import '../core/project_repository.dart';
import '../core/models.dart';
import '../screens/project_browser_screen.dart';

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
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          "STOTRA MANJARI",
          style: theme.appBarTheme.titleTextStyle,
        ),
        centerTitle: true,
        backgroundColor: theme.appBarTheme.backgroundColor,
        elevation: 3,
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
                style: theme.textTheme.bodyLarge,
              ),
            );
          }

          final projects = snapshot.data ?? [];
          if (projects.isEmpty) {
            return Center(
              child: Text(
                "No projects available",
                style: theme.textTheme.bodyLarge,
              ),
            );
          }

          final featured = projects.where((p) => p.featured).toList();
          debugPrint("📸 Featured projects: ${featured.map((f) => f.id).toList()}");

          final filteredProjects = selectedCategory == "All"
              ? projects
              : projects; // TODO: filter when categories are wired

          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 🔹 Featured Carousel
                SizedBox(
                  height: 220,
                  child: PageView.builder(
                    controller: PageController(viewportFraction: 0.85),
                    itemCount: featured.length,
                    itemBuilder: (context, index) {
                      final project = featured[index];
                      return _buildFeaturedCard(context, project, index);
                    },
                  ),
                ),

                //Space between the Featured Carousel and Category Chips (buttons)
                const SizedBox(height: 4),

                // 🔹 Category Chips
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Row(
                    children: categories.map((cat) {
                      final isSelected = cat == selectedCategory;
                      return AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        curve: Curves.easeInOut,
                        margin: const EdgeInsets.symmetric(horizontal: 4),
                        child: ChoiceChip(
                          label: Text(cat),
                          selected: isSelected,
                          onSelected: (_) {
                            setState(() => selectedCategory = cat);
                          },
                          selectedColor: theme.colorScheme.secondary,
                          backgroundColor: theme.chipTheme.backgroundColor,
                          labelStyle: TextStyle(
                            color: isSelected
                                ? theme.colorScheme.onSecondary
                                : theme.textTheme.bodyLarge?.color,
                          ),
                          shape: StadiumBorder(
                            side: BorderSide(
                              color: Color(0xFF040C43), //theme.colorScheme.secondary,
                              width: 2,
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),

                // Space between the Category Chips and the Project Grid
                const SizedBox(height: 0),

                // 🔹 Projects Grid
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: filteredProjects.length,
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 4, // 🔹 vertical spacing between rows
                      crossAxisSpacing: 4, // 🔹 horizontal spacing between cards
                      //childAspectRatio: 0.55, // was 0.8 now taller
                      mainAxisExtent: 320, // 👈 explicit height in px
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
    final theme = Theme.of(context);
    final hasBanner = project.banner.isNotEmpty;
    final imageUrl = hasBanner ? project.banner : project.thumbnail;

    // Special case: Ramayanam title formatting
    final displayTitle =
    project.id == "ramayanam_sriramghanapatigal" ? "Śrīmad Rāmāyaṇam" : project.title;

    return GestureDetector(
      onTap: () => _openProject(project),
      child: Hero(
        tag: "project-${project.id}",
        child: Container(
          height: hasBanner ? 260 : 200, // ✅ adaptive height
          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(hasBanner ? 12 : 20), // ✅ softer for banners
            image: DecorationImage(
              image: NetworkImage(imageUrl),
              fit: BoxFit.cover,
            ),
          ),
          child: hasBanner
              ? Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  Colors.black.withValues(alpha: 0.6),
                  Colors.transparent,
                ],
              ),
            ),
            padding: const EdgeInsets.all(16),
            alignment: Alignment.bottomLeft,
            child: Text(
              displayTitle,
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.onPrimary,
                fontSize: 20,
                fontWeight: FontWeight.bold,
                shadows: const [Shadow(blurRadius: 6, color: Colors.black)],
              ),
            ),
          )
              : Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  Colors.black.withValues(alpha: 0.6),
                  Colors.transparent,
                ],
              ),
            ),
            padding: const EdgeInsets.all(16),
            alignment: Alignment.bottomLeft,
            child: Text(
              "$displayTitle\n${project.subtitle}",
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.onPrimary,
                fontWeight: FontWeight.bold,
                shadows: const [Shadow(blurRadius: 4, color: Colors.black)],
              ),
            ),
          ),
        ),
      ),
    );
  }



  Widget _buildProjectCard(BuildContext context, ProjectSummary project) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: () => _openProject(project),
      child: Hero(
        tag: "project-${project.id}-grid",
        child: Card(
          elevation: 6,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          clipBehavior: Clip.antiAlias,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 🔹 Image with lock overlay
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
                        color: theme.colorScheme.secondary,
                      ),
                    ),
                  ),

                  // 🔹 Lock icon overlay (bottom-right of image)
                  Positioned(
                    bottom: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: const BoxDecoration(
                        color: Colors.black54, // keeps the circular background for contrast
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        project.isPremium ? Icons.lock : Icons.lock_open,
                        color: project.isPremium ? Colors.red : Colors.green, // 🔴/🟢
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
                  style: theme.textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: theme.colorScheme.onSurface,
                  ),
                ),
              ),

              // 🔹 Subtitle (BOLD + tighter spacing)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                child: Text(
                  project.subtitle,
                  textAlign: TextAlign.center,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                    color: Colors.white //theme.colorScheme.onSurface.withOpacity(0.85),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }


  void _openProject(ProjectSummary project) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ProjectBrowserScreen(project: project),
      ),
    );
  }
}
