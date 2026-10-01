import 'chat_source.dart';

enum ChatAuthor { user, assistant }

/// Un único mensaje dentro de una conversación de chat.
class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.author,
    required this.content,
    required this.createdAt,
    this.sources = const [],
  });

  final String id;
  final ChatAuthor author;
  final String content;
  final DateTime createdAt;
  final List<ChatSource> sources;

  ChatMessage copyWith({String? content, List<ChatSource>? sources}) {
    return ChatMessage(
      id: id,
      author: author,
      content: content ?? this.content,
      createdAt: createdAt,
      sources: sources ?? this.sources,
    );
  }
}
