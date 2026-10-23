import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../data/atlas_data.dart';
import '../data/models.dart';
import 'theme.dart';

/// Etiqueta colorida (equivalente ao "badge" do site).
class Pill extends StatelessWidget {
  const Pill(this.text, {super.key, this.tone = Tone.neutral});

  final String text;
  final Tone tone;

  @override
  Widget build(BuildContext context) {
    final c = toneColors(context, tone);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: c.bg, borderRadius: BorderRadius.circular(20)),
      child: Text(text, style: TextStyle(color: c.fg, fontSize: 12, fontWeight: FontWeight.w600)),
    );
  }
}

class PillWrap extends StatelessWidget {
  const PillWrap({super.key, required this.pills});
  final List<Widget> pills;

  @override
  Widget build(BuildContext context) => Wrap(spacing: 6, runSpacing: 6, children: pills);
}

/// Seção com título (anunciado como cabeçalho para leitores de tela). Quando recebe [claims],
/// mostra a barra de fontes/verificação da seção.
class Section extends StatelessWidget {
  const Section({super.key, required this.title, required this.child, this.icon, this.claims = const <Claim>[], this.accent});

  final String title;
  final Widget child;
  final IconData? icon;
  final List<Claim> claims;
  final Color? accent;

  @override
  Widget build(BuildContext context) {
    final color = accent ?? Theme.of(context).colorScheme.primary;
    return Container(
      margin: const EdgeInsets.only(top: 14),
      padding: const EdgeInsets.fromLTRB(16, 14, 16, 14),
      decoration: softBox(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (icon != null)
                Container(
                  width: 34,
                  height: 34,
                  margin: const EdgeInsets.only(right: 10),
                  decoration: BoxDecoration(color: color.withAlpha(36), borderRadius: BorderRadius.circular(10)),
                  child: Icon(icon, size: 19, color: color),
                ),
              Expanded(
                child: Semantics(
                  header: true,
                  child: Text(title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          child,
          if (claims.isNotEmpty) SourceBar(title: title, claims: claims),
        ],
      ),
    );
  }
}

/// Barra "Fontes": resume status e referências das afirmações da seção; toque abre o detalhe.
class SourceBar extends StatelessWidget {
  const SourceBar({super.key, required this.title, required this.claims});

  final String title;
  final List<Claim> claims;

  @override
  Widget build(BuildContext context) {
    final refIds = <String>{for (final c in claims) ...c.refs};
    final corrected = claims.where((c) => c.status == 'corrigido').length;
    final caveats = claims.where((c) => c.status == 'ressalva').length;
    final names = refIds.map(refShort).toList();
    final tone = caveats > 0 ? Tone.bad : (corrected > 0 ? Tone.warn : Tone.ok);
    final c = toneColors(context, tone);
    final summary = StringBuffer('${claims.length} afirmação(ões) verificada(s)');
    if (corrected > 0) summary.write(' · $corrected corrigida(s)');
    if (caveats > 0) summary.write(' · $caveats com ressalva');
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Material(
        color: c.bg,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () => showClaimsSheet(context, title, claims),
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.verified_outlined, size: 18, color: c.fg),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(summary.toString(), style: TextStyle(color: c.fg, fontWeight: FontWeight.w700, fontSize: 12.5)),
                      if (names.isNotEmpty)
                        Text('Fontes: ${names.join(' · ')}', style: TextStyle(color: c.fg, fontSize: 12)),
                      Text('Toque para ver evidências e referências', style: TextStyle(color: c.fg.withAlpha(190), fontSize: 11.5)),
                    ],
                  ),
                ),
                Icon(Icons.chevron_right, size: 18, color: c.fg),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Detalhe das afirmações: status, texto, trecho-evidência, fontes e texto anterior (se corrigido).
void showClaimsSheet(BuildContext context, String title, List<Claim> claims) {
  showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    builder: (ctx) => DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.8,
      minChildSize: 0.4,
      maxChildSize: 0.95,
      builder: (ctx, scroll) => ListView(
        controller: scroll,
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 28),
        children: [
          Text('Verificação: $title', style: Theme.of(ctx).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800)),
          const SizedBox(height: 4),
          Text(
            'Cada afirmação foi conferida em fonte lida. As citações em inglês são os trechos devolvidos pelo leitor de páginas; confira na fonte antes de citar.',
            style: Theme.of(ctx).textTheme.bodySmall,
          ),
          const SizedBox(height: 10),
          for (final c in claims) ClaimCard(claim: c),
        ],
      ),
    ),
  );
}

class ClaimCard extends StatelessWidget {
  const ClaimCard({super.key, required this.claim});

  final Claim claim;

  @override
  Widget build(BuildContext context) {
    final c = claim;
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: softBox(context, radius: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          PillWrap(pills: [Pill(c.statusLabel, tone: toneForClaim(c.status)), Pill(c.section)]),
          const SizedBox(height: 8),
          Text(c.text),
          if (c.evidence != null && c.evidence!.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text('Evidência: ${c.evidence}', style: Theme.of(context).textTheme.bodySmall),
          ],
          if (c.refs.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text('Referências: ${c.refs.map(refShort).join(' · ')}', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700)),
          ],
          if (c.before != null) ...[
            const SizedBox(height: 6),
            Text('Texto anterior (corrigido): ${c.before}', style: Theme.of(context).textTheme.bodySmall),
          ],
          if (c.note != null && c.note!.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text('Nota: ${c.note}', style: Theme.of(context).textTheme.bodySmall),
          ],
        ],
      ),
    );
  }
}

class BulletList extends StatelessWidget {
  const BulletList(this.items, {super.key, this.numbered = false});

  final List<String> items;
  final bool numbered;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var i = 0; i < items.length; i++)
          Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(width: numbered ? 28 : 16, child: Text(numbered ? '${i + 1}.' : '•')),
                Expanded(child: Text(items[i])),
              ],
            ),
          ),
      ],
    );
  }
}

/// Aviso em caixa (ressalvas, avisos de revisão etc.).
class Notice extends StatelessWidget {
  const Notice(this.text, {super.key, this.tone = Tone.warn, this.title});

  final String text;
  final String? title;
  final Tone tone;

  @override
  Widget build(BuildContext context) {
    final c = toneColors(context, tone);
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: c.bg, borderRadius: BorderRadius.circular(10)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title != null)
            Text(title!, style: TextStyle(color: c.fg, fontWeight: FontWeight.w700)),
          Text(text, style: TextStyle(color: c.fg)),
        ],
      ),
    );
  }
}

class LabeledText extends StatelessWidget {
  const LabeledText(this.label, this.value, {super.key});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Text.rich(TextSpan(children: [
        TextSpan(text: '$label: ', style: const TextStyle(fontWeight: FontWeight.w700)),
        TextSpan(text: value),
      ])),
    );
  }
}

/// Imagem do pacote de assets; mostra um substituto se o arquivo não existir.
class AtlasImage extends StatelessWidget {
  const AtlasImage(this.image, {super.key, this.fit = BoxFit.cover, this.cacheWidth});

  final ImageItem image;
  final BoxFit fit;
  final int? cacheWidth;

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      image.assetPath,
      fit: fit,
      cacheWidth: cacheWidth,
      semanticLabel: image.alt,
      errorBuilder: (context, error, stack) => Container(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        alignment: Alignment.center,
        child: const Icon(Icons.broken_image_outlined),
      ),
    );
  }
}

Future<void> copyText(BuildContext context, String text, String message) async {
  await Clipboard.setData(ClipboardData(text: text));
  if (!context.mounted) return;
  ScaffoldMessenger.of(context)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(content: Text(message)));
}

/// Referência bibliográfica com botões para copiar DOI/PubMed (o app não abre links externos).
class RefTile extends StatelessWidget {
  const RefTile(this.ref, {super.key});

  final RefItem ref;

  @override
  Widget build(BuildContext context) {
    final doi = ref.doiUrl;
    final pm = ref.pubmedUrl;
    final url = ref.url;
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(ref.short, style: const TextStyle(fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text(ref.citation),
            if (ref.access.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text('Acesso: ${ref.access}', style: Theme.of(context).textTheme.bodySmall),
            ],
            Wrap(
              spacing: 4,
              children: [
                if (doi != null)
                  TextButton.icon(
                    onPressed: () => copyText(context, doi, 'Link do DOI copiado'),
                    icon: const Icon(Icons.copy, size: 16),
                    label: const Text('Copiar DOI'),
                  ),
                if (pm != null)
                  TextButton.icon(
                    onPressed: () => copyText(context, pm, 'Link do PubMed copiado'),
                    icon: const Icon(Icons.copy, size: 16),
                    label: const Text('Copiar PubMed'),
                  ),
                if (doi == null && pm == null && url != null)
                  TextButton.icon(
                    onPressed: () => copyText(context, url, 'Link copiado'),
                    icon: const Icon(Icons.copy, size: 16),
                    label: const Text('Copiar link'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Brasão da UFAM sobre disco branco (legível em fundos coloridos e no tema escuro).
class UfamSeal extends StatelessWidget {
  const UfamSeal({super.key, this.size = 72});

  final double size;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Brasão da Universidade Federal do Amazonas',
      image: true,
      child: Container(
        width: size,
        height: size,
        padding: EdgeInsets.all(size * 0.04),
        decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle),
        child: ClipOval(
          child: Image.asset(
            'brand/ufam_brasao.png',
            fit: BoxFit.contain,
            excludeFromSemantics: true,
            errorBuilder: (context, e, s) => Icon(Icons.account_balance, size: size * 0.5, color: kUfamGreen),
          ),
        ),
      ),
    );
  }
}

/// Cabeçalho em degradê com título, subtítulo e ícone (módulos, espécie).
class GradientHeader extends StatelessWidget {
  const GradientHeader({super.key, required this.gradient, required this.child, this.radius = 24, this.padding = const EdgeInsets.all(20)});

  final Gradient gradient;
  final Widget child;
  final double radius;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(radius),
        boxShadow: [BoxShadow(color: Colors.black.withAlpha(30), blurRadius: 14, offset: const Offset(0, 6))],
      ),
      child: child,
    );
  }
}
