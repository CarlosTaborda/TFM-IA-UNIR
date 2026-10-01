import '../../domain/entities/user_avatar.dart';
import '../../domain/repositories/profile_repository.dart';
import '../datasources/profile_local_data_source.dart';

class ProfileRepositoryImpl implements ProfileRepository {
  ProfileRepositoryImpl(this._localDataSource);

  final ProfileLocalDataSource _localDataSource;

  @override
  Future<UserAvatar> getOrCreateAvatar() => _localDataSource.getOrCreateAvatar();
}
