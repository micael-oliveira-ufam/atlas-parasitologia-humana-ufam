import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import 'theme.dart';
import 'widgets.dart';

/// Aba "Artefatos": estruturas que podem ser confundidas com parasitos.
class ArtifactsTab extends StatelessWidget {
  const ArtifactsTab({super.key, required this.data});

  final AtlasData data;

  @override
  Widget build(BuildContext context) {
    final g = data.artifacts;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Artefatos e pseudoparasitos', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        if (g.tip.isNotEmpty) Notice(g.tip, tone: Tone.ok, title: 'Dica'),
        if (g.items.isEmpty) const Notice('Nenhum item disponível.', tone: Tone.neutral),
        for (final a in g.items)
          Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(14),
            decoration: softBox(context, radius: 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: kAmber),
                    const SizedBox(width: 8),
                    Expanded(child: Text(a.name, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16))),
                  ],
                ),
                const SizedBox(height: 6),
                if (a.confusedWith.isNotEmpty) LabeledText('Confundida com', a.confusedWith),
                if (a.howToTell.isNotEmpty) LabeledText('Como diferenciar', a.howToTell),
                if (a.status.isNotEmpty) Pill(a.status == 'ressalva' ? 'Com ressalva' : a.status, tone: toneForClaim(a.status)),
                if (a.refs.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Text('Fontes: ${a.refs.map(refShort).join('; ')}', style: Theme.of(context).textTheme.bodySmall),
                  ),
                if (a.evidence.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text('Evidência: ${a.evidence}', style: Theme.of(context).textTheme.bodySmall),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}
