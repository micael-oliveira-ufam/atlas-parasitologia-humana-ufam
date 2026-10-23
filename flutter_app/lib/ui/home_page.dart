import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import 'about_page.dart';
import 'artifacts_page.dart';
import 'module_page.dart';
import 'protocols_page.dart';
import 'quiz_page.dart';
import 'search.dart';
import 'theme.dart';
import 'widgets.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.data});

  final AtlasData data;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _tab = 0;

  static const _titles = <String>['Atlas', 'Protocolos', 'Quiz', 'Artefatos', 'Sobre'];

  @override
  Widget build(BuildContext context) {
    final d = widget.data;
    return Scaffold(
      appBar: AppBar(
        titleSpacing: 12,
        title: Row(
          children: [
            const UfamSeal(size: 34),
            const SizedBox(width: 10),
            Text(_titles[_tab]),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.search),
            tooltip: 'Buscar',
            onPressed: () => showSearch<void>(context: context, delegate: AtlasSearch(d)),
          ),
        ],
      ),
      body: IndexedStack(
        index: _tab,
        children: [
          ModulesTab(data: d),
          ProtocolsTab(data: d),
          QuizTab(data: d),
          ArtifactsTab(data: d),
          AboutTab(data: d),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.biotech_outlined), selectedIcon: Icon(Icons.biotech, color: kTeal), label: 'Atlas'),
          NavigationDestination(icon: Icon(Icons.science_outlined), selectedIcon: Icon(Icons.science, color: kViolet), label: 'Protocolos'),
          NavigationDestination(icon: Icon(Icons.quiz_outlined), selectedIcon: Icon(Icons.quiz, color: kAmber), label: 'Quiz'),
          NavigationDestination(icon: Icon(Icons.warning_amber_outlined), selectedIcon: Icon(Icons.warning_amber, color: kCoral), label: 'Artefatos'),
          NavigationDestination(icon: Icon(Icons.info_outline), selectedIcon: Icon(Icons.info, color: kSky), label: 'Sobre'),
        ],
      ),
    );
  }
}
