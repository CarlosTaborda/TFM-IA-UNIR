import '../entities/chat_message.dart';
import '../repositories/chat_repository.dart';

class SendMessageUseCase {
  const SendMessageUseCase(this._repository);

  final ChatRepository _repository;

  Future<ChatMessage> call({
    required String chatId,
    required String question,
  }) {
    return _repository.sendMessage(chatId: chatId, question: question);
  }
}
