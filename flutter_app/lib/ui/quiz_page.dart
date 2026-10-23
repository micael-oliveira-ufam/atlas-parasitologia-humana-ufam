import 'package:flutter/material.dart';

import '../data/atlas_data.dart';
import '../data/quiz_session.dart';
import 'theme.dart';
import 'widgets.dart';

/// Aba "Quiz": perguntas e alternativas embaralhadas a cada sessão.
class QuizTab extends StatefulWidget {
  const QuizTab({super.key, required this.data});

  final AtlasData data;

  @override
  State<QuizTab> createState() => _QuizTabState();
}

class _QuizTabState extends State<QuizTab> {
  late QuizSession _s;

  @override
  void initState() {
    super.initState();
    _s = QuizSession(widget.data.quiz);
  }

  void _restart() => setState(() => _s = QuizSession(widget.data.quiz));

  @override
  Widget build(BuildContext context) {
    if (_s.items.isEmpty) {
      return const Center(child: Padding(padding: EdgeInsets.all(24), child: Text('Nenhuma questão disponível.')));
    }
    if (_s.finished) return _result(context);

    final it = _s.current;
    final q = it.question;
    return ListView(
      key: ValueKey<int>(_s.index),
      padding: const EdgeInsets.all(16),
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(value: _s.index / _s.total, minHeight: 8),
        ),
        const SizedBox(height: 8),
        Text('Questão ${_s.index + 1} de ${_s.total} · acertos: ${_s.score}', style: Theme.of(context).textTheme.bodySmall),
        const SizedBox(height: 8),
        if (q.category.isNotEmpty) PillWrap(pills: [Pill(q.category)]),
        if (q.title.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(q.title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
        ],
        if (q.context.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(q.context),
        ],
        const SizedBox(height: 12),
        Text(q.question, style: const TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 12),
        for (var i = 0; i < it.options.length; i++) _option(context, it, i),
        if (_s.answered) ...[
          const SizedBox(height: 8),
          Notice(q.explanation, title: _s.selected == it.correctIndex ? 'Correto' : 'Incorreto', tone: _s.selected == it.correctIndex ? Tone.ok : Tone.bad),
          if (q.fieldPearl != null) Notice(q.fieldPearl!, title: 'Pérola de bancada', tone: Tone.neutral),
          if (q.refs.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text('Fontes: ${q.refs.map(refShort).join('; ')}', style: Theme.of(context).textTheme.bodySmall),
            ),
          const SizedBox(height: 8),
          FilledButton(
            onPressed: () => setState(_s.next),
            child: Text(_s.index + 1 >= _s.total ? 'Ver resultado' : 'Próxima'),
          ),
        ],
      ],
    );
  }

  Widget _option(BuildContext context, QuizItem it, int i) {
    var tone = Tone.neutral;
    if (_s.answered) {
      if (i == it.correctIndex) {
        tone = Tone.ok;
      } else if (i == _s.selected) {
        tone = Tone.bad;
      }
    }
    final c = toneColors(context, tone);
    final letter = String.fromCharCode(65 + i);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: _s.answered ? c.bg : Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(14),
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: _s.answered ? null : () => setState(() => _s.select(i)),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  radius: 13,
                  backgroundColor: _s.answered ? c.fg.withAlpha(40) : kTeal.withAlpha(35),
                  child: Text(letter, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: _s.answered ? c.fg : kTeal)),
                ),
                const SizedBox(width: 10),
                Expanded(child: Text(it.options[i], style: TextStyle(color: _s.answered ? c.fg : null))),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _result(BuildContext context) {
    final pct = (_s.score * 100 / _s.total).round();
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(pct >= 70 ? Icons.emoji_events_rounded : Icons.flag_rounded, size: 72, color: pct >= 70 ? kAmber : kTeal),
            Text('$pct%', style: Theme.of(context).textTheme.displayMedium?.copyWith(fontWeight: FontWeight.w800)),
            Text('${_s.score} de ${_s.total} questões corretas'),
            const SizedBox(height: 16),
            FilledButton(onPressed: _restart, child: const Text('Refazer (ordem embaralhada)')),
          ],
        ),
      ),
    );
  }
}
