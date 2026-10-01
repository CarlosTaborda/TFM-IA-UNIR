import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../../../../core/env/env_config.dart';
import '../models/chat_message_model.dart';
import '../../domain/entities/chat_message.dart';
import '../../domain/entities/chat_source.dart';

/// Se comunica con el backend RAG (`rag_backend`) desplegado en Azure.
abstract class ChatRemoteDataSource {
  Future<ChatMessageModel> sendMessage({
    required String chatId,
    required String question,
  });
}

class ChatRemoteDataSourceImpl implements ChatRemoteDataSource {
  ChatRemoteDataSourceImpl({http.Client? client})
    : _client = client ?? http.Client();

  final http.Client _client;

  @override
  Future<ChatMessageModel> sendMessage({
    required String chatId,
    required String question,
  }) async {
    final uri = Uri.parse('${EnvConfig.backendBaseUrl}/chat');
    final response = await _client.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'X-App-Api-Key': EnvConfig.appApiKey,
      },
      body: jsonEncode({'pregunta': question, 'chat_id': chatId}),
    );
    debugPrint('Response status: ${response}');

    if (response.statusCode != 200) {
      throw ChatRemoteException(
        'El backend respondió con el código ${response.statusCode}: '
        '${response.body}',
      );
    }

    final decoded = jsonDecode(utf8.decode(response.bodyBytes))
        as Map<String, dynamic>;
    final sources = (decoded['fuentes'] as List<dynamic>? ?? [])
        .map(
          (raw) => ChatSource(
            title: raw['title'] as String? ?? 'Desconocido',
            sourcePath: raw['source_path'] as String? ?? 'Desconocido',
            pageNumber: raw['page_number'] as int? ?? 0,
          ),
        )
        .toList();

    return ChatMessageModel(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      author: ChatAuthor.assistant,
      content: decoded['respuesta'] as String? ?? '',
      createdAt: DateTime.now(),
      sources: sources,
    );
  }
}

class ChatRemoteException implements Exception {
  ChatRemoteException(this.message);

  final String message;

  @override
  String toString() => message;
}
