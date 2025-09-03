// lib/screens/chapters_list_screen.dart
import 'package:flutter/material.dart';
import '../core/models.dart';
import '../core/ui_settings.dart';
import 'player_screen.dart';

class ChaptersListScreen extends StatelessWidget {
  final String projectId;
  final VolumeSummary volume;
  final String lang;

  const ChaptersListScreen({
    super.key,
    required this.projectId,
    required this.volume,
    required this.lang,
  });

  @override
  Widget build(BuildContext context) {
    final smColors = activeTheme.smColors;
    final chapters = volume.chaptersList;

    return Scaffold(
      backgroundColor: smColors.versePlayerBackColor,
      appBar: AppBar(
        title: Text(
          volume.title,
          style: TextStyle(
            color: smColors.projectBrowserTitle,
            fontWeight: FontWeight.w700,
            fontSize: 20,
          ),
        ),
        backgroundColor: smColors.versePlayerControlColor,
        centerTitle: true,
        elevation: 2,
      ),
      body: chapters.isEmpty
          ? const Center(child: Text("No chapters available"))
          : ListView.builder(
        itemCount: chapters.length,
        padding: const EdgeInsets.all(12),
        itemBuilder: (_, i) {
          final chapter = chapters[i];

          // ✅ Use subtitle if present, otherwise fall back gracefully
          String subtitle = chapter.subtitle.isNotEmpty
              ? chapter.subtitle
              : "";

          if (chapter.state == 1) subtitle += " (coming soon)";
          else if (chapter.state == 0) subtitle = "hidden";

          return Card(
            elevation: 10,
            margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
            color: Colors.white,
            shadowColor: Colors.black.withOpacity(0.35),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
              side: BorderSide(
                color: smColors.volumeCardSubtitleColor.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              leading: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: smColors.marketplaceCardBkColor,
                  shape: BoxShape.circle,
                ),
                alignment: Alignment.center,
                child: Text(
                  '${chapter.index}',   // ✅ pulled directly from JSON
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: smColors.marketplaceCardTitleColor,
                  ),
                ),
              ),
              title: Text(
                chapter.title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 18,
                  color: smColors.volumeCardTitleColor,
                ),
              ),
              subtitle: Text(
                subtitle,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  fontSize: 14,
                  color: smColors.volumeCardSubtitleColor,
                ),
              ),
              trailing: Icon(
                chapter.state == 2 ? Icons.play_arrow : Icons.lock,
                color: chapter.state == 2
                    ? smColors.chapterCardNextArrowColor
                    : Colors.grey,
                size: 24,
              ),
              onTap: chapter.state == 2
                  ? () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PlayerScreen(
                      projectId: projectId,
                      volumeId: volume.id,
                      chapterMeta: chapter,   // ✅ pass ChapterSummary
                      language: lang,
                    ),
                  ),
                );
              }
                  : null,
            ),
          );
        },
      ),
    );
  }
}
