import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../profile/presentation/widgets/user_avatar_widget.dart';
import '../providers/chat_controller.dart';
import '../widgets/chat_drawer.dart';
import '../widgets/message_bubble.dart';
import '../widgets/message_input.dart';

class ChatPage extends ConsumerStatefulWidget {
  const ChatPage({super.key});

  @override
  ConsumerState<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends ConsumerState<ChatPage> {
  final _scrollController = ScrollController();

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chatAsync = ref.watch(chatControllerProvider);

    ref.listen(chatControllerProvider, (previous, next) {
      final message = next.value?.errorMessage;
      if (message != null && message != previous?.value?.errorMessage) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text(message)));
      }
      if ((next.value?.activeChat.messages.length ?? 0) >
          (previous?.value?.activeChat.messages.length ?? 0)) {
        _scrollToBottom();
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('VialCol'),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: UserAvatarWidget(),
          ),
        ],
      ),
      drawer: const ChatDrawer(),
      body: chatAsync.when(
        data: (state) {
          final messages = state.activeChat.messages;
          return Column(
            children: [
              if (!state.isActiveChatToday)
                Container(
                  width: double.infinity,
                  color: Theme.of(context).colorScheme.secondaryContainer,
                  padding: const EdgeInsets.all(8),
                  child: Text(
                    'Estás viendo un chat anterior. Solo puedes enviar '
                    'mensajes nuevos en el chat de hoy.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Theme.of(
                        context,
                      ).colorScheme.onSecondaryContainer,
                    ),
                  ),
                ),
              Expanded(
                child: messages.isEmpty
                    ? const Center(
                        child: Padding(
                          padding: EdgeInsets.all(24),
                          child: Text(
                            'Pregunta lo que necesites sobre normativa de '
                            'tránsito y transporte en Colombia.',
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        itemCount: messages.length,
                        itemBuilder: (context, index) =>
                            MessageBubble(message: messages[index]),
                      ),
              ),
              MessageInput(
                enabled: state.isActiveChatToday,
                isSending: state.isSending,
                onSend: (text) => ref
                    .read(chatControllerProvider.notifier)
                    .sendMessage(text),
              ),
            ],
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stackTrace) =>
            Center(child: Text('Ocurrió un error: $error')),
      ),
    );
  }
}
