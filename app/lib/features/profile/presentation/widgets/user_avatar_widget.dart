import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/avatar_palette.dart';
import '../providers/profile_providers.dart';

/// Icono aleatorio que representa al usuario en la parte superior del chat.
class UserAvatarWidget extends ConsumerWidget {
  const UserAvatarWidget({super.key, this.radius = 18});

  final double radius;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final avatarAsync = ref.watch(userAvatarProvider);
    return avatarAsync.when(
      data: (avatar) => CircleAvatar(
        radius: radius,
        backgroundColor: AvatarPalette.colors[avatar.colorIndex],
        child: Icon(
          AvatarPalette.icons[avatar.iconIndex],
          color: Colors.white,
          size: radius,
        ),
      ),
      loading: () => CircleAvatar(
        radius: radius,
        backgroundColor: Colors.grey.shade300,
      ),
      error: (_, _) => CircleAvatar(
        radius: radius,
        backgroundColor: Colors.grey.shade300,
        child: Icon(Icons.person, size: radius, color: Colors.white),
      ),
    );
  }
}
