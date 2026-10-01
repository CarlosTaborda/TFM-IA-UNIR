import '../entities/chat_conversation.dart';
import '../repositories/chat_repository.dart';

class GetAllChatsUseCase {
  const GetAllChatsUseCase(this._repository);

  final ChatRepository _repository;

  Future<List<ChatConversation>> call() => _repository.getAllChats();
}
