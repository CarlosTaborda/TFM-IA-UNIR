import '../../domain/entities/chat_message.dart';
import '../../domain/entities/chat_source.dart';

/// Modelo serializable de [ChatMessage] para persistencia local.
class ChatMessageModel extends ChatMessage {
  const ChatMessageModel({
    required super.id,
    required super.author,
    required super.content,
    required super.createdAt,
    super.sources,
  });

  factory ChatMessageModel.fromEntity(ChatMessage entity) {
    return ChatMessageModel(
      id: entity.id,
      author: entity.author,
      content: entity.content,
      createdAt: entity.createdAt,
      sources: entity.sources,
    );
  }

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) {
    return ChatMessageModel(
      id: json['id'] as String,
      author: (json['author'] as String) == 'user'
          ? ChatAuthor.user
          : ChatAuthor.assistant,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      sources: (json['sources'] as List<dynamic>? ?? [])
          .map(
            (raw) => ChatSource(
              title: raw['title'] as String? ?? 'Desconocido',
              sourcePath: raw['sourcePath'] as String? ?? 'Desconocido',
              pageNumber: raw['pageNumber'] as int? ?? 0,
            ),
          )
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'author': author == ChatAuthor.user ? 'user' : 'assistant',
      'content': content,
      'createdAt': createdAt.toIso8601String(),
      'sources': sources
          .map(
            (source) => {
              'title': source.title,
              'sourcePath': source.sourcePath,
              'pageNumber': source.pageNumber,
            },
          )
          .toList(),
    };
  }
}
