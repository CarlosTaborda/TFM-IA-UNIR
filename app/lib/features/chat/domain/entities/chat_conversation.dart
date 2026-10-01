import 'chat_message.dart';

/// Conversación de chat asociada a un único día. La app mantiene un chat
/// por día, identificado por [id] (único) y agrupado por [dayKey].
class ChatConversation {
  const ChatConversation({
    required this.id,
    required this.dayKey,
    required this.createdAt,
    this.messages = const [],
  });

  final String id;
  final String dayKey;
  final DateTime createdAt;
  final List<ChatMessage> messages;

  bool get isEmpty => messages.isEmpty;

  ChatConversation copyWith({List<ChatMessage>? messages}) {
    return ChatConversation(
      id: id,
      dayKey: dayKey,
      createdAt: createdAt,
      messages: messages ?? this.messages,
    );
  }
}
