import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import '../data/models.dart';
import 'specimen_page.dart';
import 'theme.dart';
import 'widgets.dart';

/// Aba "Atlas": cabeçalho institucional, números do acervo e cartões coloridos dos módulos.
class ModulesTab extends StatelessWidget {
  const ModulesTab({super.key, required this.data});

  final AtlasData data;

  @override
  Widget build(BuildContext context) {
    final site = data.site;
    final specs = data.specimens;
    final images = specs.fold<int>(0, (a, s) => a + s.images.length);
    final claims = specs.fold<int>(0, (a, s) => a + s.verification.length);
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
      children: [
        GradientHeader(
          gradient: const LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: [kTeal, kTealDark]),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const UfamSeal(size: 64),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          site.title,
                          style: const TextStyle(color: Colors.white, fontSize: 21, fontWeight: FontWeight.w800, height: 1.15),
                        ),
                        if (site.institution.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 4),
                            child: Text(site.institution, style: const TextStyle(color: Color(0xE6FFFFFF), fontSize: 12.5)),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
              if (site.subtitle.isNotEmpty) ...[
                const SizedBox(height: 12),
                Text(site.subtitle, style: const TextStyle(color: Color(0xE6FFFFFF), fontSize: 14)),
              ],
              const SizedBox(height: 16),
              Row(
                children: [
                  _Stat(icon: Icons.biotech, value: '${specs.length}', label: 'espécies'),
                  const SizedBox(width: 8),
                  _Stat(icon: Icons.photo_library_outlined, value: '$images', label: 'imagens'),
                  const SizedBox(width: 8),
                  _Stat(icon: Icons.verified_outlined, value: '$claims', label: 'afirmações\nverificadas'),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        Text('Módulos', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 10),
        for (final m in data.modules) _ModuleCard(module: m),
      ],
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({required this.icon, required this.value, required this.label});

  final IconData icon;
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(color: Colors.white.withAlpha(34), borderRadius: BorderRadius.circular(14)),
        child: Column(
          children: [
            Icon(icon, color: Colors.white, size: 20),
            const SizedBox(height: 2),
            Text(value, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
            Text(label, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xE6FFFFFF), fontSize: 11, height: 1.1)),
          ],
        ),
      ),
    );
  }
}

class _ModuleCard extends StatelessWidget {
  const _ModuleCard({required this.module});

  final AtlasModule module;

  @override
  Widget build(BuildContext context) {
    final n = module.specimens.length;
    final imgs = module.specimens.fold<int>(0, (a, s) => a + s.images.length);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Material(
        color: Colors.transparent,
        child: Ink(
          decoration: BoxDecoration(
            gradient: gradientFor(module.accent),
            borderRadius: BorderRadius.circular(22),
            boxShadow: [BoxShadow(color: accentFor(module.accent).withAlpha(70), blurRadius: 12, offset: const Offset(0, 5))],
          ),
          child: InkWell(
            borderRadius: BorderRadius.circular(22),
            onTap: () => Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => ModulePage(module: module))),
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(color: Colors.white.withAlpha(46), borderRadius: BorderRadius.circular(16)),
                    child: Icon(iconForModule(module.id), color: Colors.white, size: 30),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(module.title, style: const TextStyle(color: Colors.white, fontSize: 19, fontWeight: FontWeight.w800)),
                        if (module.subtitle.isNotEmpty)
                          Text(module.subtitle, style: const TextStyle(color: Color(0xEBFFFFFF), fontSize: 13)),
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: [
                            if (module.underConstruction)
                              const _WhitePill('Em construção')
                            else ...[
                              _WhitePill(n == 1 ? '1 espécie' : '$n espécies'),
                              _WhitePill('$imgs imagens'),
                            ],
                          ],
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.arrow_forward_ios_rounded, color: Colors.white, size: 18),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _WhitePill extends StatelessWidget {
  const _WhitePill(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(color: Colors.white.withAlpha(48), borderRadius: BorderRadius.circular(20)),
      child: Text(text, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700)),
    );
  }
}

class ModulePage extends StatelessWidget {
  const ModulePage({super.key, required this.module});

  final AtlasModule module;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(module.title)),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(16, 4, 16, 24),
        children: [
          GradientHeader(
            gradient: gradientFor(module.accent),
            child: Row(
              children: [
                Icon(iconForModule(module.id), color: Colors.white, size: 36),
                const SizedBox(width: 14),
                Expanded(
                  child: Text(
                    module.description.isNotEmpty ? module.description : module.subtitle,
                    style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.3),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          if (module.specimens.isEmpty)
            Notice(
              module.underConstruction ? 'Este módulo está em construção e ainda não tem espécies publicadas.' : 'Nenhuma espécie publicada neste módulo.',
              tone: Tone.neutral,
            ),
          for (final sp in module.specimens) SpecimenTile(specimen: sp, accent: accentFor(module.accent)),
        ],
      ),
    );
  }
}
