import 'dart:math';

import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/constants/avatar_palette.dart';
import '../../domain/entities/user_avatar.dart';

abstract class ProfileLocalDataSource {
  Future<UserAvatar> getOrCreateAvatar();
}

class ProfileLocalDataSourceImpl implements ProfileLocalDataSource {
  ProfileLocalDataSourceImpl(this._prefs);

  final SharedPreferences _prefs;

  static const _iconIndexKey = 'vialcol_avatar_icon_index';
  static const _colorIndexKey = 'vialcol_avatar_color_index';

  @override
  Future<UserAvatar> getOrCreateAvatar() async {
    final storedIcon = _prefs.getInt(_iconIndexKey);
    final storedColor = _prefs.getInt(_colorIndexKey);
    if (storedIcon != null && storedColor != null) {
      return UserAvatar(iconIndex: storedIcon, colorIndex: storedColor);
    }

    final random = Random();
    final iconIndex = random.nextInt(AvatarPalette.icons.length);
    final colorIndex = random.nextInt(AvatarPalette.colors.length);
    await _prefs.setInt(_iconIndexKey, iconIndex);
    await _prefs.setInt(_colorIndexKey, colorIndex);
    return UserAvatar(iconIndex: iconIndex, colorIndex: colorIndex);
  }
}
