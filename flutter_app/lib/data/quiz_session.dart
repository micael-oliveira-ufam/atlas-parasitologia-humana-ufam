import 'dart:math';

import 'models.dart';

/// Uma pergunta com as alternativas já embaralhadas.
class QuizItem {
  const QuizItem({required this.question, required this.options, required this.correctIndex});

  final QuizQuestion question;
  final List<String> options;
  final int correctIndex;
}

/// Lógica pura do quiz (sem Flutter), para ser testável.
/// As perguntas e as alternativas são embaralhadas a cada sessão, para que a posição da
/// alternativa correta não seja sempre a mesma.
class QuizSession {
  QuizSession(List<QuizQuestion> questions, {Random? random}) : items = _build(questions, random ?? Random());

  final List<QuizItem> items;
  int _index = 0;
  int _score = 0;

  /// Alternativa escolhida na pergunta atual (null = ainda não respondeu).
  int? selected;

  int get index => _index;
  int get total => items.length;
  int get score => _score;
  bool get finished => _index >= items.length;
  bool get answered => selected != null;
  QuizItem get current => items[_index];

  /// Registra a resposta da pergunta atual; ignora toques repetidos.
  void select(int optionIndex) {
    if (finished || answered) return;
    if (optionIndex < 0 || optionIndex >= current.options.length) return;
    selected = optionIndex;
    if (optionIndex == current.correctIndex) _score++;
  }

  void next() {
    if (finished) return;
    _index++;
    selected = null;
  }

  static List<QuizItem> _build(List<QuizQuestion> questions, Random rnd) {
    final valid = questions
        .where((q) => q.options.length >= 2 && q.correctIndex >= 0 && q.correctIndex < q.options.length)
        .toList()
      ..shuffle(rnd);
    return [
      for (final q in valid) _shuffleOptions(q, rnd),
    ];
  }

  static QuizItem _shuffleOptions(QuizQuestion q, Random rnd) {
    final order = List<int>.generate(q.options.length, (i) => i)..shuffle(rnd);
    return QuizItem(
      question: q,
      options: [for (final i in order) q.options[i]],
      correctIndex: order.indexOf(q.correctIndex),
    );
  }
}
