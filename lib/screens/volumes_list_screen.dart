import 'package:flutter/material.dart';
import '../core/languages.dart';
import '../core/models.dart';        // unified models.dart
import '../core/project_repository.dart';
import 'chapters_list_screen.dart';

class VolumesListScreen extends StatelessWidget {
  final String projectId;
  final ProjectMetadata metadata;
  final String lang;

  const VolumesListScreen({
    super.key,
    required this.projectId,
    required this.metadata,
    required this.lang,
  });

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<String>(
      valueListenable: currentLang,
      builder: (_, currentLangValue, __) {
        return Container(
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/bg_parchment.png'),
              fit: BoxFit.cover,
            ),
          ),
          child: ListView.builder(
            itemCount: metadata.volumes.length,
            padding: const EdgeInsets.all(12),
            itemBuilder: (_, i) {
              final v = metadata.volumes[i]; // VolumeSummary

              String subtitle = '${v.chapters} chapters';
              if (v.state == 1) {
                subtitle += " (coming soon)";
              } else if (v.state == 0) {
                subtitle = "hidden";
              }

              return Card(
                margin: const EdgeInsets.symmetric(vertical: 8),
                elevation: 6,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ListTile(
                  title: Text(
                    v.name,
                    style: TextStyle(
                      fontFamily: '',
                      fontSize: 22,
                      fontWeight: FontWeight.w600,
                      color: Colors.brown.shade800,
                      shadows: [
                        Shadow(
                          offset: const Offset(1, 1),
                          blurRadius: 2,
                          color: Colors.black.withOpacity(0.2),
                        ),
                      ],
                    ),
                  ),
                  subtitle: Text(
                    subtitle,
                    style: TextStyle(
                      color: Colors.brown.shade600,
                      fontSize: 16,
                    ),
                  ),
                  trailing: v.state == 2
                      ? const Icon(Icons.chevron_right)
                      : const Icon(Icons.lock, color: Colors.grey),
                  onTap: v.state == 2
                      ? () async {
                    final repo = ProjectRepository();

                    try {
                      final volumeMeta = await repo.loadVolumeMetadata(
                        projectId,
                        v.id, // e.g. "volume01"
                      );

                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ChaptersListScreen(
                            projectId: projectId,
                            volume: volumeMeta,
                            lang: lang,
                          ),
                        ),
                      );
                    } catch (e) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("❌ Failed to load volume: $e")),
                      );
                    }
                  }
                      : null,
                ),
              );
            },
          ),
        );
      },
    );
  }
}
