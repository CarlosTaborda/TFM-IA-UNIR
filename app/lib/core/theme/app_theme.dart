import 'package:flutter/material.dart';

/// Tema visual centralizado de la app VialCol.
class AppTheme {
  AppTheme._();

  static ThemeData light() {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0B5FA5)),
      appBarTheme: const AppBarTheme(centerTitle: false),
    );
  }
}
