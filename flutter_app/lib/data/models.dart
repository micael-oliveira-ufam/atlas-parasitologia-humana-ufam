// Modelos de dados do atlas. O parsing é tolerante: campo ausente vira null ou lista vazia
// (nunca lança exceção por ausência), mas o contrato dos dados é verificado por
// tool/verify_contract.py e por test/data_test.dart.

typedef Json = Map<String, dynamic>;

String? _str(Json m, String k) {
  final v = m[k];
  return (v is String && v.trim().isNotEmpty) ? v : null;
}

String _strOr(Json m, String k, [String fallback = '']) => _str(m, k) ?? fallback;

int? _int(Json m, String k) {
  final v = m[k];
  if (v is int) return v;
  if (v is num) return v.toInt();
  return null;
}

double _num(Json m, String k, [double fallback = 0]) {
  final v = m[k];
  return v is num ? v.toDouble() : fallback;
}

List<String> _strList(Json m, String k) {
  final v = m[k];
  if (v is List) return v.whereType<String>().toList();
  return const <String>[];
}

List<Json> _objList(Json m, String k) {
  final v = m[k];
  if (v is List) return v.whereType<Map<String, dynamic>>().toList();
  return const <Json>[];
}

Json _obj(Json m, String k) {
  final v = m[k];
  return v is Map<String, dynamic> ? v : <String, dynamic>{};
}

/// "2026-09-04" -> "04/09/2026"; qualquer outro formato -> null.
String? formatIsoDate(String? iso) {
  if (iso == null) return null;
  final m = RegExp(r'^(\d{4})-(\d{2})-(\d{2})$').firstMatch(iso);
  if (m == null) return null;
  return '${m.group(3)}/${m.group(2)}/${m.group(1)}';
}

class Person {
  const Person({required this.name, required this.role});
  final String name;
  final String role;

  /// Iniciais para o avatar (primeira e última palavra do nome).
  String get initials {
    final parts = name.split(RegExp(r'\s+')).where((p) => p.isNotEmpty).toList();
    if (parts.isEmpty) return '?';
    if (parts.length == 1) return parts.first.substring(0, 1).toUpperCase();
    return (parts.first.substring(0, 1) + parts.last.substring(0, 1)).toUpperCase();
  }

  factory Person.fromJson(Json j) => Person(name: _strOr(j, 'name'), role: _strOr(j, 'role'));
}

class SiteInfo {
  const SiteInfo({
    required this.title,
    required this.subtitle,
    required this.course,
    required this.developer,
    required this.references,
    this.institution = '',
    this.advisor,
    this.developers = const <Person>[],
    this.referencesNote = '',
  });

  final String title;
  final String subtitle;
  final String course;
  final String developer;
  final List<String> references;
  final String institution;
  final Person? advisor;
  final List<Person> developers;
  final String referencesNote;

  factory SiteInfo.fromJson(Json j) {
    final adv = j['advisor'];
    return SiteInfo(
      title: _strOr(j, 'title', 'Atlas Digital de Parasitologia Humana'),
      subtitle: _strOr(j, 'subtitle'),
      course: _strOr(j, 'course'),
      developer: _strOr(j, 'developer'),
      references: _strList(j, 'references'),
      institution: _strOr(j, 'institution'),
      advisor: adv is Map<String, dynamic> ? Person.fromJson(adv) : null,
      developers: _objList(j, 'developers').map(Person.fromJson).toList(),
      referencesNote: _strOr(j, 'referencesNote'),
    );
  }
}

class Hotspot {
  const Hotspot({
    required this.id,
    required this.x,
    required this.y,
    required this.title,
    required this.description,
  });

  final String id;

  /// Posição em porcentagem (0–100) da largura/altura da imagem.
  final double x;
  final double y;
  final String title;
  final String description;

  factory Hotspot.fromJson(Json j) => Hotspot(
        id: _strOr(j, 'id'),
        x: _num(j, 'x'),
        y: _num(j, 'y'),
        title: _strOr(j, 'title'),
        description: _strOr(j, 'description'),
      );
}

class ImageItem {
  const ImageItem({
    required this.id,
    required this.file,
    required this.width,
    required this.height,
    required this.type,
    required this.kind,
    required this.alt,
    required this.hotspots,
    this.lamina,
    this.confidence,
    this.caption,
    this.credit,
    this.license,
    this.sourceFile,
    this.date,
    this.dateBasis,
    this.creditStatus,
  });

  final String id;
  final String file;
  final int width;
  final int height;

  /// microfotografia | ilustracao | externa
  final String type;

  /// detalhe | campo | externa
  final String kind;
  final int? lamina;

  /// confirmada | alta | media | null
  final String? confidence;
  final String alt;
  final String? caption;
  final String? credit;
  final String? license;
  final String? sourceFile;
  final String? date;
  final String? dateBasis;

  /// informado | a-confirmar | null
  final String? creditStatus;
  final List<Hotspot> hotspots;

  String get assetPath => 'assets/img/$file';
  double get aspectRatio => (width > 0 && height > 0) ? width / height : 1.0;
  bool get isMicrograph => type == 'microfotografia';
  bool get creditPending => credit == null || creditStatus == 'a-confirmar';

  String get typeLabel => switch (type) {
        'microfotografia' => 'Microfotografia',
        'ilustracao' => 'Ilustração esquemática',
        'externa' => 'Imagem externa (origem a confirmar)',
        _ => type,
      };

  String? get confidenceLabel => switch (confidence) {
        'confirmada' => 'Identificação confirmada',
        'alta' => 'Identificação: alta confiança',
        'media' => 'Identificação: média — a confirmar',
        'documento' => 'Identificação conforme legenda do documento',
        _ => null,
      };

  String? get laminaLabel {
    final l = lamina;
    if (l == null) return null;
    final n = l.toString().padLeft(2, '0');
    return 'Lâmina $n · ${kind == 'detalhe' ? 'detalhe ampliado' : 'campo geral'}';
  }

  /// Linha de crédito exibida ao usuário.
  String get creditLine {
    final c = credit;
    if (c == null) return 'Crédito da imagem: não informado (origem a confirmar).';
    final d = formatIsoDate(date);
    final buf = StringBuffer('Crédito: $c');
    if (d != null) buf.write(' · foto de $d');
    final lic = license;
    if (lic != null) buf.write(' · $lic');
    return buf.toString();
  }

  factory ImageItem.fromJson(Json j) => ImageItem(
        id: _strOr(j, 'id'),
        file: _strOr(j, 'file'),
        width: _int(j, 'width') ?? 0,
        height: _int(j, 'height') ?? 0,
        type: _strOr(j, 'type', 'microfotografia'),
        kind: _strOr(j, 'kind', 'detalhe'),
        lamina: _int(j, 'lamina'),
        confidence: _str(j, 'confidence'),
        alt: _strOr(j, 'alt', 'Imagem do atlas'),
        caption: _str(j, 'caption'),
        credit: _str(j, 'credit'),
        license: _str(j, 'license'),
        sourceFile: _str(j, 'sourceFile'),
        date: _str(j, 'date'),
        dateBasis: _str(j, 'dateBasis'),
        creditStatus: _str(j, 'creditStatus'),
        hotspots: _objList(j, 'hotspots').map(Hotspot.fromJson).toList(),
      );
}

class DiagnosticMethods {
  const DiagnosticMethods({
    required this.alternatives,
    this.goldStandard,
    this.sampleType,
    this.technicalObservation,
  });

  final String? goldStandard;
  final List<String> alternatives;
  final String? sampleType;
  final String? technicalObservation;

  bool get isEmpty =>
      goldStandard == null && alternatives.isEmpty && sampleType == null && technicalObservation == null;

  factory DiagnosticMethods.fromJson(Json j) => DiagnosticMethods(
        goldStandard: _str(j, 'goldStandard'),
        alternatives: _strList(j, 'alternatives'),
        sampleType: _str(j, 'sampleType'),
        technicalObservation: _str(j, 'technicalObservation'),
      );
}

class CycleInfo {
  const CycleInfo({
    this.transmissionRoute,
    this.infectiveForm,
    this.diagnosticForm,
    this.habitat,
    this.cycleType,
  });

  final String? transmissionRoute;
  final String? infectiveForm;
  final String? diagnosticForm;
  final String? habitat;
  final String? cycleType;

  bool get isEmpty =>
      transmissionRoute == null &&
      infectiveForm == null &&
      diagnosticForm == null &&
      habitat == null &&
      cycleType == null;

  factory CycleInfo.fromJson(Json j) => CycleInfo(
        transmissionRoute: _str(j, 'transmissionRoute'),
        infectiveForm: _str(j, 'infectiveForm'),
        diagnosticForm: _str(j, 'diagnosticForm'),
        habitat: _str(j, 'habitat'),
        cycleType: _str(j, 'cycleType'),
      );
}

/// Afirmação científica verificada: texto exibido, status, fontes e trecho-evidência.
class Claim {
  const Claim({
    required this.id,
    required this.section,
    required this.text,
    required this.status,
    required this.refs,
    this.evidence,
    this.note,
    this.before,
  });

  final String id;
  final String section;
  final String text;

  /// confirmado | corrigido | ressalva | observacao
  final String status;
  final List<String> refs;
  final String? evidence;
  final String? note;
  final String? before;

  String get statusLabel => switch (status) {
        'confirmado' => 'Confirmado',
        'corrigido' => 'Corrigido',
        'ressalva' => 'Ressalva',
        'observacao' => 'Observação da lâmina',
        _ => status,
      };

  factory Claim.fromJson(Json j) => Claim(
        id: _strOr(j, 'id'),
        section: _strOr(j, 'section'),
        text: _strOr(j, 'text'),
        status: _strOr(j, 'status'),
        refs: _strList(j, 'refs'),
        evidence: _str(j, 'evidence'),
        note: _str(j, 'note'),
        before: _str(j, 'before'),
      );
}

/// Afirmação do texto anterior que foi retirada por falta de fonte lida.
class RemovedItem {
  const RemovedItem({required this.before, required this.reason, required this.field});
  final String before;
  final String reason;
  final String field;

  factory RemovedItem.fromJson(Json j) =>
      RemovedItem(before: _strOr(j, 'before'), reason: _strOr(j, 'reason'), field: _strOr(j, 'field'));
}

class Specimen {
  const Specimen({
    required this.id,
    required this.moduleId,
    required this.commonName,
    required this.scientificName,
    required this.taxonomy,
    required this.category,
    required this.evolutionaryStage,
    required this.status,
    required this.morphologyDescription,
    required this.keyDiagnosticFeatures,
    required this.clinicalManifestations,
    required this.diagnosticMethods,
    required this.cycle,
    required this.prophylaxis,
    required this.images,
    this.treatment = const <String>[],
    this.taxonomyNote,
    this.ncbi,
    this.verification = const <Claim>[],
    this.removed = const <RemovedItem>[],
    this.approxSizeMicrons,
    this.disease,
    this.pathogenesis,
    this.benchTip,
    this.differentialDiagnosis,
    this.reviewNote,
  });

  final String id;
  final String moduleId;
  final String commonName;
  final String scientificName;

  /// Ordem fixa: filo, classe, ordem, família, gênero, espécie (só os presentes).
  final List<MapEntry<String, String>> taxonomy;
  final String category;
  final String evolutionaryStage;

  /// publicado | revisar | rascunho
  final String status;
  final String? approxSizeMicrons;
  final String morphologyDescription;
  final List<String> keyDiagnosticFeatures;
  final String? disease;
  final String? pathogenesis;
  final List<String> clinicalManifestations;
  final DiagnosticMethods diagnosticMethods;
  final CycleInfo cycle;
  final List<String> prophylaxis;
  final String? benchTip;
  final String? differentialDiagnosis;
  final String? reviewNote;
  final List<ImageItem> images;
  final List<String> treatment;
  final String? taxonomyNote;
  final String? ncbi;
  final List<Claim> verification;
  final List<RemovedItem> removed;

  /// Afirmações de uma seção (ex.: "Clínica"), na ordem do JSON.
  List<Claim> claimsFor(Iterable<String> sections) =>
      verification.where((c) => sections.contains(c.section)).toList();

  ImageItem? get cover => images.isEmpty ? null : images.first;
  bool get inReview => status == 'revisar';

  static const _taxLabels = <String, String>{
    'phylum': 'Filo',
    'class': 'Classe',
    'order': 'Ordem',
    'family': 'Família',
    'genus': 'Gênero',
    'species': 'Espécie',
  };

  factory Specimen.fromJson(Json j, String moduleId) {
    final t = _obj(j, 'taxonomy');
    final tax = <MapEntry<String, String>>[];
    for (final e in _taxLabels.entries) {
      final v = _str(t, e.key);
      if (v != null) tax.add(MapEntry(e.value, v));
    }
    return Specimen(
      id: _strOr(j, 'id'),
      moduleId: moduleId,
      commonName: _strOr(j, 'commonName'),
      scientificName: _strOr(j, 'scientificName'),
      taxonomy: tax,
      category: _strOr(j, 'category'),
      evolutionaryStage: _strOr(j, 'evolutionaryStage'),
      status: _strOr(j, 'status', 'publicado'),
      approxSizeMicrons: _str(j, 'approxSizeMicrons'),
      morphologyDescription: _strOr(j, 'morphologyDescription'),
      keyDiagnosticFeatures: _strList(j, 'keyDiagnosticFeatures'),
      disease: _str(j, 'disease'),
      pathogenesis: _str(j, 'pathogenesis'),
      clinicalManifestations: _strList(j, 'clinicalManifestations'),
      diagnosticMethods: DiagnosticMethods.fromJson(_obj(j, 'diagnosticMethods')),
      cycle: CycleInfo.fromJson(_obj(j, 'transmissionAndCycle')),
      prophylaxis: _strList(j, 'prophylaxis'),
      benchTip: _str(j, 'benchTip'),
      differentialDiagnosis: _str(j, 'differentialDiagnosis'),
      reviewNote: _str(j, 'reviewNote'),
      images: _objList(j, 'images').map(ImageItem.fromJson).toList(),
      treatment: _strList(j, 'treatment'),
      taxonomyNote: _str(t, 'note'),
      ncbi: _str(t, 'ncbi'),
      verification: _objList(j, 'verification').map(Claim.fromJson).toList(),
      removed: _objList(j, 'removed').map(RemovedItem.fromJson).toList(),
    );
  }
}

class AtlasModule {
  AtlasModule({
    required this.id,
    required this.order,
    required this.title,
    required this.subtitle,
    required this.description,
    required this.status,
    required this.accent,
    required this.dataFile,
    List<Specimen>? specimens,
  }) : specimens = specimens ?? <Specimen>[];

  final String id;
  final int order;
  final String title;
  final String subtitle;
  final String description;

  /// ativo | em-construcao
  final String status;

  /// teal | amber | violet
  final String accent;

  /// Caminho relativo do JSON do módulo (ex.: data/modulos/nematelmintos.json).
  final String dataFile;
  final List<Specimen> specimens;

  bool get underConstruction => status == 'em-construcao';

  factory AtlasModule.fromJson(Json j) => AtlasModule(
        id: _strOr(j, 'id'),
        order: _int(j, 'order') ?? 0,
        title: _strOr(j, 'title'),
        subtitle: _strOr(j, 'subtitle'),
        description: _strOr(j, 'description'),
        status: _strOr(j, 'status', 'ativo'),
        accent: _strOr(j, 'accent', 'teal'),
        dataFile: _strOr(j, 'dataFile'),
      );
}

// ---------------------------------------------------------------- referências e protocolos

class RefItem {
  const RefItem({
    required this.id,
    required this.short,
    required this.citation,
    required this.access,
    this.doi,
    this.pmid,
    this.url,
    this.group,
  });

  final String id;
  final String? group;
  final String short;
  final String citation;
  final String access;
  final String? doi;
  final String? pmid;
  final String? url;

  String? get doiUrl => doi == null ? null : 'https://doi.org/$doi';
  String? get pubmedUrl => pmid == null ? null : 'https://pubmed.ncbi.nlm.nih.gov/$pmid/';

  factory RefItem.fromJson(Json j) => RefItem(
        id: _strOr(j, 'id'),
        short: _strOr(j, 'short', _strOr(j, 'id')),
        citation: _strOr(j, 'citation'),
        access: _strOr(j, 'access'),
        doi: _str(j, 'doi'),
        pmid: _str(j, 'pmid'),
        url: _str(j, 'url'),
        group: _str(j, 'group'),
      );
}

class ReviewMeta {
  const ReviewMeta({
    required this.reviewedOn,
    required this.scope,
    required this.notValidation,
    required this.notReviewed,
    required this.sourceAccessNote,
  });

  final String reviewedOn;
  final String scope;
  final String notValidation;
  final List<String> notReviewed;
  final String sourceAccessNote;

  String get reviewedOnBr => formatIsoDate(reviewedOn) ?? reviewedOn;

  factory ReviewMeta.fromJson(Json j) => ReviewMeta(
        reviewedOn: _strOr(j, 'reviewedOn'),
        scope: _strOr(j, 'scope'),
        notValidation: _strOr(j, 'notValidation'),
        notReviewed: _strList(j, 'notReviewed'),
        sourceAccessNote: _strOr(j, 'sourceAccessNote'),
      );
}

class Evidence {
  const Evidence({required this.text, required this.refs});
  final String text;
  final List<String> refs;

  factory Evidence.fromJson(Json j) => Evidence(text: _strOr(j, 'text'), refs: _strList(j, 'refs'));
}

class Verification {
  const Verification({
    required this.item,
    required this.status,
    required this.note,
    required this.refs,
  });

  final String item;

  /// confirmado | corrigido | removido | ressalva
  final String status;
  final String note;
  final List<String> refs;

  String get statusLabel => switch (status) {
        'confirmado' => 'Confirmado',
        'corrigido' => 'Corrigido',
        'removido' => 'Removido',
        'ressalva' => 'Ressalva',
        _ => status,
      };

  factory Verification.fromJson(Json j) => Verification(
        item: _strOr(j, 'item'),
        status: _strOr(j, 'status'),
        note: _strOr(j, 'note'),
        refs: _strList(j, 'refs'),
      );
}

class IntensityTable {
  const IntensityTable({
    required this.source,
    required this.note,
    required this.refs,
    required this.header,
    required this.rows,
  });

  final String source;
  final String note;
  final List<String> refs;
  final List<String> header;
  final List<List<String>> rows;

  factory IntensityTable.fromJson(Json j) {
    final rawRows = j['rows'];
    final rows = <List<String>>[];
    if (rawRows is List) {
      for (final r in rawRows) {
        if (r is List) rows.add(r.map((c) => c.toString()).toList());
      }
    }
    return IntensityTable(
      source: _strOr(j, 'source'),
      note: _strOr(j, 'note'),
      refs: _strList(j, 'refs'),
      header: _strList(j, 'header'),
      rows: rows,
    );
  }
}

class Protocol {
  const Protocol({
    required this.id,
    required this.title,
    required this.popularName,
    required this.indication,
    required this.principle,
    required this.materials,
    required this.steps,
    required this.advantages,
    required this.limitations,
    required this.parasites,
    required this.evidence,
    required this.verification,
    required this.refs,
    this.intensity,
  });

  final String id;
  final String title;
  final String popularName;
  final String indication;
  final String principle;
  final List<String> materials;
  final List<String> steps;
  final List<String> advantages;
  final List<String> limitations;
  final List<String> parasites;
  final List<Evidence> evidence;
  final List<Verification> verification;
  final List<String> refs;
  final IntensityTable? intensity;

  factory Protocol.fromJson(Json j) {
    final inten = j['intensity'];
    return Protocol(
      id: _strOr(j, 'id'),
      title: _strOr(j, 'title'),
      popularName: _strOr(j, 'popularName'),
      indication: _strOr(j, 'indication'),
      principle: _strOr(j, 'principle'),
      materials: _strList(j, 'reagentsAndMaterials'),
      steps: _strList(j, 'stepByStep'),
      advantages: _strList(j, 'advantages'),
      limitations: _strList(j, 'limitations'),
      parasites: _strList(j, 'keyParasitesDetected'),
      evidence: _objList(j, 'evidence').map(Evidence.fromJson).toList(),
      verification: _objList(j, 'verification').map(Verification.fromJson).toList(),
      refs: _strList(j, 'refs'),
      intensity: inten is Map<String, dynamic> ? IntensityTable.fromJson(inten) : null,
    );
  }
}

// ---------------------------------------------------------------- quiz, artefatos, manifesto

class QuizQuestion {
  const QuizQuestion({
    required this.id,
    required this.category,
    required this.title,
    required this.context,
    required this.question,
    required this.options,
    required this.correctIndex,
    required this.explanation,
    this.fieldPearl,
    this.refs = const <String>[],
  });

  final List<String> refs;
  final String id;
  final String category;
  final String title;
  final String context;
  final String question;
  final List<String> options;
  final int correctIndex;
  final String explanation;
  final String? fieldPearl;

  factory QuizQuestion.fromJson(Json j) => QuizQuestion(
        id: _strOr(j, 'id'),
        category: _strOr(j, 'category'),
        title: _strOr(j, 'title'),
        context: _strOr(j, 'context'),
        question: _strOr(j, 'question'),
        options: _strList(j, 'options'),
        correctIndex: _int(j, 'correctIndex') ?? 0,
        explanation: _strOr(j, 'explanation'),
        fieldPearl: _str(j, 'fieldPearl'),
        refs: _strList(j, 'refs'),
      );
}

class ArtifactItem {
  const ArtifactItem({
    required this.name,
    required this.confusedWith,
    required this.howToTell,
    this.refs = const <String>[],
    this.status = '',
    this.evidence = '',
  });
  final List<String> refs;
  final String status;
  final String evidence;
  final String name;
  final String confusedWith;
  final String howToTell;

  factory ArtifactItem.fromJson(Json j) => ArtifactItem(
        name: _strOr(j, 'nome'),
        confusedWith: _strOr(j, 'confundidaCom'),
        howToTell: _strOr(j, 'comoDiferenciar'),
        refs: _strList(j, 'refs'),
        status: _strOr(j, 'status'),
        evidence: _strOr(j, 'evidencia'),
      );
}

class ArtifactGuide {
  const ArtifactGuide({required this.items, required this.tip});
  final List<ArtifactItem> items;
  final String tip;

  factory ArtifactGuide.fromJson(Json j) => ArtifactGuide(
        items: _objList(j, 'itens').map(ArtifactItem.fromJson).toList(),
        tip: _strOr(j, 'dica'),
      );
}

class DataManifest {
  const DataManifest({required this.fileCount, required this.combinedSha256});
  final int fileCount;
  final String combinedSha256;

  String get shortHash => combinedSha256.length >= 12 ? combinedSha256.substring(0, 12) : combinedSha256;

  factory DataManifest.fromJson(Json j) => DataManifest(
        fileCount: _int(j, 'fileCount') ?? 0,
        combinedSha256: _strOr(j, 'combinedSha256', 'desconhecido'),
      );
}
