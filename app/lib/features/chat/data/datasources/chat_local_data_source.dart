import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/chat_conversation_model.dart';

/// Persiste el listado de chats (uno por día) en el dispositivo mediante
/// `shared_preferences`.
abstract class ChatLocalDataSource {
  Future<List<ChatConversationModel>> getAllChats();
  Future<void> saveChat(ChatConversationModel conversation);
}

class ChatLocalDataSourceImpl implements ChatLocalDataSource {
  ChatLocalDataSourceImpl(this._prefs);

  final SharedPreferences _prefs;

  static const _storageKey = 'vialcol_chats_v1';

  @override
  Future<List<ChatConversationModel>> getAllChats() async {
    final raw = _prefs.getString(_storageKey);
    if (raw == null || raw.isEmpty) return [];
    final decoded = jsonDecode(raw) as List<dynamic>;
    return decoded
        .map(
          (item) =>
              ChatConversationModel.fromJson(item as Map<String, dynamic>),
        )
        .toList();
  }

  @override
  Future<void> saveChat(ChatConversationModel conversation) async {
    final chats = await getAllChats();
    final index = chats.indexWhere((c) => c.id == conversation.id);
    if (index >= 0) {
      chats[index] = conversation;
    } else {
      chats.add(conversation);
    }
    final encoded = jsonEncode(
      chats.map((c) => c.toJson()).toList(growable: false),
    );
    await _prefs.setString(_storageKey, encoded);
  }
}
