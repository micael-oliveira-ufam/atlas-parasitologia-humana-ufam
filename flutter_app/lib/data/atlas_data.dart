import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import 'models.dart';

/// Lê o conteúdo de um asset a partir da chave (ex.: "assets/data/modulos.json").
/// Nos testes, injete uma função que leia do disco.
typedef AssetReader = Future<String> Function(String key);

Future<String> _bundleReader(String key) => rootBundle.loadString(key);

/// Última carga concluída (usada pela interface para resolver nomes de referências sem repassar
/// o objeto por todas as telas). Definida por [AtlasData.load].
AtlasData? currentAtlas;

/// Nome curto de uma referência (cai para o próprio id se não existir).
String refShort(String id) => currentAtlas?.refs[id]?.short ?? id;

/// Todo o conteúdo do atlas, carregado uma vez na abertura do app (tudo offline).
class AtlasData {
  AtlasData._({
    required this.site,
    required this.modules,
    required this.protocols,
    required this.refs,
    required this.review,
    required this.quiz,
    required this.artifacts,
    required this.manifest,
  });

  final SiteInfo site;
  final List<AtlasModule> modules;
  final List<Protocol> protocols;
  final Map<String, RefItem> refs;
  final ReviewMeta review;
  final List<QuizQuestion> quiz;
  final ArtifactGuide artifacts;
  final DataManifest manifest;

  /// Todas as espécies publicadas/em revisão (sem rascunhos), em ordem de módulo.
  List<Specimen> get specimens => [for (final m in modules) ...m.specimens];

  AtlasModule? moduleById(String id) {
    for (final m in modules) {
      if (m.id == id) return m;
    }
    return null;
  }

  RefItem? ref(String id) => refs[id];

  static Future<AtlasData> load({AssetReader? read}) async {
    final reader = read ?? _bundleReader;
    Future<dynamic> j(String key) async => json.decode(await reader(key));

    final registry = await j('assets/data/modulos.json') as Json;
    final modules = (registry['modules'] as List)
        .whereType<Map<String, dynamic>>()
        .map(AtlasModule.fromJson)
        .toList()
      ..sort((a, b) => a.order.compareTo(b.order));

    for (final m in modules) {
      final data = await j('assets/${m.dataFile}') as Json;
      final raw = data['specimens'];
      if (raw is List) {
        for (final s in raw.whereType<Map<String, dynamic>>()) {
          final sp = Specimen.fromJson(s, m.id);
          if (sp.status != 'rascunho') m.specimens.add(sp);
        }
      }
    }

    final protocolsRaw = await j('assets/data/protocolos.json') as List;
    final refsDoc = await j('assets/data/referencias.json') as Json;
    final quizRaw = await j('assets/data/quiz.json') as List;
    final artifactsRaw = await j('assets/data/artefatos.json') as Json;
    final manifestRaw = await j('assets/data/manifest.json') as Json;

    final refItems = (refsDoc['items'] as List)
        .whereType<Map<String, dynamic>>()
        .map(RefItem.fromJson);

    final siteRaw = registry['site'];
    final loaded = AtlasData._(
      site: SiteInfo.fromJson(siteRaw is Map<String, dynamic> ? siteRaw : <String, dynamic>{}),
      modules: modules,
      protocols: protocolsRaw.whereType<Map<String, dynamic>>().map(Protocol.fromJson).toList(),
      refs: {for (final r in refItems) r.id: r},
      review: ReviewMeta.fromJson(_asJson(refsDoc['review'])),
      quiz: quizRaw.whereType<Map<String, dynamic>>().map(QuizQuestion.fromJson).toList(),
      artifacts: ArtifactGuide.fromJson(artifactsRaw),
      manifest: DataManifest.fromJson(manifestRaw),
    );
    currentAtlas = loaded;
    return loaded;
  }

  static Json _asJson(Object? v) => v is Map<String, dynamic> ? v : <String, dynamic>{};
}

const _folds = <String, String>{
  'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
  'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
  'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
  'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
  'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
  'ç': 'c', 'ñ': 'n',
};

/// Minúsculas e sem acentos, para busca tolerante ("amarelao" encontra "amarelão").
String foldText(String s) {
  final lower = s.toLowerCase();
  final b = StringBuffer();
  for (final r in lower.runes) {
    final ch = String.fromCharCode(r);
    b.write(_folds[ch] ?? ch);
  }
  return b.toString();
}

/// Busca por nome comum/científico, doença e estágio. Termos separados por espaço (AND).
List<Specimen> searchSpecimens(AtlasData data, String query) {
  final terms = foldText(query.trim()).split(RegExp(r'\s+')).where((t) => t.isNotEmpty).toList();
  if (terms.isEmpty) return const <Specimen>[];
  return data.specimens.where((s) {
    final hay = foldText([s.commonName, s.scientificName, s.disease ?? '', s.evolutionaryStage, s.category].join(' '));
    return terms.every(hay.contains);
  }).toList();
}

List<Protocol> searchProtocols(AtlasData data, String query) {
  final terms = foldText(query.trim()).split(RegExp(r'\s+')).where((t) => t.isNotEmpty).toList();
  if (terms.isEmpty) return const <Protocol>[];
  return data.protocols.where((p) {
    final hay = foldText([p.title, p.popularName, p.indication, p.parasites.join(' ')].join(' '));
    return terms.every(hay.contains);
  }).toList();
}
