import 'package:flutter/material.dart';

import '../constants.dart';
import '../data/atlas_data.dart';
import '../data/models.dart';
import 'theme.dart';
import 'widgets.dart';

/// Aba "Sobre": instituição, equipe, créditos das imagens, verificação científica, referências e limitações.
class AboutTab extends StatelessWidget {
  const AboutTab({super.key, required this.data});

  final AtlasData data;

  @override
  Widget build(BuildContext context) {
    final site = data.site;
    final specs = data.specimens;
    final allImages = [for (final s in specs) ...s.images];
    final pending = allImages.where((i) => i.creditPending).length;
    final named = allImages.where((i) => !i.creditPending).length;
    final r = data.review;
    final claims = [for (final s in specs) ...s.verification];
    int count(String st) => claims.where((c) => c.status == st).length;
    final removed = specs.fold<int>(0, (a, s) => a + s.removed.length);
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 28),
      children: [
        // Cabeçalho institucional com a logo completa da UFAM
        GradientHeader(
          gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [kUfamGreen, kTealDark]),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)),
                child: Image.asset(
                  'brand/ufam_logo.png',
                  height: 120,
                  fit: BoxFit.contain,
                  semanticLabel: 'Logo da Universidade Federal do Amazonas',
                  errorBuilder: (context, e, s) => const UfamSeal(size: 96),
                ),
              ),
              const SizedBox(height: 14),
              Text(
                site.institution.isNotEmpty ? site.institution : 'Universidade Federal do Amazonas (UFAM)',
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w800),
              ),
              if (site.course.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(site.course, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xE6FFFFFF), fontSize: 13)),
                ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        Text(site.title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
        if (site.subtitle.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 4), child: Text(site.subtitle)),
        Section(
          title: 'Equipe',
          icon: Icons.groups_2_outlined,
          accent: kViolet,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final p in site.developers) _PersonTile(person: p, color: kTeal),
              if (site.advisor != null) _PersonTile(person: site.advisor!, color: kAmber, icon: Icons.school_outlined),
              if (site.developers.isEmpty && site.developer.isNotEmpty) LabeledText('Desenvolvimento', site.developer),
            ],
          ),
        ),
        Section(
          title: 'Verificação científica',
          icon: Icons.verified_outlined,
          accent: kTeal,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('${claims.length} afirmações das fichas de espécie foram conferidas em fontes lidas e registradas uma a uma.'),
              const SizedBox(height: 8),
              PillWrap(pills: [
                Pill('${count('confirmado')} confirmadas', tone: Tone.ok),
                Pill('${count('corrigido')} corrigidas', tone: Tone.warn),
                Pill('${count('ressalva')} com ressalva', tone: Tone.bad),
                Pill('${count('observacao')} observações das lâminas'),
                Pill('$removed itens retirados', tone: Tone.warn),
              ]),
              const SizedBox(height: 8),
              Text('Toque no selo “Fontes” de cada seção, na ficha da espécie, para ver status, referências e o trecho de evidência.',
                  style: Theme.of(context).textTheme.bodySmall),
              if (r.reviewedOn.isNotEmpty) LabeledText('Data da revisão', r.reviewedOnBr),
              if (r.scope.isNotEmpty) Text(r.scope),
              if (r.notValidation.isNotEmpty) ...[
                const SizedBox(height: 8),
                Notice(r.notValidation, title: 'Limite da validação'),
              ],
              if (r.sourceAccessNote.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(r.sourceAccessNote, style: Theme.of(context).textTheme.bodySmall),
              ],
              if (r.notReviewed.isNotEmpty) ...[
                const SizedBox(height: 8),
                const Text('Não revisado:', style: TextStyle(fontWeight: FontWeight.w700)),
                BulletList(r.notReviewed),
              ],
            ],
          ),
        ),
        Section(
          title: 'Créditos das imagens',
          icon: Icons.photo_camera_outlined,
          accent: kCoral,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('${allImages.length} imagens: $named com autoria informada e $pending com crédito ausente ou autoria a confirmar. '
                  'Nenhuma autoria foi presumida.'),
              const SizedBox(height: 8),
              for (final s in specs)
                if (s.images.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    decoration: softBox(context, radius: 14),
                    child: ExpansionTile(
                      shape: const Border(),
                      collapsedShape: const Border(),
                      title: Text(s.commonName, style: const TextStyle(fontWeight: FontWeight.w700)),
                      subtitle: Text('${s.images.length} imagem(ns)'),
                      childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                      expandedCrossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        for (final im in s.images)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: Text('${im.laminaLabel ?? im.typeLabel}: ${im.creditLine}'),
                          ),
                      ],
                    ),
                  ),
            ],
          ),
        ),
        Section(
          title: 'Integridade dos dados',
          icon: Icons.fingerprint,
          accent: kSky,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const LabeledText('Versão do app', appVersion),
              LabeledText('Arquivos de dados e imagens', '${data.manifest.fileCount}'),
              LabeledText('SHA-256 combinado (início)', data.manifest.shortHash),
              Text(
                'O manifesto completo (assets/data/manifest.json) lista o SHA-256 de cada arquivo e permite conferir se o pacote corresponde à fonte.',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        ),
        if (site.references.isNotEmpty)
          Section(
            title: 'Bibliografia de base',
            icon: Icons.menu_book_outlined,
            accent: kAmber,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                BulletList(site.references),
                if (site.referencesNote.isNotEmpty) Text(site.referencesNote, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
        if (data.refs.isNotEmpty)
          Section(
            title: 'Referências citadas (${data.refs.length})',
            icon: Icons.library_books_outlined,
            accent: kViolet,
            child: Column(children: [for (final ref in data.refs.values) RefTile(ref)]),
          ),
        const Section(
          title: 'Limitações',
          icon: Icons.info_outline,
          child: BulletList([
            'Material didático de apoio; não é ferramenta de diagnóstico nem prescrição.',
            'Funciona offline: nenhum dado é enviado a servidores.',
            'Os links externos (DOI/PubMed/páginas) podem ser copiados, mas o app não os abre.',
            'Os trechos de evidência em inglês vêm de um leitor automático de páginas; confira na fonte antes de citar.',
          ]),
        ),
      ],
    );
  }
}

class _PersonTile extends StatelessWidget {
  const _PersonTile({required this.person, required this.color, this.icon});

  final Person person;
  final Color color;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          CircleAvatar(
            radius: 24,
            backgroundColor: color,
            child: icon != null
                ? Icon(icon, color: Colors.white)
                : Text(person.initials, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(person.name, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15.5)),
                Text(person.role, style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
