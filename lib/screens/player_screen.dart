import 'dart:async';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:audio_session/audio_session.dart';
import 'package:scrollable_positioned_list/scrollable_positioned_list.dart';
import 'package:auto_size_text/auto_size_text.dart';

import '../core/models.dart';
import '../core/languages.dart';
import '../widgets/transport_bar.dart';
import '../services/ai_service.dart';
import '../core/app_settings.dart';
import '../core/url_builder.dart'; // 🔹 for build*Url helpers

// === Text styles per language ===
TextStyle verseStyle(String lang, {bool isActive = false}) {
  final cfg = configFor(lang);
  return TextStyle(
    fontFamily: cfg.fontFamily.isNotEmpty ? cfg.fontFamily : null,
    fontSize: isActive ? cfg.highlightSize : cfg.baseSize,
    fontWeight: isActive ? cfg.highlightWeight : cfg.baseWeight,
    height: 1.4,
    shadows: (lang == 'sa' && isActive)
        ? [
      Shadow(
        offset: const Offset(0.4, 0.4),
        blurRadius: 0.6,
        color: Colors.black.withValues(alpha: 0.25),
      ),
    ]
        : null,
  );
}

int maxWrapLines(String lang, {bool isActive = false}) {
  final cfg = configFor(lang);
  if (cfg.wrapAlways) return 2;
  return isActive ? 2 : 1;
}

class PlayerScreen extends StatefulWidget {
  final String projectId;
  final int volumeIndex;
  final int chapterIndex;
  final String title;
  final String language;

  const PlayerScreen({
    super.key,
    required this.projectId,
    required this.volumeIndex,
    required this.chapterIndex,
    required this.title,
    required this.language,
  });

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> {
  final _player = AudioPlayer();
  final ItemScrollController _itemScrollCtrl = ItemScrollController();
  final ItemPositionsListener _itemPositions = ItemPositionsListener.create();

  bool _showMeanings = false;
  Chapter? _chapter;
  String? _loadError;
  int _currentIndex = 0;

  double _speed = 1.0;
  bool _autoScroll = true;
  bool _isPlaying = false;
  bool _suppressAuto = false;

  StreamSubscription<Duration>? _posSub;
  StreamSubscription<PlayerState>? _stateSub;
  late String _language;

  @override
  void initState() {
    super.initState();
    _language = widget.language;
    _init();
  }

  String renderVerseText(String raw, String lang, bool isActive) {
    final cfg = configFor(lang);
    if (isActive) {
      return cfg.flattenHighlight
          ? raw.replaceAll('{b}{t}', '')
          : raw.replaceAll('{b}{t}', '\n');
    } else {
      return cfg.flattenNoHighlight
          ? raw.replaceAll('{b}{t}', '')
          : raw.replaceAll('{b}{t}', '\n');
    }
  }

  int _indexAtTime(List<VerseLine> lines, int ms) {
    int lo = 0, hi = lines.length - 1, ans = 0;
    while (lo <= hi) {
      final mid = (lo + hi) >> 1;
      final L = lines[mid];
      if (ms < L.startMs) {
        hi = mid - 1;
      } else if (ms >= L.endMs) {
        lo = mid + 1;
        ans = lo.clamp(0, lines.length - 1);
      } else {
        return mid;
      }
    }
    return ans;
  }

  Future<void> _init() async {
    try {
      final session = await AudioSession.instance;
      await session.configure(const AudioSessionConfiguration.music());
      await session.setActive(true);

      final volumeId = "volume${widget.volumeIndex.toString().padLeft(2, '0')}";
      final chapterId = "chapter${widget.chapterIndex.toString().padLeft(2, '0')}";

      // 🔹 Build URLs with projectId
      final textUrl = buildVersesUrl(
        projectId: widget.projectId,
        volumeId: volumeId,
        chapterId: chapterId,
        lang: _language,
      );
      final meaningsUrl = buildMeaningsUrl(
        projectId: widget.projectId,
        volumeId: volumeId,
        chapterId: chapterId,
        lang: _language,
      );
      final durationsUrl = buildDurationsUrl(
        projectId: widget.projectId,
        volumeId: volumeId,
        chapterId: chapterId,
      );
      final audioUrl = buildAudioUrl(
        projectId: widget.projectId,
        volumeId: volumeId,
        chapterId: chapterId,
        format: "m4a", // change to "m4a" later
      );

      // 🔹 Load Chapter
      final chapter = await Chapter.fromNetwork(
        id: '${widget.projectId}-k${widget.volumeIndex}-s${widget.chapterIndex}-$_language',
        title: widget.title,
        language: _language,
        textUrl: textUrl,
        meaningsUrl: meaningsUrl,
        durationsUrl: durationsUrl,
      );
      setState(() => _chapter = chapter);

      // 🔹 Setup audio
      await _player.setUrl(audioUrl);

      _stateSub = _player.playerStateStream.listen((s) {
        final nowPlaying = s.playing;
        if (nowPlaying != _isPlaying) {
          setState(() {
            _isPlaying = nowPlaying;
            _autoScroll = nowPlaying;
          });
        }
      });

      _posSub = _player.positionStream.listen((pos) async {
        if (_suppressAuto) return;
        final s = _chapter;
        if (s == null) return;

        final idx = _indexAtTime(s.lines, pos.inMilliseconds);
        if (idx != _currentIndex) {
          setState(() => _currentIndex = idx);

          // autoscroll
          if (_autoScroll && _itemScrollCtrl.isAttached) {
            double? alignment = idx < 3 ? null : 0.35;
            if (alignment != null) {
              _itemScrollCtrl.scrollTo(
                index: idx,
                alignment: alignment,
                duration: const Duration(milliseconds: 250),
                curve: Curves.easeOutCubic,
              );
            }
          }

          final line = s.lines[idx];
          final currentMeaningLang =
          AppSettings.meaningsInVerseLang ? _language : "en";

          if (!line.meanings.containsKey(currentMeaningLang)) {
            final fetched =
            await fetchMeaningFromAI(line.text, currentMeaningLang);
            if (fetched != null) {
              setState(() {
                line.meanings[currentMeaningLang] = fetched;
              });
            }
          }

          if (AppSettings.pauseSeconds > 0) {
            final remaining = line.endMs - pos.inMilliseconds;
            if (remaining > 0) {
              Future.delayed(Duration(milliseconds: remaining), () async {
                if (_currentIndex == idx && _player.playing) {
                  await _player.pause();
                  Future.delayed(
                      Duration(seconds: AppSettings.pauseSeconds), () async {
                    if (!_player.playing) {
                      await _player.play();
                    }
                  });
                }
              });
            }
          }
        }
      });
    } catch (e, st) {
      debugPrint('Init error: $e\n$st');
      setState(() => _loadError = e.toString());
    }
  }

  Future<void> _jumpTo(Duration target) async {
    _suppressAuto = true;
    final lines = _chapter!.lines;
    final idx = _indexAtTime(lines, target.inMilliseconds);
    setState(() => _currentIndex = idx);

    if (_itemScrollCtrl.isAttached) {
      final positions = _itemPositions.itemPositions.value;
      final isVisible = positions.any((pos) => pos.index == idx);

      if (!isVisible) {
        double alignment = (idx >= 4) ? 0.35 : 0.0;
        _itemScrollCtrl.scrollTo(
          index: idx,
          alignment: alignment,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOutCubic,
        );
      }
    }

    await _player.seek(target);
    Future.delayed(const Duration(milliseconds: 250), () {
      _suppressAuto = false;
    });
  }

  @override
  void dispose() {
    _stateSub?.cancel();
    _posSub?.cancel();
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loadError != null) {
      return Scaffold(
        appBar: AppBar(title: Text(widget.title)),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Text('Failed to load sarga:\n$_loadError'),
          ),
        ),
      );
    }

    final sarga = _chapter;
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          // 🌐 Language toggle
          PopupMenuButton<String>(
            initialValue: _language,
            onSelected: (newLang) async {
              if (newLang != _language) {
                final currentPos = await _player.position;
                try {
                  final newChapter = await Chapter.fromNetwork(
                    id: '${widget.projectId}-k${widget.volumeIndex}-s${widget.chapterIndex}-$newLang',
                    title: widget.title,
                    language: newLang,
                    textUrl: buildVersesUrl(
                      projectId: widget.projectId,
                      volumeId: "volume${widget.volumeIndex.toString().padLeft(2, '0')}",
                      chapterId: "chapter${widget.chapterIndex.toString().padLeft(2, '0')}",
                      lang: newLang,
                    ),
                    meaningsUrl: buildMeaningsUrl(
                      projectId: widget.projectId,
                      volumeId: "volume${widget.volumeIndex.toString().padLeft(2, '0')}",
                      chapterId: "chapter${widget.chapterIndex.toString().padLeft(2, '0')}",
                      lang: newLang,
                    ),
                    durationsUrl: buildDurationsUrl(
                      projectId: widget.projectId,
                      volumeId: "volume${widget.volumeIndex.toString().padLeft(2, '0')}",
                      chapterId: "chapter${widget.chapterIndex.toString().padLeft(2, '0')}",
                    ),
                  );
                  setState(() {
                    _language = newLang;
                    _chapter = newChapter;
                    _currentIndex = _indexAtTime(
                        newChapter.lines, currentPos.inMilliseconds);
                  });
                } catch (e) {
                  debugPrint('⚠️ Failed to load new language $newLang: $e');
                }
              }
            },
            itemBuilder: (ctx) => supportedLangs
                .map((l) => PopupMenuItem(
              value: l.code,
              child: Text(l.label),
            ))
                .toList(),
            child: Row(
              children: [
                const Icon(Icons.language, color: Colors.white),
                const SizedBox(width: 6),
                Text(_language.toUpperCase()),
                const Icon(Icons.arrow_drop_down, color: Colors.white),
              ],
            ),
          ),
          // 🎵 Speed control
          PopupMenuButton<double>(
            initialValue: _speed,
            onSelected: (v) async {
              setState(() => _speed = v);
              await _player.setSpeed(v);
            },
            itemBuilder: (ctx) => const [
              PopupMenuItem(value: 0.75, child: Text('0.75x')),
              PopupMenuItem(value: 1.0, child: Text('1.0x')),
              PopupMenuItem(value: 1.25, child: Text('1.25x')),
              PopupMenuItem(value: 1.5, child: Text('1.5x')),
            ],
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12.0),
              child: Center(child: Text('${_speed.toStringAsFixed(2)}x')),
            ),
          ),
        ],
      ),
      body: sarga == null
          ? const Center(child: CircularProgressIndicator())
          : Column(
        children: [
          Container(
            color: Colors.amber.shade300.withValues(alpha: 0.95),
            child: TransportBar(
              player: _player,
              onScrubEnd: (target) => _jumpTo(target),
              showMeanings: _showMeanings,
              onToggleMeanings: (val) =>
                  setState(() => _showMeanings = val),
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: ScrollablePositionedList.builder(
              itemScrollController: _itemScrollCtrl,
              itemPositionsListener: _itemPositions,
              itemCount: sarga.lines.length,
              physics: _isPlaying
                  ? const NeverScrollableScrollPhysics()
                  : const AlwaysScrollableScrollPhysics(),
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).size.height * 0.45,
              ),
              itemBuilder: (ctx, i) {
                final line = sarga.lines[i];
                final isActive = i == _currentIndex;

                final currentMeaningLang =
                AppSettings.meaningsInVerseLang ? _language : "en";
                final meaning = line.meanings[currentMeaningLang];
                final displayText =
                renderVerseText(line.text, _language, isActive);

                return InkWell(
                  onTap: () async {
                    await _jumpTo(Duration(milliseconds: line.startMs));
                    if (!_player.playing) await _player.play();
                  },
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: isActive
                          ? Theme.of(context)
                          .colorScheme
                          .secondaryContainer
                          : null,
                      border: Border(
                        left: BorderSide(
                          width: 4,
                          color: isActive
                              ? Theme.of(context).colorScheme.secondary
                              : Colors.transparent,
                        ),
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        AutoSizeText(
                          displayText,
                          textAlign: TextAlign.center,
                          maxLines: maxWrapLines(_language,
                              isActive: isActive),
                          overflow: TextOverflow.ellipsis,
                          style:
                          verseStyle(_language, isActive: isActive),
                          minFontSize: 12,
                          stepGranularity: 1,
                        ),
                        if (_showMeanings &&
                            isActive &&
                            meaning != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 8.0),
                            child: Text(
                              meaning,
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                fontFamily: 'Roboto',
                                fontSize: 18,
                                fontWeight: FontWeight.w600,
                                height: 1.4,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
