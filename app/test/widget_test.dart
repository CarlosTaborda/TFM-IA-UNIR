// Prueba básica de humo: verifica que la app arranca y muestra el AppBar.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:app/app.dart';
import 'package:app/core/env/env_config.dart';
import 'package:app/core/providers/shared_preferences_provider.dart';

void main() {
  testWidgets('VialColApp muestra el título en el AppBar', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    await EnvConfig.load();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [sharedPreferencesProvider.overrideWithValue(prefs)],
        child: const VialColApp(),
      ),
    );
    await tester.pump();

    expect(find.text('VialCol'), findsOneWidget);
  });
}
