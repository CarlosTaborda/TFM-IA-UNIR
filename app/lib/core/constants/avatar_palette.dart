import 'package:flutter/material.dart';

/// Paleta fija de íconos y colores usados para generar el avatar aleatorio
/// del usuario. Se referencian como constantes para evitar problemas con el
/// tree-shaking de íconos de Flutter.
class AvatarPalette {
  AvatarPalette._();

  static const List<IconData> icons = [
    Icons.directions_car_filled,
    Icons.motorcycle,
    Icons.pedal_bike,
    Icons.directions_bus_filled,
    Icons.local_taxi,
    Icons.traffic,
    Icons.emoji_people,
    Icons.face,
  ];

  static const List<Color> colors = [
    Color(0xFF0B5FA5),
    Color(0xFF2E7D32),
    Color(0xFFB8860B),
    Color(0xFF6A1B9A),
    Color(0xFFC62828),
    Color(0xFF00838F),
    Color(0xFFEF6C00),
    Color(0xFF283593),
  ];
}
