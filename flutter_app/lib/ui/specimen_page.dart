import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import '../data/models.dart';
import 'image_viewer.dart';
import 'theme.dart';
import 'widgets.dart';

void openSpecimen(BuildContext context, Specimen sp) {
  Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => SpecimenPage(specimen: sp)));
}

Color _accentOf(Specimen sp) {
  final m = currentAtlas?.moduleById(sp.moduleId);
  return accentFor(m?.accent ?? 'teal');
}

/// Item de lista de espécie (miniatura + nomes), usado no módulo e na busca.
class SpecimenTile extends StatelessWidget {
  const SpecimenTile({super.key, required this.specimen, this.accent});

  final Specimen specimen;
  final Color? accent;

  @override
  Widget build(BuildContext context) {
    final sp = specimen;
    final cover = sp.cover;
    final color = accent ?? _accentOf(sp);
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: Colors.transparent,
        child: Ink(
          decoration: softBox(context, radius: 18),
          child: InkWell(
            borderRadius: BorderRadius.circular(18),
            onTap: () => openSpecimen(context, sp),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.horizontal(left: Radius.circular(18)),
                  child: SizedBox(
                    width: 104,
                    height: 104,
                    child: cover == null
                        ? Container(color: color.withAlpha(30), child: Icon(Icons.image_not_supported_outlined, color: color))
                        : AtlasImage(cover, cacheWidth: 320),
                  ),
                ),
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(sp.commonName, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15.5)),
                        Text(sp.scientificName, style: const TextStyle(fontStyle: FontStyle.italic, fontSize: 13)),
                        const SizedBox(height: 6),
                        PillWrap(pills: [
                          Pill(sp.category),
                          if (sp.images.isNotEmpty) Pill('${sp.images.length} img'),
                          if (sp.inReview) const Pill('Em revisão', tone: Tone.warn),
                        ]),
                      ],
                    ),
                  ),
                ),
                Padding(padding: const EdgeInsets.only(right: 8), child: Icon(Icons.chevron_right, color: color)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class SpecimenPage extends StatelessWidget {
  const SpecimenPage({super.key, required this.specimen});

  final Specimen specimen;

  void _openViewer(BuildContext context, int index) {
    Navigator.of(context).push(MaterialPageRoute<void>(
      fullscreenDialog: true,
      builder: (_) => ImageViewerPage(images: specimen.images, initialIndex: index, title: specimen.commonName),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final sp = specimen;
    final d = sp.diagnosticMethods;
    final c = sp.cycle;
    final accent = _accentOf(sp);
    final module = currentAtlas?.moduleById(sp.moduleId);
    final grad = gradientFor(module?.accent ?? 'teal');
    return Scaffold(
      appBar: AppBar(title: Text(sp.commonName)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 32),
        children: [
          GradientHeader(
            gradient: grad,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(iconForModule(sp.moduleId), color: Colors.white, size: 26),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        sp.scientificName,
                        style: const TextStyle(color: Colors.white, fontSize: 19, fontWeight: FontWeight.w800, fontStyle: FontStyle.italic, height: 1.2),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Wrap(spacing: 6, runSpacing: 6, children: [
                  if (sp.category.isNotEmpty) _HeaderPill(sp.category),
                  if (sp.evolutionaryStage.isNotEmpty) _HeaderPill(sp.evolutionaryStage),
                  if (sp.inReview) const _HeaderPill('Texto em revisão'),
                ]),
              ],
            ),
          ),
          const SizedBox(height: 12),
          _gallery(context),
          if (sp.reviewNote != null) ...[
            const SizedBox(height: 10),
            Notice(sp.reviewNote!, title: 'Nota de revisão'),
          ],
          if (sp.images.isNotEmpty)
            Section(
              title: 'Créditos das imagens',
              icon: Icons.photo_camera_outlined,
              accent: accent,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (var i = 0; i < sp.images.length; i++)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Imagem ${i + 1}${sp.images[i].laminaLabel != null ? ' · ${sp.images[i].laminaLabel}' : ''}',
                              style: const TextStyle(fontWeight: FontWeight.w700)),
                          if (sp.images[i].caption != null) Text(sp.images[i].caption!),
                          Text(sp.images[i].creditLine, style: Theme.of(context).textTheme.bodySmall),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          if (sp.taxonomy.isNotEmpty)
            Section(
              title: 'Classificação',
              icon: Icons.account_tree_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Taxonomia']),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final e in sp.taxonomy) Align(alignment: Alignment.centerLeft, child: LabeledText(e.key, e.value)),
                  if (sp.ncbi != null) LabeledText('NCBI Taxonomy', sp.ncbi!),
                  if (sp.taxonomyNote != null) Text(sp.taxonomyNote!, style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
          if (sp.morphologyDescription.isNotEmpty || sp.approxSizeMicrons != null)
            Section(
              title: 'Morfologia e tamanho',
              icon: Icons.zoom_in,
              accent: accent,
              claims: sp.claimsFor(const ['Tamanho', 'Morfologia']),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (sp.approxSizeMicrons != null) LabeledText('Tamanho', sp.approxSizeMicrons!),
                  if (sp.morphologyDescription.isNotEmpty) Text(sp.morphologyDescription),
                ],
              ),
            ),
          if (sp.claimsFor(const ['Lâmina']).isNotEmpty)
            Section(
              title: 'Observação das lâminas',
              icon: Icons.visibility_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Lâmina']),
              child: Text(sp.claimsFor(const ['Lâmina']).map((c) => c.text).join(' ')),
            ),
          if (sp.keyDiagnosticFeatures.isNotEmpty)
            Section(
              title: 'Características-chave',
              icon: Icons.key,
              accent: accent,
              claims: sp.claimsFor(const ['Traços']),
              child: BulletList(sp.keyDiagnosticFeatures),
            ),
          if (sp.disease != null)
            Section(title: 'Doença', icon: Icons.coronavirus_outlined, accent: accent, claims: sp.claimsFor(const ['Doença']), child: Text(sp.disease!)),
          if (sp.pathogenesis != null)
            Section(title: 'Patogenia', icon: Icons.sync_alt, accent: accent, claims: sp.claimsFor(const ['Patogenia']), child: Text(sp.pathogenesis!)),
          if (sp.clinicalManifestations.isNotEmpty)
            Section(
              title: 'Manifestações clínicas',
              icon: Icons.medical_information_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Clínica']),
              child: BulletList(sp.clinicalManifestations),
            ),
          if (!d.isEmpty)
            Section(
              title: 'Diagnóstico laboratorial',
              icon: Icons.science_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Diagnóstico']),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (d.goldStandard != null) LabeledText('Método principal', d.goldStandard!),
                  if (d.sampleType != null) LabeledText('Amostra', d.sampleType!),
                  if (d.alternatives.isNotEmpty) ...[
                    const Text('Outros métodos:', style: TextStyle(fontWeight: FontWeight.w700)),
                    BulletList(d.alternatives),
                  ],
                  if (d.technicalObservation != null) LabeledText('Observação técnica', d.technicalObservation!),
                ],
              ),
            ),
          if (!c.isEmpty)
            Section(
              title: 'Transmissão e ciclo',
              icon: Icons.loop,
              accent: accent,
              claims: sp.claimsFor(const ['Ciclo']),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (c.cycleType != null) LabeledText('Ciclo', c.cycleType!),
                  if (c.habitat != null) LabeledText('Local no hospedeiro', c.habitat!),
                  if (c.transmissionRoute != null) LabeledText('Via de transmissão', c.transmissionRoute!),
                  if (c.infectiveForm != null) LabeledText('Forma infectante', c.infectiveForm!),
                  if (c.diagnosticForm != null) LabeledText('Forma diagnóstica', c.diagnosticForm!),
                ],
              ),
            ),
          if (sp.treatment.isNotEmpty)
            Section(
              title: 'Tratamento (fármacos citados)',
              icon: Icons.medication_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Tratamento']),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  BulletList(sp.treatment),
                  Text('Informação didática: doses e esquemas não são reproduzidos; siga diretrizes vigentes e prescrição.',
                      style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
          if (sp.prophylaxis.isNotEmpty)
            Section(
              title: 'Prevenção',
              icon: Icons.health_and_safety_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Prevenção']),
              child: BulletList(sp.prophylaxis),
            ),
          if (sp.differentialDiagnosis != null)
            Section(
              title: 'Diagnóstico diferencial',
              icon: Icons.compare_arrows,
              accent: accent,
              claims: sp.claimsFor(const ['Diferencial']),
              child: Text(sp.differentialDiagnosis!),
            ),
          if (sp.benchTip != null)
            Section(
              title: 'Dica de bancada',
              icon: Icons.tips_and_updates_outlined,
              accent: accent,
              claims: sp.claimsFor(const ['Bancada']),
              child: Text(sp.benchTip!),
            ),
          if (sp.removed.isNotEmpty)
            Section(
              title: 'Revisão do texto anterior',
              icon: Icons.history_edu_outlined,
              accent: accent,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${sp.removed.length} afirmação(ões) do texto anterior foram retiradas por falta de fonte lida; '
                      '${sp.verification.where((c) => c.status == 'corrigido').length} foram corrigidas.'),
                  const SizedBox(height: 6),
                  OutlinedButton.icon(
                    onPressed: () => _showRemoved(context, sp),
                    icon: const Icon(Icons.list_alt, size: 18),
                    label: const Text('Ver itens retirados'),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 14),
          Text(
            'Conteúdo didático; não substitui consulta a fontes primárias nem avaliação clínica.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  void _showRemoved(BuildContext context, Specimen sp) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.75,
        maxChildSize: 0.95,
        builder: (ctx, scroll) => ListView(
          controller: scroll,
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 28),
          children: [
            Text('Itens retirados: ${sp.commonName}', style: Theme.of(ctx).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 8),
            for (final r in sp.removed)
              Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(12),
                decoration: softBox(ctx, radius: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (r.field.isNotEmpty) Pill(r.field, tone: Tone.warn),
                    const SizedBox(height: 6),
                    Text('Antes: ${r.before}'),
                    const SizedBox(height: 4),
                    Text('Motivo: ${r.reason}', style: Theme.of(ctx).textTheme.bodySmall),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _gallery(BuildContext context) {
    final imgs = specimen.images;
    if (imgs.isEmpty) {
      return const Notice('Esta espécie ainda não tem imagens no atlas.', tone: Tone.neutral);
    }
    return SizedBox(
      height: 190,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: imgs.length,
        separatorBuilder: (context, i) => const SizedBox(width: 10),
        itemBuilder: (context, i) {
          final im = imgs[i];
          final w = (190 * im.aspectRatio).clamp(120.0, 280.0).toDouble();
          return Semantics(
            button: true,
            label: 'Ampliar imagem: ${im.alt}',
            child: InkWell(
              borderRadius: BorderRadius.circular(16),
              onTap: () => _openViewer(context, i),
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: SizedBox(width: w, height: 190, child: AtlasImage(im, cacheWidth: 640)),
                  ),
                  Positioned(
                    right: 8,
                    bottom: 8,
                    child: Container(
                      padding: const EdgeInsets.all(5),
                      decoration: const BoxDecoration(color: Colors.black54, shape: BoxShape.circle),
                      child: const Icon(Icons.zoom_out_map, size: 16, color: Colors.white),
                    ),
                  ),
                  Positioned(
                    left: 6,
                    top: 6,
                    child: Pill(im.creditPending ? 'Crédito a confirmar' : 'Crédito informado', tone: im.creditPending ? Tone.warn : Tone.ok),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _HeaderPill extends StatelessWidget {
  const _HeaderPill(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: Colors.white.withAlpha(46), borderRadius: BorderRadius.circular(20)),
      child: Text(text, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700)),
    );
  }
}
