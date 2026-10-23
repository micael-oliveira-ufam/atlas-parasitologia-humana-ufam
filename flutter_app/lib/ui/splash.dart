import 'package:flutter/material.dart';

import 'theme.dart';
import 'widgets.dart';

/// Tela de abertura: mesmo fundo (kTeal) do splash nativo do Android, para a transição ser contínua.
/// Respeita "remover animações" do sistema (acessibilidade).
class SplashView extends StatefulWidget {
  const SplashView({super.key});

  @override
  State<SplashView> createState() => _SplashViewState();
}

class _SplashViewState extends State<SplashView> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 900));
  late final Animation<double> _fade = CurvedAnimation(parent: _c, curve: Curves.easeOut);
  late final Animation<double> _scale = Tween<double>(begin: 0.86, end: 1).animate(CurvedAnimation(parent: _c, curve: Curves.easeOutBack));
  bool _started = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_started) return;
    _started = true;
    if (MediaQuery.of(context).disableAnimations) {
      _c.value = 1;
    } else {
      _c.forward();
    }
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const cream = Color(0xFFF6F3EC);
    return Scaffold(
      body: Semantics(
        label: 'Atlas de Parasitologia Humana, carregando',
        child: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: [kTeal, kTealDark]),
          ),
          alignment: Alignment.center,
          child: FadeTransition(
            opacity: _fade,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const UfamSeal(size: 112),
                const SizedBox(height: 8),
                const Text(
                  'Universidade Federal do Amazonas',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xE6F6F3EC), fontSize: 14, fontWeight: FontWeight.w600, letterSpacing: 0.3),
                ),
                const SizedBox(height: 26),
                ScaleTransition(
                  scale: _scale,
                  child: Image.asset(
                    'brand/logo_mark.png',
                    width: 112,
                    height: 112,
                    excludeFromSemantics: true,
                    errorBuilder: (context, e, s) => const Icon(Icons.biotech, size: 72, color: cream),
                  ),
                ),
                const SizedBox(height: 14),
                const Text(
                  'Atlas de Parasitologia',
                  style: TextStyle(color: cream, fontSize: 25, fontWeight: FontWeight.w800, letterSpacing: 0.3),
                ),
                const SizedBox(height: 4),
                const Text('Parasitologia Humana', style: TextStyle(color: Color(0xCCF6F3EC), fontSize: 14)),
                const SizedBox(height: 26),
                const SizedBox(
                  width: 28,
                  height: 28,
                  child: CircularProgressIndicator(strokeWidth: 2.5, color: cream),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
