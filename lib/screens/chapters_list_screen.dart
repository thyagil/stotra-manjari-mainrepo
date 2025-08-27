import 'package:flutter/material.dart';
import '../core/languages.dart';
import '../core/project_models.dart';   // now uses new VolumeInfo with chapterCount
import '../core/volumes_data.dart';     // for loadChapterDescriptions()
import 'player_screen.dart';

class ChaptersListScreen extends StatefulWidget {
  final String projectId;
  final VolumeInfo volume;
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
  List<String> _descs = [];
  String? _err;

  @override
  void initState() {
    super.initState();
    _init();
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

  Future<void> _init() async {
    try {
      _descs = await loadChapterDescriptions(
        projectId: widget.projectId,
        volumeIndex: widget.volume.index,
      );
      setState(() {});
    } catch (e) {
      setState(() => _err = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    final v = widget.volume;
    return Scaffold(
      appBar: AppBar(title: Text(v.name)),
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/bg_parchment.png'),
            fit: BoxFit.cover,
          ),
        ),
        child: _err != null
            ? Center(child: Text('Failed to load: $_err'))
            : ListView.builder(
          itemCount: v.chapterCount,  // ✅ use chapterCount
          padding: const EdgeInsets.all(12),
          itemBuilder: (_, i) {
            final chapterNum = i + 1;
            final title = 'Chapter $chapterNum';
            final desc = (chapterNum - 1 < _descs.length)
                ? _descs[chapterNum - 1]
                : '—';

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
                    '$chapterNum',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.black,
                    ),
                  ),
                ),
                title: Text(
                  title,
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
                  desc,
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
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => PlayerScreen(
                        projectId: widget.projectId,
                        volumeIndex: v.index,
                        chapterIndex: chapterNum,
                        title: 'Chapter $chapterNum',
                        language: widget.lang,
                      ),
                    ),
                  );
                },
              ),
            );
          },
        ),
      ),
    );
  }
}
