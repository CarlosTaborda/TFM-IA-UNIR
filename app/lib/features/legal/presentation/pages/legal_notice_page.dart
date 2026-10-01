import 'package:flutter/material.dart';

/// Aviso legal mostrado desde el menú lateral de la app.
class LegalNoticePage extends StatelessWidget {
  const LegalNoticePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Aviso legal')),
      body: const Padding(
        padding: EdgeInsets.all(20),
        child: SingleChildScrollView(
          child: Text(
            'VialCol es una aplicación informativa que ofrece orientación '
            'general sobre normativa de tránsito y transporte en Colombia '
            'mediante un asistente basado en inteligencia artificial (RAG) '
            'que consulta fuentes normativas públicas.\n\n'
            'La información suministrada tiene fines exclusivamente '
            'informativos y no constituye asesoría legal. Las respuestas '
            'pueden contener imprecisiones o quedar desactualizadas respecto '
            'a modificaciones normativas recientes. Ante cualquier duda o '
            'decisión legal, se recomienda consultar la fuente oficial '
            'citada o a un profesional del derecho.\n\n'
            'Los chats se almacenan únicamente en el dispositivo del '
            'usuario, agrupados por día, y no son compartidos con terceros '
            'distintos al backend necesario para generar la respuesta.\n\n'
            'El uso de esta aplicación implica la aceptación de los términos '
            'aquí descritos.',
            style: TextStyle(fontSize: 15, height: 1.5),
          ),
        ),
      ),
    );
  }
}
