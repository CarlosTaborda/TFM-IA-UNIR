import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/providers/shared_preferences_provider.dart';
import '../../data/datasources/profile_local_data_source.dart';
import '../../data/repositories/profile_repository_impl.dart';
import '../../domain/entities/user_avatar.dart';
import '../../domain/repositories/profile_repository.dart';

final profileLocalDataSourceProvider = Provider<ProfileLocalDataSource>((ref) {
  return ProfileLocalDataSourceImpl(ref.watch(sharedPreferencesProvider));
});

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepositoryImpl(ref.watch(profileLocalDataSourceProvider));
});

/// Avatar aleatorio del usuario, generado una vez y persistido en el
/// dispositivo.
final userAvatarProvider = FutureProvider<UserAvatar>((ref) {
  return ref.watch(profileRepositoryProvider).getOrCreateAvatar();
});
