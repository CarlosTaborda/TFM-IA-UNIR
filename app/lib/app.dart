import 'package:flutter/material.dart';

import 'core/theme/app_theme.dart';
import 'features/chat/presentation/pages/chat_page.dart';

class VialColApp extends StatelessWidget {
  const VialColApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'VialCol',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      home: const ChatPage(),
    );
  }
}
