/// Utilidades para trabajar con la clave de agrupación diaria de los chats.
class DateKey {
  DateKey._();

  /// Devuelve una clave estable `yyyy-MM-dd` para agrupar un chat por día.
  static String fromDate(DateTime date) {
    final normalized = DateTime(date.year, date.month, date.day);
    final y = normalized.year.toString().padLeft(4, '0');
    final m = normalized.month.toString().padLeft(2, '0');
    final d = normalized.day.toString().padLeft(2, '0');
    return '$y-$m-$d';
  }

  static String today() => fromDate(DateTime.now());
}
