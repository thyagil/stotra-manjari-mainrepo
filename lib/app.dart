// lib/app.dart
import 'package:flutter/material.dart';
import 'screens/project_marketplace.dart';
import 'core/ui_settings.dart';  // 👈 where your UITheme + themes live

class StotraManjariApp extends StatelessWidget {
  const StotraManjariApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stotra Manjari',
      theme: activeTheme.toThemeData(), // 👈 Use the active UI theme globally
      home: const ProjectMarketplaceScreen(),
    );
  }
}
