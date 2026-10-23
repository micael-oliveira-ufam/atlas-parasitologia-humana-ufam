import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import 'protocols_page.dart';
import 'specimen_page.dart';

/// Busca por espécie/doença/estágio e por protocolo (sem distinção de acentos).
class AtlasSearch extends SearchDelegate<void> {
  AtlasSearch(this.data) : super(searchFieldLabel: 'Buscar espécie, doença ou protocolo');

  final AtlasData data;

  @override
  List<Widget>? buildActions(BuildContext context) => [
        if (query.isNotEmpty) IconButton(icon: const Icon(Icons.clear), tooltip: 'Limpar', onPressed: () => query = ''),
      ];

  @override
  Widget? buildLeading(BuildContext context) =>
      IconButton(icon: const Icon(Icons.arrow_back), tooltip: 'Voltar', onPressed: () => close(context, null));

  @override
  Widget buildResults(BuildContext context) => _list(context);

  @override
  Widget buildSuggestions(BuildContext context) => _list(context);

  Widget _list(BuildContext context) {
    if (query.trim().isEmpty) {
      return const Center(child: Padding(padding: EdgeInsets.all(24), child: Text('Digite o nome de uma espécie, doença ou protocolo.')));
    }
    final sps = searchSpecimens(data, query);
    final prs = searchProtocols(data, query);
    if (sps.isEmpty && prs.isEmpty) {
      return const Center(child: Text('Nenhum resultado.'));
    }
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (sps.isNotEmpty) ...[
          const Text('Espécies', style: TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          for (final s in sps) SpecimenTile(specimen: s),
        ],
        if (prs.isNotEmpty) ...[
          const SizedBox(height: 8),
          const Text('Protocolos', style: TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          for (final p in prs) ProtocolTile(data: data, protocol: p),
        ],
      ],
    );
  }
}
