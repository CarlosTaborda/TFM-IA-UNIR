/// Referencia normativa (artículo, ley o decreto) que respalda una respuesta.
class ChatSource {
  const ChatSource({
    required this.title,
    required this.sourcePath,
    required this.pageNumber,
  });

  final String title;
  final String sourcePath;
  final int pageNumber;
}
