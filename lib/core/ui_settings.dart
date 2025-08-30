// lib/core/ui_settings.dart
import 'package:flutter/material.dart';

class UISettings {
  static bool meaningsInVerseLang = false;
  static int pauseSeconds = 0;
  static double percentageLock = 0.35;
}

class UITheme {
  final Color primary;
  final Color onPrimary;
  final Color secondary;
  final Color onSecondary;
  final Color surface;      // replaces background
  final Color onSurface;
  final Color textColor;
  final Color cardColor;

  const UITheme({
    required this.primary,
    required this.onPrimary,
    required this.secondary,
    required this.onSecondary,
    required this.surface,
    required this.onSurface,
    required this.textColor,
    required this.cardColor,
  });

  ThemeData toThemeData() {
    final base = ThemeData(useMaterial3: true);

    return base.copyWith(
      colorScheme: ColorScheme.fromSeed(
        seedColor: primary,
        primary: primary,
        onPrimary: onPrimary,
        secondary: secondary,
        onSecondary: onSecondary,
        surface: cardColor,
        onSurface: onSurface,
      ),
      scaffoldBackgroundColor: surface, // ✅ use surface
      cardTheme: CardThemeData(
        color: cardColor,
        elevation: 6,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: primary,
        foregroundColor: onPrimary,
        centerTitle: true,
        titleTextStyle: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: onPrimary,
        ),
      ),
      textTheme: base.textTheme.apply(
        bodyColor: textColor,
        displayColor: textColor,
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: primary,
        foregroundColor: onPrimary,
      ),
    );
  }
}

/// 🎨 Example themes
const brownGoldTheme = UITheme(
  primary: Color(0xFF040C43),   // deep brown
  onPrimary: Color(0xFFFFF8E7), // cream
  secondary: Color(0xFFC79A3B), // gold
  onSecondary: Colors.black,
  surface: Color(0xFFC8A851),   // soft cream (used for scaffold + bg)
  onSurface: Color(0xFFC5A247), // dark brown text
  textColor: Color(0xFF000000),
  cardColor: Color(0xFF040C43),  // cream cards
);

const maroonCreamTheme = UITheme(
  primary: Color(0xFF7B1E22), // maroon
  onPrimary: Color(0xFFFFF8E7),
  secondary: Color(0xFFC79A3B),
  onSecondary: Colors.black,
  surface: Color(0xFFFFFBF2),
  onSurface: Color(0xFF311B0B),
  textColor: Color(0xFF311B0B),
  cardColor: Color(0xFFFFF8E7),

);

/// 👇 Switch here to change the global theme
const activeTheme = brownGoldTheme;
