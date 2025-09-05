import 'package:flutter/material.dart';

/// Global app settings
class UISettings {
  static bool meaningsInVerseLang = false;
  static int pauseSeconds = 0;
  static double percentageLock = 0.35;

  /// 🎚 Fade settings
  static bool enableSmoothFade = true;       // master toggle
  static Duration fadeOutDuration = const Duration(milliseconds: 200);
  static Duration fadeInDuration = const Duration(milliseconds: 300);
  static int fadeSteps = 10;                 // higher = smoother
}

/// 🎨 Minimal custom colors for special use
class SMColors {
  final Color volumeCardBkColor;
  final Color volumeCardTitleColor;
  final Color volumeCardSubtitleColor;
  final Color chapterCardBkColor;
  final Color chapterCardTitleColor;
  final Color chapterCardSubtitleColor;
  final Color chapterCardCircleColor;
  final Color chapterCardCircleTextColor;
  final Color chapterCardNextArrowColor;
  final Color projectBrowserTitle;
  final Color projectBrowserSubtitle;
  final Color versePlayerControlColor;
  final Color versePlayerInactiveTextColor;
  final Color versePlayerActiveTextColor;
  final Color versePlayerActiveColor;
  final Color versePlayerBackColor;
  final Color versePlayerControlTextColor;
  final Color versePlayerControlToggleOffColor;
  final Color marketplaceBackColor;
  final Color marketplaceAppBarTitleColor;
  final Color marketplaceCardBkColor;
  final Color marketplaceCardTitleColor;
  final Color marketplaceCardSubtitleColor;
  final Color marketplaceChipSelectedColor;
  final Color marketplaceChipUnselectedColor;
  final Color marketplaceChipTextSelectedColor;
  final Color marketplaceChipTextUnselectedColor;
  final Color versePlayerTransportBarColor;

  const SMColors({
    required this.volumeCardBkColor,
    required this.volumeCardTitleColor,
    required this.volumeCardSubtitleColor,
    required this.chapterCardBkColor,
    required this.chapterCardTitleColor,
    required this.chapterCardSubtitleColor,
    required this.chapterCardCircleColor,
    required this.chapterCardCircleTextColor,
    required this.chapterCardNextArrowColor,
    required this.projectBrowserTitle,
    required this.projectBrowserSubtitle,
    required this.versePlayerActiveColor,
    required this.versePlayerActiveTextColor,
    required this.versePlayerControlColor,
    required this.versePlayerInactiveTextColor,
    required this.versePlayerBackColor,
    required this.versePlayerControlTextColor,
    required this.versePlayerControlToggleOffColor,
    required this.marketplaceBackColor,
    required this.marketplaceAppBarTitleColor,
    required this.marketplaceCardBkColor,
    required this.marketplaceCardTitleColor,
    required this.marketplaceCardSubtitleColor,
    required this.marketplaceChipSelectedColor,
    required this.marketplaceChipUnselectedColor,
    required this.marketplaceChipTextSelectedColor,
    required this.marketplaceChipTextUnselectedColor,
    required this.versePlayerTransportBarColor
  });
}


/// 🎨 Full theme wrapper
class UITheme {
  final Color primary;
  final Color onPrimary;
  final Color secondary;
  final Color onSecondary;
  final Color surface;
  final Color onSurface;
  final Color textColor;
  final Color cardColor;

  /// 👇 optional: attach SMColors to each theme
  final SMColors smColors;

  const UITheme({
    required this.primary,
    required this.onPrimary,
    required this.secondary,
    required this.onSecondary,
    required this.surface,
    required this.onSurface,
    required this.textColor,
    required this.cardColor,
    required this.smColors,
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
        surface: surface,
        onSurface: onSurface,
      ),
      scaffoldBackgroundColor: surface,
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


/// Example: Brown-Gold Theme
const brownGoldTheme = UITheme(
  primary: Color(0xFF040C43),
  onPrimary: Color(0xFFFFF8E7),
  secondary: Color(0xFFFFFFFF),
  onSecondary: Colors.black,
  surface: Color(0xFFF8F5E4),
  onSurface: Color(0xFFC5A247),
  textColor: Color(0xFF000000),
  cardColor: Color(0xFF040C43),
  smColors: SMColors(

    //Project Browser Screen
    projectBrowserTitle : Colors.black,
    projectBrowserSubtitle : Color(0xFF040C43),

    // Volume List Screen
    volumeCardBkColor: Colors.white38,
    volumeCardTitleColor: Colors.black,
    volumeCardSubtitleColor: Color(0xFF040C43),

    // Chapter List Screen
    chapterCardBkColor: Colors.white38,
    chapterCardTitleColor: Colors.black,
    chapterCardSubtitleColor: Color(0xFF040C43),
    chapterCardCircleColor: Color(0xFF040C43),
    chapterCardCircleTextColor: Colors.white,
    chapterCardNextArrowColor: Color(0xFF040C43),

    // 🎨 Player screen palette
    versePlayerBackColor       : Color(0xFFF8F5E4), // background
    versePlayerControlColor    : Color(0xFFE6C34D), // controls bar
    versePlayerInactiveTextColor : Color(0xFF4A403A), // inactive text
    versePlayerActiveTextColor : Color(0xFFFFF8E7), // active verse text
    versePlayerActiveColor     : Color(0xFF403D58), // highlight box
    versePlayerTransportBarColor : Color(0xFFF3E9AB), // highlight box
    versePlayerControlTextColor: Color(0xFF2B2B2B),     // ✅ labels
    versePlayerControlToggleOffColor: Colors.white, //Color(0xFF8B6B3E), // ✅ meanings OFF

    // Marketplace
    marketplaceBackColor: Color(0xFFF8F5E4), // parchment cream
    marketplaceAppBarTitleColor: Color(0xFF2B2B2B), // charcoal
    marketplaceCardBkColor: Color(0xFF403D58), // dark plum/navy
    marketplaceCardTitleColor: Color(0xFFFFF8E7), // cream
    marketplaceCardSubtitleColor: Color(0xFFE6C34D), // rich gold
    marketplaceChipSelectedColor: Color(0xFFE6C34D), // gold
    marketplaceChipUnselectedColor: Color(0xFFD8D2C4), // muted cream/gray
    marketplaceChipTextSelectedColor: Colors.black,
    marketplaceChipTextUnselectedColor: Color(0xFF403D58),
  ),
);



/// 👇 Pick the active one here
const activeTheme = brownGoldTheme;

