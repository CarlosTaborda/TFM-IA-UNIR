import '../entities/user_avatar.dart';

abstract class ProfileRepository {
  /// Devuelve el avatar del usuario, generándolo aleatoriamente la primera
  /// vez y reutilizando el mismo en las siguientes aperturas de la app.
  Future<UserAvatar> getOrCreateAvatar();
}
