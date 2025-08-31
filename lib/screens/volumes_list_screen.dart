// lib/screens/volumes_list_screen.dart
import 'package:flutter/material.dart';
import '../core/languages.dart';
import '../core/models.dart';
import '../core/project_repository.dart';
import '../core/ui_settings.dart';
import 'chapters_list_screen.dart';

class VolumesListScreen extends StatelessWidget {
  final String projectId;
  final ProjectMetadata metadata;
  final String lang;
  final bool standalone;

  const VolumesListScreen({
    super.key,
    required this.projectId,
    required this.metadata,
    required this.lang,
    this.standalone = true,
  });

  @override
  Widget build(BuildContext context) {
    final smColors = activeTheme.smColors;

    final content = ListView.builder(
      itemCount: metadata.volumes.length,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemBuilder: (_, i) {
        final v = metadata.volumes[i];

        String subtitle = '${v.chapters} chapters';
        if (v.state == 1) subtitle += " (coming soon)";
        else if (v.state == 0) subtitle = "hidden";

        return Card(
          elevation: 10,
          margin: const EdgeInsets.symmetric(vertical: 10, horizontal: 2),
          color: Colors.white, // 👈 makes it pop against cream background
          shadowColor: Colors.black.withOpacity(0.35),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
            side: BorderSide(
              color: smColors.volumeCardSubtitleColor.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            leading: v.cover.isNotEmpty
                ? SizedBox(
              width: 56,
              height: 56,
              child: ClipOval(
                child: Image.network(
                  v.cover,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    color: Colors.grey.shade300,
                    child: const Icon(Icons.book, color: Colors.black54),
                  ),
                ),
              ),
            )
                : const CircleAvatar(
              radius: 35, // 70/2
              backgroundColor: Colors.grey,
              child: Icon(Icons.book, color: Colors.black54),
            ),


            title: Text(
              v.title,
              style: TextStyle(
                fontWeight: FontWeight.w800,
                fontSize: 18,
                color: smColors.volumeCardTitleColor,
              ),
            ),
            subtitle: Text(
              subtitle,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: 14,
                color: smColors.volumeCardSubtitleColor,
              ),
            ),
            trailing: v.state == 2
                ? Icon(Icons.chevron_right,
                color: smColors.chapterCardNextArrowColor, size: 24)
                : const Icon(Icons.lock, color: Colors.grey),
            onTap: v.state == 2
                ? () async {
              final repo = ProjectRepository();
              try {
                final volumeMeta = await repo.loadVolumeMetadata(
                  projectId,
                  v.id,
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
    );

    return standalone
        ? Scaffold(
      appBar: AppBar(
        backgroundColor: smColors.versePlayerControlColor, // gold
        elevation: 2,
        centerTitle: true,
        iconTheme: const IconThemeData(color: Colors.black), // ✅ back button/icons
        titleTextStyle: const TextStyle( // ✅ enforce black title
          color: Colors.black,
          fontWeight: FontWeight.w700,
          fontSize: 20,
        ),
        title: const Text("Volumes"),
      ),
      body: content,
    )
        : content;

  }
}
