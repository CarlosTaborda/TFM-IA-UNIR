import 'package:flutter/material.dart';

import '../../domain/entities/chat_message.dart';

class MessageBubble extends StatelessWidget {
  const MessageBubble({super.key, required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final isUser = message.author == ChatAuthor.user;
    final colorScheme = Theme.of(context).colorScheme;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        decoration: BoxDecoration(
          color: isUser
              ? colorScheme.primary
              : colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.content,
              style: TextStyle(
                color: isUser ? colorScheme.onPrimary : colorScheme.onSurface,
              ),
            ),
            if (message.sources.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                'Fuentes:',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                  color: isUser ? colorScheme.onPrimary : colorScheme.onSurface,
                ),
              ),
              for (final source in message.sources)
                Text(
                  '• ${source.title} (pág. ${source.pageNumber})',
                  style: TextStyle(
                    fontSize: 12,
                    color: isUser
                        ? colorScheme.onPrimary
                        : colorScheme.onSurface,
                  ),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
