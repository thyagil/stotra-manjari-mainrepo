// lib/core/app_settings.dart

/// Global app settings (for now just simple constants/variables).
/// Later we can hook this into SharedPreferences for persistence.

class AppSettings {
  /// If true → fetch meanings in the verse’s language
  /// If false → always fetch in English
  static bool meaningsInVerseLang = false;

  /// Number of seconds to auto-pause after a verse meaning.
  /// 0 = no pause.
  static int pauseSeconds = 0;

  /// percentage of the screen below which the highlight box locks
  static double percentageLock = 0.35;
}
