import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../domain/entities/chat_conversation.dart';
import '../../domain/entities/chat_message.dart';
import 'chat_providers.dart';
import 'chat_state.dart';

/// Controla la conversación activa, el listado de chats (uno por día) y el
/// envío de mensajes al backend RAG.
class ChatController extends AsyncNotifier<ChatState> {
  static const _uuid = Uuid();

  @override
  Future<ChatState> build() async {
    final todayChat = await ref.read(getOrCreateTodayChatUseCaseProvider)();
    final allChats = await ref.read(getAllChatsUseCaseProvider)();
    final merged = _upsert(allChats, todayChat);
    return ChatState(allChats: merged, activeChatId: todayChat.id);
  }

  List<ChatConversation> _upsert(
    List<ChatConversation> chats,
    ChatConversation chat,
  ) {
    final updated = [...chats];
    final index = updated.indexWhere((c) => c.id == chat.id);
    if (index >= 0) {
      updated[index] = chat;
    } else {
      updated.insert(0, chat);
    }
    updated.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return updated;
  }

  /// Cambia la conversación mostrada (p.ej. al elegir un chat de un día
  /// anterior desde el menú lateral).
  void selectChat(String chatId) {
    final current = state.value;
    if (current == null) return;
    state = AsyncData(current.copyWith(activeChatId: chatId, clearError: true));
  }

  Future<void> sendMessage(String question) async {
    final trimmed = question.trim();
    if (trimmed.isEmpty) return;

    final current = state.value;
    if (current == null || !current.isActiveChatToday) return;

    final activeChat = current.activeChat;
    final userMessage = ChatMessage(
      id: _uuid.v4(),
      author: ChatAuthor.user,
      content: trimmed,
      createdAt: DateTime.now(),
    );

    final withUserMessage = activeChat.copyWith(
      messages: [...activeChat.messages, userMessage],
    );

    state = AsyncData(
      current.copyWith(
        allChats: _upsert(current.allChats, withUserMessage),
        isSending: true,
        clearError: true,
      ),
    );
    await ref.read(chatRepositoryProvider).saveConversation(withUserMessage);

    try {
      final assistantMessage = await ref
          .read(sendMessageUseCaseProvider)
          .call(chatId: activeChat.id, question: trimmed);

      final withAssistantMessage = withUserMessage.copyWith(
        messages: [...withUserMessage.messages, assistantMessage],
      );
      await ref
          .read(chatRepositoryProvider)
          .saveConversation(withAssistantMessage);

      final latest = state.value ?? current;
      state = AsyncData(
        latest.copyWith(
          allChats: _upsert(latest.allChats, withAssistantMessage),
          isSending: false,
        ),
      );
    } catch (e) {
      final latest = state.value ?? current;
      state = AsyncData(
        latest.copyWith(
          isSending: false,
          errorMessage: 'No se pudo obtener respuesta: $e',
        ),
      );
    }
  }
}

final chatControllerProvider =
    AsyncNotifierProvider<ChatController, ChatState>(ChatController.new);
