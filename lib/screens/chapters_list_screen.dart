import 'package:flutter/material.dart';
import '../core/languages.dart';
import '../core/models.dart';          // ✅ for VolumeMetadata & ChapterMetadata
import '../core/project_repository.dart';
import 'player_screen.dart';

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
  late List<ChapterMetadata> _chapters;

  @override
  void initState() {
    super.initState();
    _loadVolumeMetadata();
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

  Future<void> _loadVolumeMetadata() async {
    try {
      final repo = ProjectRepository();
      final volumeMeta =
      await repo.loadVolumeMetadata(widget.projectId, widget.volume.id);
      setState(() {
        _chapters = volumeMeta.chaptersList
            .map((c) => ChapterMetadata(
          id: c.id,
          volumeId: volumeMeta.id,
          title: c.title,
          index: c.index,
          state: c.state,
          description: c.title, // fallback if no desc
          verses: c.verses,
        ))
            .toList();
      });
    } catch (e) {
      setState(() => _err = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final v = widget.volume;
    return Scaffold(
      appBar: AppBar(title: Text(v.title)),
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/bg_parchment.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: _err != null
            ? Center(child: Text('Failed to load: $_err'))
            : (_chapters.isEmpty
            ? const Center(child: CircularProgressIndicator())
            : ListView.builder(
          itemCount: _chapters.length,
          padding: const EdgeInsets.all(12),
          itemBuilder: (_, i) {
            final chapter = _chapters[i];

            return Card(
              margin: const EdgeInsets.symmetric(vertical: 8),
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.brown.shade200,
                  child: Text(
                    '${chapter.index}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                ),
                title: Text(
                  chapter.title,
                  style: TextStyle(
                    fontFamily: widget.lang == 'sa'
                        ? 'AmruthamSanskrit'
                        : widget.lang == 'ta'
                        ? 'AmruthamTamil'
                        : null,
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    color: Colors.brown.shade800,
                  ),
                ),
                subtitle: Text(
                  chapter.description,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    color: Colors.brown.shade700,
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    height: 1.3,
                  ),
                ),
                trailing: const Icon(Icons.play_arrow),
                onTap: chapter.isEnabled
                    ? () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => PlayerScreen(
                        projectId: widget.projectId,
                        volumeId: v.id,
                        chapterMeta: chapter,
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
      ),
    );
  }
}
