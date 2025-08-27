// lib/core/languages.dart
import 'package:flutter/material.dart';

class Lang {
  final String code;
  final String label;
  const Lang(this.code, this.label);
}

const supportedLangs = <Lang>[
  Lang('sa', 'Sanskrit'),
  Lang('be', 'Bengali'),
  Lang('en', 'English'),
  Lang('gu', 'Gujarati'),
  Lang('ta', 'Tamil'),
  Lang('te', 'Telugu'),
  Lang('ka', 'Kannada'),
  Lang('ma', 'Malayalam'),
];

// ✅ Global language notifier (used across app)
final ValueNotifier<String> currentLang = ValueNotifier<String>('sa');

// 🔹 Per-language configuration
class LangConfig {
  final String fontFamily;
  final double baseSize;
  final double highlightSize;
  final FontWeight baseWeight;
  final FontWeight highlightWeight;
  final bool wrapAlways;
  final bool flattenNoHighlight;
  final bool flattenHighlight;

  const LangConfig({
    required this.fontFamily,
    required this.baseSize,
    required this.highlightSize,
    required this.baseWeight,
    required this.highlightWeight,
    this.wrapAlways = false,
    required this.flattenNoHighlight,
    required this.flattenHighlight,

  });
}

const langConfigs = {
  'sa': LangConfig(
    fontFamily: 'AmruthamSanskrit',
    baseSize: 22,
    highlightSize: 40,
    baseWeight: FontWeight.w500,
    highlightWeight: FontWeight.w700,
    wrapAlways: false,
    flattenNoHighlight: true,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'te': LangConfig(
    fontFamily: '',
    baseSize: 22,
    highlightSize: 40,
    baseWeight: FontWeight.w500,
    highlightWeight: FontWeight.w700,
    wrapAlways: false,
    flattenNoHighlight: true,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'gu': LangConfig(
    fontFamily: '',
    baseSize: 22,
    highlightSize: 40,
    baseWeight: FontWeight.w500,
    highlightWeight: FontWeight.w700,
    wrapAlways: false,
    flattenNoHighlight: true,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'ka': LangConfig(
    fontFamily: '',
    baseSize: 22,
    highlightSize: 40,
    baseWeight: FontWeight.w500,
    highlightWeight: FontWeight.w700,
    wrapAlways: false,
    flattenNoHighlight: true,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'en': LangConfig(
    fontFamily: '',
    baseSize: 22,
    highlightSize: 40,
    baseWeight: FontWeight.w500,
    highlightWeight: FontWeight.w700,
    wrapAlways: true,
    flattenNoHighlight: false,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'ta': LangConfig(
    fontFamily: 'NotoSerifTamil',
    baseSize: 20,
    highlightSize: 32,
    baseWeight: FontWeight.w400,
    highlightWeight: FontWeight.w600,
    wrapAlways: true,
    flattenNoHighlight: false,   // 👈 expand {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'be': LangConfig(
    fontFamily: 'NotoSansBengali',
    baseSize: 20,
    highlightSize: 34,
    baseWeight: FontWeight.w400,
    highlightWeight: FontWeight.w600,
    wrapAlways: false,
    flattenNoHighlight: true,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'ma': LangConfig(
    fontFamily: '',
    baseSize: 20,
    highlightSize: 34,
    baseWeight: FontWeight.w400,
    highlightWeight: FontWeight.w600,
    wrapAlways: true,
    flattenNoHighlight: false,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
  'default': LangConfig(
    fontFamily: '',
    baseSize: 20,
    highlightSize: 34,
    baseWeight: FontWeight.w400,
    highlightWeight: FontWeight.w600,
    wrapAlways: false,
    flattenNoHighlight: true,   // 👈 collapse {b}{t} when not highlighted
    flattenHighlight: false,    // 👈 but expand {b}{t} into newlines when highlighted
  ),
};

LangConfig configFor(String code) =>
    langConfigs[code] ?? langConfigs['default']!;
