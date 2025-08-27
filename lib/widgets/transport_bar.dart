import 'dart:async';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';

class TransportBar extends StatefulWidget {
  final AudioPlayer player;
  final void Function(Duration target)? onScrubEnd;

  /// whether meanings are visible
  final bool showMeanings;
  final void Function(bool value)? onToggleMeanings;

  const TransportBar({
    super.key,
    required this.player,
    this.onScrubEnd,
    this.showMeanings = true,
    this.onToggleMeanings,
  });

  @override
  State<TransportBar> createState() => _TransportBarState();
}

class _TransportBarState extends State<TransportBar> {
  Duration _pos = Duration.zero;
  Duration _dur = Duration.zero;
  StreamSubscription<Duration>? _posSub;
  StreamSubscription<Duration?>? _durSub;
  bool _dragging = false;

  @override
  void initState() {
    super.initState();
    _posSub = widget.player.positionStream.listen((d) {
      if (!_dragging) setState(() => _pos = d);
    });
    _durSub = widget.player.durationStream.listen((d) {
      setState(() => _dur = d ?? Duration.zero);
    });
  }

  @override
  void dispose() {
    _posSub?.cancel();
    _durSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final total = _dur.inMilliseconds.toDouble().clamp(1.0, double.infinity);
    final value = _pos.inMilliseconds.toDouble().clamp(0.0, total);

    final colors = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 6),
      child: Column(
        children: [
          // Time labels ABOVE the slider
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(_fmt(_pos),
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: colors.onSurface)),
                Text(_fmt(_dur),
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: colors.onSurface)),
              ],
            ),
          ),

          // Slider + control buttons
          Row(
            children: [
              Expanded(
                child: Slider(
                  value: value,
                  min: 0,
                  max: total,
                  onChangeStart: (_) => _dragging = true,
                  onChanged: (v) =>
                      setState(() => _pos = Duration(milliseconds: v.toInt())),
                  onChangeEnd: (v) async {
                    _dragging = false;
                    final d = Duration(milliseconds: v.toInt());
                    if (widget.onScrubEnd != null) widget.onScrubEnd!(d);
                  },
                ),
              ),

              // Meanings toggle button
              InkWell(
                onTap: () {
                  if (widget.onToggleMeanings != null) {
                    widget.onToggleMeanings!(!widget.showMeanings);
                  }
                },
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  width: 36,
                  height: 36,
                  margin: const EdgeInsets.only(right: 8),
                  decoration: BoxDecoration(
                    color: widget.showMeanings
                        ? colors.secondary
                        : colors.surface,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: colors.secondary,
                      width: widget.showMeanings ? 0 : 2,
                    ),
                  ),
                  child: Icon(
                    Icons.menu_book,
                    size: 20,
                    color: widget.showMeanings
                        ? colors.onSecondary
                        : colors.secondary,
                  ),
                ),
              ),

              // Play / Pause button
              InkWell(
                onTap: () async {
                  if (widget.player.playing) {
                    await widget.player.pause();
                  } else {
                    await widget.player.play();
                  }
                  setState(() {});
                },
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: colors.primary,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    widget.player.playing ? Icons.pause : Icons.play_arrow,
                    size: 22,
                    color: colors.onPrimary,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _fmt(Duration d) {
    final mm = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final ss = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    return '$mm:$ss';
  }
}
