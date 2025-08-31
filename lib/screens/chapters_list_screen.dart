import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:stotra_manjari/core/ui_settings.dart';
import '../core/languages.dart';
import '../core/models.dart';
import 'player_screen.dart';
import '../core/ui_settings.dart';

class ChaptersListScreen extends StatefulWidget {
  final String projectId;
  final VolumeMetadata volume;
  final String lang;

  const ChaptersListScreen({
    super.key,
    required this.projectId,
    required this.volume,
    required this.lang,
  });

  @override
  State<ChaptersListScreen> createState() => _ChaptersListScreenState();
}

class _ChaptersListScreenState extends State<ChaptersListScreen> {
  String? _err;
  late List<ChapterSummary> _chapters;
  Map<String, Map<String, dynamic>> _chapterDetails = {};

  @override
  void initState() {
    super.initState();
    _chapters = widget.volume.chaptersList;
    _loadChapterMetadata();
    currentLang.addListener(_onLangChanged);
  }

  @override
  void dispose() {
    currentLang.removeListener(_onLangChanged);
    super.dispose();
  }

  void _onLangChanged() {
    if (currentLang.value != widget.lang) {
      Navigator.of(context).pop();
    }
  }

  Future<void> _loadChapterMetadata() async {
    final details = <String, Map<String, dynamic>>{};
    for (final c in _chapters) {
      try {
        final path =
            "assets/projects/${widget.projectId}/${widget.volume.id}/${c.id}/metadata.json";
        final raw = await rootBundle.loadString(path);
        details[c.id] = jsonDecode(raw);
      } catch (_) {
        // fallback: leave entry empty
      }
    }
    setState(() => _chapterDetails = details);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);         // 👈 here
    final smColors = activeTheme.smColors;
    final v = widget.volume;

    return Scaffold(
      backgroundColor: smColors.versePlayerBackColor, // ✅ same bg as volume list
      appBar: AppBar(
        title: Text(
          v.title,
          style: TextStyle(
            color: smColors.projectBrowserTitle,
            fontWeight: FontWeight.w700,
            fontSize: 20,
          ),
        ),
        backgroundColor: smColors.versePlayerControlColor, // ✅ same top bar as volume list
        centerTitle: true,
        elevation: 2,
      ),
      body: _err != null
          ? Center(child: Text('Failed to load: $_err'))
          : (_chapters.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
        itemCount: _chapters.length,
        padding: const EdgeInsets.all(12),
        itemBuilder: (_, i) {
          final chapter = _chapters[i];
          final meta = _chapterDetails[chapter.id];

          final title = meta?["title"] ?? chapter.title;
          final desc = meta?["description"] ?? chapter.title;

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
                  color: smColors.marketplaceCardBkColor, // ✅ same as project card background
                  shape: BoxShape.circle,
                ),
                alignment: Alignment.center,
                child: Text(
                  '${chapter.index}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: smColors.marketplaceCardTitleColor, // ✅ gold text like project card
                  ),
                ),
              ),
              title: Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 18,
                  color: smColors.volumeCardTitleColor,
                ),
              ),
              subtitle: Text(
                desc,
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
                final cm = ChapterMetadata(
                  id: chapter.id,
                  volumeId: v.id,
                  title: title,
                  index: chapter.index,
                  state: chapter.state,
                  description: desc,
                  verses: chapter.verses,
                );
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => PlayerScreen(
                      projectId: widget.projectId,
                      volumeId: v.id,
                      chapterMeta: cm,
                      language: widget.lang,
                    ),
                  ),
                );
              }
                  : null,
            ),
          );

        },
      )),
    );
  }
}
