import 'package:uuid/uuid.dart';

import '../../../../core/utils/date_key.dart';
import '../../domain/entities/chat_conversation.dart';
import '../../domain/entities/chat_message.dart';
import '../../domain/repositories/chat_repository.dart';
import '../datasources/chat_local_data_source.dart';
import '../datasources/chat_remote_data_source.dart';
import '../models/chat_conversation_model.dart';

class ChatRepositoryImpl implements ChatRepository {
  ChatRepositoryImpl({
    required ChatLocalDataSource localDataSource,
    required ChatRemoteDataSource remoteDataSource,
    Uuid? uuid,
  }) : _localDataSource = localDataSource,
       _remoteDataSource = remoteDataSource,
       _uuid = uuid ?? const Uuid();

  final ChatLocalDataSource _localDataSource;
  final ChatRemoteDataSource _remoteDataSource;
  final Uuid _uuid;

  @override
  Future<List<ChatConversation>> getAllChats() async {
    final chats = await _localDataSource.getAllChats();
    chats.sort((a, b) => b.createdAt.compareTo(a.createdAt));
    return chats;
  }

  @override
  Future<ChatConversation> getOrCreateTodayChat() async {
    final todayKey = DateKey.today();
    final chats = await _localDataSource.getAllChats();
    for (final chat in chats) {
      if (chat.dayKey == todayKey) return chat;
    }

    final newChat = ChatConversationModel(
      id: _uuid.v4(),
      dayKey: todayKey,
      createdAt: DateTime.now(),
      messages: const [],
    );
    await _localDataSource.saveChat(newChat);
    return newChat;
  }

  @override
  Future<ChatMessage> sendMessage({
    required String chatId,
    required String question,
  }) {
    return _remoteDataSource.sendMessage(chatId: chatId, question: question);
  }

  @override
  Future<void> saveConversation(ChatConversation conversation) {
    return _localDataSource.saveChat(
      ChatConversationModel.fromEntity(conversation),
    );
  }
}
