/// Avatar aleatorio asignado al usuario, generado una única vez por
/// instalación de la app y persistido en el dispositivo.
class UserAvatar {
  const UserAvatar({required this.iconIndex, required this.colorIndex});

  final int iconIndex;
  final int colorIndex;
}
