import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Debe sobreescribirse en `main.dart` con la instancia real obtenida de
/// `SharedPreferences.getInstance()` antes de ejecutar la app.
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError(
    'sharedPreferencesProvider debe sobreescribirse en main.dart',
  );
});
