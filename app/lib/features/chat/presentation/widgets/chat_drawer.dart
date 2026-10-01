import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../legal/presentation/pages/legal_notice_page.dart';
import '../providers/chat_controller.dart';

class ChatDrawer extends ConsumerWidget {
  const ChatDrawer({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chatState = ref.watch(chatControllerProvider).value;
    final dateFormat = DateFormat('EEEE d MMMM y', 'es_CO');

    return Drawer(
      child: SafeArea(
        child: Column(
          children: [
            const DrawerHeader(
              child: Align(
                alignment: Alignment.bottomLeft,
                child: Text(
                  'VialCol',
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Historial de chats',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
              ),
            ),
            Expanded(
              child: chatState == null
                  ? const Center(child: CircularProgressIndicator())
                  : ListView.builder(
                      itemCount: chatState.allChats.length,
                      itemBuilder: (context, index) {
                        final chat = chatState.allChats[index];
                        final isActive = chat.id == chatState.activeChatId;
                        String label;
                        try {
                          label = dateFormat.format(chat.createdAt);
                        } catch (_) {
                          label = chat.dayKey;
                        }
                        return ListTile(
                          leading: const Icon(Icons.chat_bubble_outline),
                          title: Text(label),
                          selected: isActive,
                          onTap: () {
                            ref
                                .read(chatControllerProvider.notifier)
                                .selectChat(chat.id);
                            Navigator.of(context).pop();
                          },
                        );
                      },
                    ),
            ),
            const Divider(height: 1),
            ListTile(
              leading: const Icon(Icons.gavel_outlined),
              title: const Text('Aviso legal'),
              onTap: () {
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const LegalNoticePage()),
                );
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }
}
