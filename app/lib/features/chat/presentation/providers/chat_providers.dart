import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/providers/shared_preferences_provider.dart';
import '../../data/datasources/chat_local_data_source.dart';
import '../../data/datasources/chat_remote_data_source.dart';
import '../../data/repositories/chat_repository_impl.dart';
import '../../domain/repositories/chat_repository.dart';
import '../../domain/usecases/get_all_chats_usecase.dart';
import '../../domain/usecases/get_or_create_today_chat_usecase.dart';
import '../../domain/usecases/send_message_usecase.dart';

final chatLocalDataSourceProvider = Provider<ChatLocalDataSource>((ref) {
  return ChatLocalDataSourceImpl(ref.watch(sharedPreferencesProvider));
});

final chatRemoteDataSourceProvider = Provider<ChatRemoteDataSource>((ref) {
  return ChatRemoteDataSourceImpl();
});

final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  return ChatRepositoryImpl(
    localDataSource: ref.watch(chatLocalDataSourceProvider),
    remoteDataSource: ref.watch(chatRemoteDataSourceProvider),
  );
});

final getAllChatsUseCaseProvider = Provider<GetAllChatsUseCase>((ref) {
  return GetAllChatsUseCase(ref.watch(chatRepositoryProvider));
});

final getOrCreateTodayChatUseCaseProvider =
    Provider<GetOrCreateTodayChatUseCase>((ref) {
      return GetOrCreateTodayChatUseCase(ref.watch(chatRepositoryProvider));
    });

final sendMessageUseCaseProvider = Provider<SendMessageUseCase>((ref) {
  return SendMessageUseCase(ref.watch(chatRepositoryProvider));
});
