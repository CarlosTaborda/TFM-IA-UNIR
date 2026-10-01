import '../../domain/entities/chat_conversation.dart';
import 'chat_message_model.dart';

/// Modelo serializable de [ChatConversation] para persistencia local.
class ChatConversationModel extends ChatConversation {
  const ChatConversationModel({
    required super.id,
    required super.dayKey,
    required super.createdAt,
    super.messages,
  });

  factory ChatConversationModel.fromEntity(ChatConversation entity) {
    return ChatConversationModel(
      id: entity.id,
      dayKey: entity.dayKey,
      createdAt: entity.createdAt,
      messages: entity.messages,
    );
  }

  factory ChatConversationModel.fromJson(Map<String, dynamic> json) {
    return ChatConversationModel(
      id: json['id'] as String,
      dayKey: json['dayKey'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      messages: (json['messages'] as List<dynamic>? ?? [])
          .map((raw) => ChatMessageModel.fromJson(raw as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'dayKey': dayKey,
      'createdAt': createdAt.toIso8601String(),
      'messages': messages
          .map((message) => ChatMessageModel.fromEntity(message).toJson())
          .toList(),
    };
  }
}
