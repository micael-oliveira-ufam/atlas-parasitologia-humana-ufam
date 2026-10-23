import 'dart:io';
import 'dart:math';

import 'package:atlas_parasitologia/data/atlas_data.dart';
import 'package:atlas_parasitologia/data/models.dart';
import 'package:atlas_parasitologia/data/quiz_session.dart';
import 'package:flutter_test/flutter_test.dart';

/// Lê os assets direto do disco (flutter test roda na raiz do pacote).
Future<String> diskReader(String key) => File(key).readAsString();

void main() {
  late AtlasData data;

  setUpAll(() async {
    data = await AtlasData.load(read: diskReader);
  });

  group('contagens (conferidas contra os JSON de origem)', () {
    test('espécies por módulo', () {
      expect(data.moduleById('nematelmintos')!.specimens.length, 5);
      expect(data.moduleById('platelmintos')!.specimens.length, 3);
      expect(data.moduleById('protozoarios')!.specimens.length, 5);
      expect(data.specimens.length, 13);
    });

    test('protocolos, referências e quiz', () {
      expect(data.protocols.length, 5);
      expect(data.refs.length, 48);
      expect(data.quiz.length, 30);
    });

    test('toda referência citada nos protocolos existe', () {
      for (final p in data.protocols) {
        for (final id in p.refs) {
          expect(data.ref(id), isNotNull, reason: '${p.id} cita $id');
        }
      }
    });

    test('toda imagem referenciada existe em assets/img', () {
      for (final s in data.specimens) {
        for (final im in s.images) {
          expect(File(im.assetPath).existsSync(), isTrue, reason: im.assetPath);
        }
      }
    });

    test('toda referência citada nas afirmações, no quiz e nos artefatos existe', () {
      for (final sp in data.specimens) {
        for (final c in sp.verification) {
          for (final id in c.refs) {
            expect(data.ref(id), isNotNull, reason: '${sp.id}/${c.id} cita $id');
          }
        }
      }
      for (final q in data.quiz) {
        for (final id in q.refs) {
          expect(data.ref(id), isNotNull, reason: 'quiz ${q.id} cita $id');
        }
      }
      for (final a in data.artifacts.items) {
        for (final id in a.refs) {
          expect(data.ref(id), isNotNull, reason: 'artefato ${a.name} cita $id');
        }
      }
    });

    test('afirmação corrigida sempre traz o texto anterior', () {
      for (final sp in data.specimens) {
        for (final c in sp.verification.where((c) => c.status == 'corrigido')) {
          expect(c.before, isNotNull, reason: '${sp.id}/${c.id}');
        }
      }
    });

    test('equipe e instituição (modulos.json)', () {
      expect(data.site.institution, contains('Amazonas'));
      expect(data.site.advisor?.name, 'Profa. Dra. Jaila Dias Borges Lalwani');
      expect(data.site.developers.map((p) => p.name),
          ['Micael Davi Lima de Oliveira', 'Elias de Souza Barros']);
    });

    test('nenhum rascunho é carregado', () {
      expect(data.specimens.where((s) => s.status == 'rascunho'), isEmpty);
    });
  });

  group('busca', () {
    test('foldText remove acentos e caixa', () {
      expect(foldText('Ancilostomíase "Amarelão"'), 'ancilostomiase "amarelao"');
    });

    test('encontra por doença sem acento', () {
      final r = searchSpecimens(data, 'ancilostomiase');
      expect(r.map((s) => s.id), contains('ancilostomideo'));
    });

    test('termos são combinados com AND', () {
      expect(searchSpecimens(data, 'ascaris ascaridiase').map((s) => s.id), ['ascaris_lumbricoides']);
      expect(searchSpecimens(data, 'ascaris giardia'), isEmpty);
    });

    test('consulta vazia não retorna nada', () {
      expect(searchSpecimens(data, '   '), isEmpty);
      expect(searchProtocols(data, ''), isEmpty);
    });

    test('encontra protocolo por nome', () {
      expect(searchProtocols(data, 'kato').map((p) => p.id), contains('kato-katz'));
    });
  });

  group('modelos', () {
    test('formatIsoDate', () {
      expect(formatIsoDate('2026-09-04'), '04/09/2026');
      expect(formatIsoDate('04/09/2026'), isNull);
      expect(formatIsoDate(null), isNull);
    });

    test('crédito ausente é sinalizado, nunca inventado', () {
      final im = ImageItem.fromJson(<String, dynamic>{'id': 'x', 'file': 'a/b.jpg'});
      expect(im.credit, isNull);
      expect(im.creditPending, isTrue);
      expect(im.creditLine, contains('não informado'));
    });

    test('parsing tolerante a campos ausentes', () {
      final sp = Specimen.fromJson(<String, dynamic>{'id': 's'}, 'm');
      expect(sp.images, isEmpty);
      expect(sp.cover, isNull);
      expect(sp.taxonomy, isEmpty);
    });
  });

  group('quiz', () {
    test('embaralhar preserva a alternativa correta', () {
      for (var seed = 0; seed < 25; seed++) {
        final s = QuizSession(data.quiz, random: Random(seed));
        expect(s.total, data.quiz.length);
        for (final it in s.items) {
          final original = it.question.options[it.question.correctIndex];
          expect(it.options[it.correctIndex], original);
          expect(it.options.toSet(), it.question.options.toSet());
        }
      }
    });

    test('pontuação, repetição de toque e fim', () {
      final s = QuizSession(data.quiz, random: Random(1));
      var expected = 0;
      while (!s.finished) {
        s.select(s.current.correctIndex);
        s.select((s.current.correctIndex + 1) % s.current.options.length); // ignorado
        expected++;
        expect(s.score, expected);
        s.next();
      }
      expect(s.score, s.total);
    });
  });
}
