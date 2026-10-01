import '../entities/chat_conversation.dart';
import '../entities/chat_message.dart';

/// Contrato de acceso a los datos de chat (almacenamiento local + backend RAG).
abstract class ChatRepository {
  /// Devuelve todas las conversaciones almacenadas en el dispositivo,
  /// ordenadas de la más reciente a la más antigua.
  Future<List<ChatConversation>> getAllChats();

  /// Obtiene la conversación del día actual, creándola si no existe.
  Future<ChatConversation> getOrCreateTodayChat();

  /// Envía una pregunta al backend RAG dentro de una conversación concreta
  /// y devuelve el mensaje de respuesta del asistente.
  Future<ChatMessage> sendMessage({
    required String chatId,
    required String question,
  });

  /// Persiste el estado actual de una conversación en el dispositivo.
  Future<void> saveConversation(ChatConversation conversation);
}
