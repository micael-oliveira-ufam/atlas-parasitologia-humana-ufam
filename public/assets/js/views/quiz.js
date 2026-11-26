// Quiz: texto (banco de questões com fontes), imagem ("qual é o parasita?") e misto.
// O quiz de imagem usa apenas fotos já publicadas no catálogo, de espécies "publicado" (as "em revisão" ficam de fora),
// e a resposta correta é a identificação da legenda do atlas — o feedback informa quando ela é dos autores do documento.
import { h, clear } from '../dom.js';
import { store, imgSrc, getModule } from '../store.js';
import { page, refName, CONF, brief } from './common.js';
import { creditText } from '../meta.js';
import { openLightbox } from '../lightbox.js';
import { icon } from '../icons.js';

const shuffle = a => { const r = [...a]; for (let i = r.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [r[i], r[j]] = [r[j], r[i]]; } return r; };
const label = s => s.commonName.split(' (')[0];
const best = { get(k) { try { return +localStorage.getItem('atlas-quiz-' + k) || 0; } catch { return 0; } }, set(k, v) { try { localStorage.setItem('atlas-quiz-' + k, String(v)); } catch { /* sem armazenamento */ } } };

/** Espécies publicadas com ao menos uma microfotografia. */
const pool = () => store.specimens.filter(s => s.status === 'publicado' && s.images.some(i => i.type === 'microfotografia'));

function imageQuestions(n, moduleId) {
  const all = pool(), base = moduleId ? all.filter(s => s.moduleId === moduleId) : all;
  if (base.length < 1 || all.length < 4) return [];
  const qs = []; let bag = [];
  while (qs.length < n) {
    if (!bag.length) bag = shuffle(base);
    const sp = bag.pop(), ph = shuffle(sp.images.filter(i => i.type === 'microfotografia'))[0];
    const same = shuffle(all.filter(x => x.id !== sp.id && x.moduleId === sp.moduleId)).slice(0, 2);
    const other = shuffle(all.filter(x => x.id !== sp.id && !same.includes(x)));
    const opts = shuffle([sp, ...same, ...other.slice(0, 3 - same.length)]);
    qs.push({ type: 'image', sp, im: ph, options: opts.map(label), correctIndex: opts.indexOf(sp), title: 'Qual é o parasita?' });
  }
  return qs;
}
function textQuestions(n, mid) {
  const src = shuffle(store.quiz.filter(q => !mid || q.module === mid)).slice(0, n);
  return src.map(q => { const order = shuffle(q.options.map((_, i) => i)); return { ...q, type: 'text', options: order.map(i => q.options[i]), correctIndex: order.indexOf(q.correctIndex) }; });
}

export function quizPage(moduleId) {
  const root = h('div', { class: 'quiz' });
  const view = page('Quiz', h('header', { class: 'quiz-head' }, h('h1', null, 'Quiz de parasitologia'), h('p', { class: 'lead' }, 'Escolha como treinar: perguntas de texto com fontes, ou olhe a lâmina e acerte o parasita.')), root);
  const mods = store.modules.filter(m => pool().some(s => s.moduleId === m.id));

  function menu() {
    const nImg = pool().length;
    const mode = (cls, ic, title, desc, extra, key) => h('article', { class: 'card mode ' + cls },
      h('span', { class: 'mode-ico' }, icon(ic, 26)), h('h2', null, title), h('p', null, desc), extra,
      best.get(key) ? h('p', { class: 'muted small' }, `Melhor resultado: ${best.get(key)}%`) : null);
    const startBtn = (t, fn, primary = true) => h('button', { type: 'button', class: 'btn' + (primary ? ' primary' : ''), onClick: fn }, icon('play', 16), t);
    const modOpts = (fn) => h('div', { class: 'chips' }, [['', 'Todos'], ...mods.map(m => [m.id, m.title])].map(([id, t]) => h('button', { type: 'button', class: 'chip-btn', onClick: () => fn(id) }, t)));
    clear(root).append(h('div', { class: 'grid modes' },
      mode('teal', 'scope', 'Qual é o parasita?', `Veja uma fotografia de lâmina real e escolha entre 4 opções. Use o zoom para procurar detalhes. ${nImg} espécies com fotos.`, h('div', null, h('p', { class: 'small muted' }, 'Escolha o grupo e comece (10 fotos):'), modOpts(id => run(imageQuestions(10, id), 'img', 'Qual é o parasita?'))), 'img'),
      mode('amber', 'info', 'Perguntas de texto', `${store.quiz.length} questões com explicação e fontes (CDC e outras): morfologia, ciclo, diagnóstico e saúde indígena.`,
        h('div', null, h('p', { class: 'small muted' }, 'Escolha o tema (10 questões):'), h('div', { class: 'chips' }, [['', 'Todos'], ...store.modules.map(m => [m.id, m.title]), ['geral', 'Saúde indígena e campo']].filter(([id]) => store.quiz.some(q => !id || q.module === id)).map(([id, t]) => h('button', { type: 'button', class: 'chip-btn', onClick: () => run(textQuestions(10, id), 'txt', 'Perguntas de texto') }, t)))), 'txt'),
      mode('violet', 'shuffle', 'Desafio misto', 'Texto e imagem embaralhados: 12 questões para testar tudo de uma vez.', startBtn('Começar', () => run(shuffle([...textQuestions(6, ''), ...imageQuestions(6, '')]), 'mix', 'Desafio misto')), 'mix')));
  }

  function run(qs, key, titleTxt) {
    if (!qs.length) { clear(root).append(h('p', null, 'Não há questões neste tema.'), h('button', { type: 'button', class: 'btn', onClick: menu }, 'Voltar')); return; }
    let i = 0, score = 0, streak = 0, top = 0; const wrong = [];
    function ask() {
      if (i >= qs.length) return end();
      const q = qs[i]; let answered = false;
      const fb = h('div', { class: 'fb', 'aria-live': 'polite' });
      const next = h('button', { type: 'button', class: 'btn primary', hidden: true, onClick: () => { i++; ask(); } }, i + 1 === qs.length ? 'Ver resultado' : 'Próxima');
      const opts = q.options.map((txt, pos) => h('button', { type: 'button', class: 'opt', onClick: e => {
        if (answered) return; answered = true; const ok = pos === q.correctIndex;
        if (ok) { score++; streak++; top = Math.max(top, streak); } else { streak = 0; wrong.push(q); }
        opts.forEach((b, p) => { b.disabled = true; if (p === q.correctIndex) b.classList.add('right'); });
        e.currentTarget.classList.add(ok ? 'right' : 'wrong');
        fb.append(feedback(q, ok)); progress.textContent = `Acertos: ${score} · sequência: ${streak}`; next.hidden = false; next.focus();
      } }, h('span', { class: 'letter' }, String.fromCharCode(65 + pos)), txt));
      const progress = h('span', null, `Acertos: ${score} · sequência: ${streak}`);
      const body = q.type === 'image' ? [
        h('h2', { class: 'q-title' }, q.title),
        h('button', { type: 'button', class: 'q-img', 'aria-label': 'Ampliar a fotografia (zoom)', onClick: () => openLightbox([{ ...q.im, alt: 'Fotografia de lâmina do quiz', caption: '', refs: [], figure: null, detail: null, hotspots: [] }], 0, { title: 'Qual é o parasita?' }) },
          h('img', { src: imgSrc(q.im), alt: 'Fotografia de lâmina de um parasita: identifique a espécie', width: q.im.width, height: q.im.height }), h('span', { class: 'g-cta' }, icon('expand', 16), h('span', null, 'Ampliar'))),
        h('p', { class: 'q' }, 'Qual parasita aparece nesta lâmina?'),
        h('details', { class: 'hint' }, h('summary', null, 'Dica'), h('p', null, `Grupo: ${(getModule(q.sp.moduleId) || {}).title || ''} (${q.sp.category}).`))] : [
        h('h2', { class: 'q-title' }, q.title), q.context ? h('p', { class: 'ctx' }, q.context) : null, h('p', { class: 'q' }, q.question)];
      clear(root).append(h('div', { class: 'qbar muted' }, h('span', null, `${titleTxt} · questão ${i + 1} de ${qs.length}`), progress), h('div', { class: 'progress', role: 'progressbar', 'aria-valuemin': 0, 'aria-valuemax': qs.length, 'aria-valuenow': i }, h('span', { style: { width: (i / qs.length * 100) + '%' } })),
        ...body, h('div', { class: 'opts' }, opts), fb, next);
      window.scrollTo({ top: 0 });
    }
    function feedback(q, ok) {
      if (q.type === 'image') {
        const conf = CONF[q.im.confidence];
        return h('div', null, h('p', null, h('strong', null, ok ? 'Correto! ' : 'Não foi dessa vez. '), 'Resposta: ', h('em', null, label(q.sp)), '. ', q.sp.disease ? `Doença: ${brief(q.sp.disease)}` : ''),
          q.im.caption ? h('p', { class: 'small' }, q.im.caption) : null,
          conf && q.im.confidence !== 'confirmada' && q.im.confidence !== 'alta' ? h('p', { class: 'notice small' }, 'Atenção: ', conf[0].toLowerCase().replace('identificação', 'a identificação'), '. Em lâmina real, confirme por morfologia, medidas e, se preciso, com o docente.') : null,
          h('p', { class: 'muted small' }, creditText(q.im)),
          h('p', null, h('a', { class: 'btn sm', href: `#/m/${q.sp.moduleId}/${q.sp.id}` }, 'Abrir a ficha de ' + label(q.sp))));
      }
      return h('div', null, h('p', null, h('strong', null, ok ? 'Correto. ' : 'Incorreto. '), q.explanation), q.fieldPearl ? h('p', { class: 'tip' }, h('strong', null, 'Dica: '), q.fieldPearl) : null, (q.refs || []).length ? h('p', { class: 'muted small' }, 'Fontes: ' + q.refs.map(refName).join('; ')) : null);
    }
    function end() {
      const pct = Math.round(score / qs.length * 100), prev = best.get(key); if (pct > prev) best.set(key, pct);
      const msg = pct === 100 ? 'Perfeito!' : pct >= 70 ? 'Muito bem!' : pct >= 40 ? 'Bom começo — revise e tente de novo.' : 'Vale revisar as fichas e tentar outra vez.';
      clear(root).append(h('div', { class: 'result' }, h('div', { class: 'ring', style: { '--p': pct } }, h('strong', null, pct + '%')), h('h2', null, `${msg} ${score} de ${qs.length}`),
        h('p', { class: 'muted' }, `Maior sequência de acertos: ${top}.`, pct > prev && prev ? ' Novo recorde!' : '')),
        wrong.length ? [h('h3', null, 'Para revisar'), h('ul', { class: 'list' }, wrong.map(q => q.type === 'image'
          ? h('li', null, 'Era ', h('a', { href: `#/m/${q.sp.moduleId}/${q.sp.id}` }, label(q.sp)), ' (você viu a lâmina de ', label(q.sp), ').')
          : h('li', null, h('strong', null, q.title), ' — ', q.explanation)))] : h('p', null, 'Você acertou todas.'),
        h('p', { class: 'row' }, h('button', { type: 'button', class: 'btn primary', onClick: menu }, 'Jogar de novo'), ' ', h('a', { class: 'btn', href: '#/m/' + (store.modules[0] || {}).id }, 'Estudar as fichas')));
    }
    ask();
  }
  menu();
  return view;
}
