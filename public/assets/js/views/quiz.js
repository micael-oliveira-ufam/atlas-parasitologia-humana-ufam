import { h, clear } from '../dom.js';
import { store } from '../store.js';
import { page, list, refName } from './common.js';

const shuffle = a => { const r = [...a]; for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; } return r; };

export function quizPage(moduleId) {
  const root = h('div', { class: 'quiz' });
  const mods = [{ id: '', title: 'Todos' }, ...store.modules.map(m => ({ id: m.id, title: m.title })), { id: 'geral', title: 'Saúde indígena e campo' }];
  const view = page('Quiz', h('h1', null, 'Quiz de parasitologia'), h('p', { class: 'lead' }, 'As alternativas são embaralhadas a cada tentativa. Escolha o tema e responda uma questão por vez.'), root);

  function menu() {
    clear(root).append(h('div', { class: 'filters' }, mods.map(m => {
      const n = store.quiz.filter(q => !m.id || q.module === m.id).length;
      return h('button', { type: 'button', class: 'btn' + (m.id === (moduleId || '') ? ' on' : ''), disabled: n === 0, onClick: () => start(m.id) }, `${m.title} (${n})`);
    })));
  }
  function start(mid) {
    const qs = shuffle(store.quiz.filter(q => !mid || q.module === mid)).map(q => { const order = shuffle(q.options.map((_, i) => i)); return { ...q, order }; });
    let i = 0, score = 0; const wrong = [];
    function ask() {
      if (i >= qs.length) return end();
      const q = qs[i]; let answered = false;
      const fb = h('div', { class: 'fb', 'aria-live': 'polite' });
      const next = h('button', { type: 'button', class: 'btn primary', hidden: true, onClick: () => { i++; ask(); } }, i + 1 === qs.length ? 'Ver resultado' : 'Próxima');
      const opts = q.order.map((oi, pos) => h('button', { type: 'button', class: 'opt', onClick: e => {
        if (answered) return; answered = true; const ok = oi === q.correctIndex; if (ok) score++; else wrong.push(q);
        opts.forEach((b, p) => { b.disabled = true; if (q.order[p] === q.correctIndex) b.classList.add('right'); });
        e.currentTarget.classList.add(ok ? 'right' : 'wrong');
        fb.append(h('p', null, h('strong', null, ok ? 'Correto. ' : 'Incorreto. '), q.explanation), q.fieldPearl ? h('p', { class: 'tip' }, h('strong', null, 'Dica: '), q.fieldPearl) : null, (q.refs || []).length ? h('p', { class: 'muted small' }, 'Fontes: ' + q.refs.map(refName).join('; ')) : null); next.hidden = false; next.focus();
      } }, h('span', { class: 'letter' }, String.fromCharCode(65 + pos)), q.options[oi]));
      clear(root).append(h('p', { class: 'muted' }, `Questão ${i + 1} de ${qs.length} · acertos: ${score}`), h('div', { class: 'progress' }, h('span', { style: { width: (i / qs.length * 100) + '%' } })),
        h('h2', null, q.title), h('p', { class: 'ctx' }, q.context), h('p', { class: 'q' }, q.question), h('div', { class: 'opts' }, opts), fb, next);
    }
    function end() {
      clear(root).append(h('h2', null, `Resultado: ${score} de ${qs.length} (${Math.round(score / qs.length * 100)}%)`),
        wrong.length ? [h('h3', null, 'Para revisar'), h('ul', { class: 'list' }, wrong.map(q => h('li', null, h('strong', null, q.title), ' — ', q.explanation)))] : h('p', null, 'Você acertou todas.'),
        h('p', null, h('button', { type: 'button', class: 'btn primary', onClick: () => start(mid) }, 'Refazer'), ' ', h('button', { type: 'button', class: 'btn', onClick: menu }, 'Escolher outro tema')));
    }
    ask();
  }
  menu();
  return view;
}
