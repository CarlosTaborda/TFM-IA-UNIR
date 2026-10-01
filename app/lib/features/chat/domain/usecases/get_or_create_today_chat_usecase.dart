import '../entities/chat_conversation.dart';
import '../repositories/chat_repository.dart';

class GetOrCreateTodayChatUseCase {
  const GetOrCreateTodayChatUseCase(this._repository);

  final ChatRepository _repository;

  Future<ChatConversation> call() => _repository.getOrCreateTodayChat();
}
