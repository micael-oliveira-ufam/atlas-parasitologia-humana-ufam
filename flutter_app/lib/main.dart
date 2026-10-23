import 'package:flutter/material.dart';

import 'data/atlas_data.dart';
import 'ui/home_page.dart';
import 'ui/splash.dart';
import 'ui/theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AtlasApp());
}

class AtlasApp extends StatelessWidget {
  const AtlasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Atlas de Parasitologia',
      debugShowCheckedModeBanner: false,
      theme: buildTheme(Brightness.light),
      darkTheme: buildTheme(Brightness.dark),
      themeMode: ThemeMode.system,
      home: const _Bootstrap(),
    );
  }
}

/// Carrega os dados uma vez; mostra erro com "tentar novamente" se algum JSON estiver inválido.
class _Bootstrap extends StatefulWidget {
  const _Bootstrap();

  @override
  State<_Bootstrap> createState() => _BootstrapState();
}

class _BootstrapState extends State<_Bootstrap> {
  late Future<AtlasData> _future;

  /// Duração mínima do splash, para a marca não "piscar" quando os dados carregam rápido.
  static const _minSplash = Duration(milliseconds: 1400);

  Future<AtlasData> _load() async {
    final minDelay = Future<void>.delayed(_minSplash);
    final data = await AtlasData.load(); // se falhar, o erro aparece sem esperar o splash
    await minDelay;
    return data;
  }

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  void _retry() => setState(() => _future = _load());

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<AtlasData>(
      future: _future,
      builder: (context, snap) {
        Widget child;
        if (snap.connectionState != ConnectionState.done) {
          child = const SplashView(key: ValueKey<String>('splash'));
        } else if (snap.hasError) {
          child = Scaffold(
            key: const ValueKey<String>('error'),
            body: Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline, size: 48),
                    const SizedBox(height: 12),
                    const Text('Não foi possível carregar os dados do atlas.'),
                    const SizedBox(height: 8),
                    Text('${snap.error}', style: Theme.of(context).textTheme.bodySmall, textAlign: TextAlign.center),
                    const SizedBox(height: 12),
                    FilledButton(onPressed: _retry, child: const Text('Tentar novamente')),
                  ],
                ),
              ),
            ),
          );
        } else {
          child = HomePage(key: const ValueKey<String>('home'), data: snap.data!);
        }
        return AnimatedSwitcher(duration: const Duration(milliseconds: 350), child: child);
      },
    );
  }
}
