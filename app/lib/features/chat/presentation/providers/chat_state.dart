import '../../domain/entities/chat_conversation.dart';

/// Estado de la pantalla de chat: listado completo (para el menú lateral),
/// conversación activa y estado de envío.
class ChatState {
  const ChatState({
    required this.allChats,
    required this.activeChatId,
    this.isSending = false,
    this.errorMessage,
  });

  final List<ChatConversation> allChats;
  final String activeChatId;
  final bool isSending;
  final String? errorMessage;

  ChatConversation get activeChat =>
      allChats.firstWhere((chat) => chat.id == activeChatId);

  String get todayDayKey {
    final now = DateTime.now();
    return '${now.year.toString().padLeft(4, '0')}-'
        '${now.month.toString().padLeft(2, '0')}-'
        '${now.day.toString().padLeft(2, '0')}';
  }

  bool get isActiveChatToday => activeChat.dayKey == todayDayKey;

  ChatState copyWith({
    List<ChatConversation>? allChats,
    String? activeChatId,
    bool? isSending,
    String? errorMessage,
    bool clearError = false,
  }) {
    return ChatState(
      allChats: allChats ?? this.allChats,
      activeChatId: activeChatId ?? this.activeChatId,
      isSending: isSending ?? this.isSending,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

