import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import '../data/models.dart';
import 'theme.dart';
import 'widgets.dart';

void openProtocol(BuildContext context, AtlasData data, Protocol p) {
  Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ProtocolPage(data: data, protocol: p)));
}

class ProtocolTile extends StatelessWidget {
  const ProtocolTile({super.key, required this.data, required this.protocol});

  final AtlasData data;
  final Protocol protocol;

  @override
  Widget build(BuildContext context) {
    final p = protocol;
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(p.title, style: const TextStyle(fontWeight: FontWeight.w700)),
        subtitle: Text(p.popularName.isNotEmpty ? p.popularName : p.indication, maxLines: 2, overflow: TextOverflow.ellipsis),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => openProtocol(context, data, p),
      ),
    );
  }
}

/// Aba "Protocolos".
class ProtocolsTab extends StatelessWidget {
  const ProtocolsTab({super.key, required this.data});

  final AtlasData data;

  @override
  Widget build(BuildContext context) {
    final r = data.review;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: ExpansionTile(
            leading: const Icon(Icons.fact_check_outlined),
            title: const Text('Sobre a revisão da literatura'),
            subtitle: r.reviewedOn.isEmpty ? null : Text('Revisão de ${r.reviewedOnBr}'),
            childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            expandedCrossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (r.scope.isNotEmpty) Text(r.scope),
              if (r.notValidation.isNotEmpty) ...[
                const SizedBox(height: 8),
                Notice(r.notValidation, title: 'O que "validado" não significa'),
              ],
              if (r.notReviewed.isNotEmpty) ...[
                const Text('Não revisado:', style: TextStyle(fontWeight: FontWeight.w700)),
                BulletList(r.notReviewed),
              ],
              if (r.sourceAccessNote.isNotEmpty) Text(r.sourceAccessNote, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
        const SizedBox(height: 8),
        for (final p in data.protocols) ProtocolTile(data: data, protocol: p),
      ],
    );
  }
}

class ProtocolPage extends StatelessWidget {
  const ProtocolPage({super.key, required this.data, required this.protocol});

  final AtlasData data;
  final Protocol protocol;

  String _refName(String id) => data.ref(id)?.short ?? id;

  @override
  Widget build(BuildContext context) {
    final p = protocol;
    final inten = p.intensity;
    return Scaffold(
      appBar: AppBar(title: Text(p.title)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
        children: [
          if (p.popularName.isNotEmpty) Text(p.popularName, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Notice(
            'Texto didático baseado nas fontes listadas abaixo. Não é um procedimento operacional padrão: '
            'siga o POP e as normas de biossegurança do seu laboratório.',
            title: 'Aviso',
          ),
          if (p.indication.isNotEmpty) Section(title: 'Indicação', child: Text(p.indication)),
          if (p.principle.isNotEmpty) Section(title: 'Princípio', child: Text(p.principle)),
          if (p.materials.isNotEmpty) Section(title: 'Reagentes e materiais', child: BulletList(p.materials)),
          if (p.steps.isNotEmpty) Section(title: 'Passo a passo', child: BulletList(p.steps, numbered: true)),
          if (p.advantages.isNotEmpty) Section(title: 'Vantagens', child: BulletList(p.advantages)),
          if (p.limitations.isNotEmpty) Section(title: 'Limitações', child: BulletList(p.limitations)),
          if (p.parasites.isNotEmpty)
            Section(title: 'Parasitos detectados', child: PillWrap(pills: [for (final x in p.parasites) Pill(x)])),
          if (inten != null && inten.header.isNotEmpty) Section(title: 'Tabela de intensidade', child: _intensity(context, inten)),
          if (p.evidence.isNotEmpty)
            Section(
              title: 'Evidências',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final e in p.evidence)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(e.text),
                          if (e.refs.isNotEmpty)
                            Text('Fontes: ${e.refs.map(_refName).join('; ')}', style: Theme.of(context).textTheme.bodySmall),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          if (p.verification.isNotEmpty) Section(title: 'Verificação item a item', child: _verification(context)),
          if (p.refs.isNotEmpty)
            Section(
              title: 'Referências',
              child: Column(
                children: [
                  for (final id in p.refs)
                    if (data.ref(id) != null) RefTile(data.ref(id)!) else ListTile(title: Text('Referência $id (não encontrada nos dados)')),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _verification(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final v in protocol.verification)
          Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Pill(v.statusLabel, tone: _toneOf(v.status)),
                    Text(v.item, style: const TextStyle(fontWeight: FontWeight.w700)),
                  ],
                ),
                if (v.note.isNotEmpty) Text(v.note),
                if (v.refs.isNotEmpty) Text('Fontes: ${v.refs.map(_refName).join('; ')}', style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
      ],
    );
  }

  static Tone _toneOf(String status) => switch (status) {
        'confirmado' => Tone.ok,
        'corrigido' => Tone.warn,
        'removido' => Tone.bad,
        'ressalva' => Tone.warn,
        _ => Tone.neutral,
      };

  Widget _intensity(BuildContext context, IntensityTable t) {
    final cols = t.header.length;
    List<String> fit(List<String> r) => [
          for (var i = 0; i < cols; i++) i < r.length ? r[i] : '',
        ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: [for (final h in t.header) DataColumn(label: Text(h, style: const TextStyle(fontWeight: FontWeight.w700)))],
            rows: [
              for (final r in t.rows) DataRow(cells: [for (final c in fit(r)) DataCell(Text(c))]),
            ],
          ),
        ),
        if (t.source.isNotEmpty) Text('Fonte: ${t.source}', style: Theme.of(context).textTheme.bodySmall),
        if (t.note.isNotEmpty) Text(t.note, style: Theme.of(context).textTheme.bodySmall),
        if (t.refs.isNotEmpty) Text('Referências: ${t.refs.map(_refName).join('; ')}', style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}
