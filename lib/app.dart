import 'package:flutter/material.dart';
import 'screens/project_marketplace.dart';

class StotraManjariApp extends StatelessWidget {
  const StotraManjariApp({super.key});

  @override
  Widget build(BuildContext context) {
    final base = ThemeData(useMaterial3: true);

    return MaterialApp(
      title: 'Stotra Manjari',
      theme: base.copyWith(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF7B1E22), // deep maroon
          primary: const Color(0xFF7B1E22),
          onPrimary: const Color(0xFFFFF8E7), // cream text
          secondary: const Color(0xFFC79A3B), // golden
          onSecondary: Colors.black,
          background: const Color(0xFFFAF5E6), // soft cream
          surface: const Color(0xFFFDFCF7),
          error: const Color(0xFFB3261E),
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.brown.shade700,//Color(0xFF7B1E22),
          foregroundColor: Color(0xFFFFF8E7),
          centerTitle: true,
          titleTextStyle: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: Color(0xFFFFF8E7),
          ),
        ),
        floatingActionButtonTheme: const FloatingActionButtonThemeData(
          backgroundColor: Color(0xFF7B1E22),
          foregroundColor: Color(0xFFFFF8E7),
          shape: StadiumBorder(),
        ),
        dividerColor: const Color(0xFFC79A3B),
        scaffoldBackgroundColor: const Color(0xFFFAF5E6),
        textTheme: base.textTheme.apply(
          bodyColor: const Color(0xFF3E2723), // dark brown text
          displayColor: const Color(0xFF3E2723),
        ),
      ),
      home: const ProjectMarketplaceScreen(),
    );
  }
}
