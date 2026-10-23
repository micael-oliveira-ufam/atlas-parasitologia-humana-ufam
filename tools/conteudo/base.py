# -*- coding: utf-8 -*-
"""Estrutura comum do conteúdo verificado.

Cada afirmação exibida no atlas é um registro C(...) com: seção, texto (em português), status,
referências e a evidência literal (trecho da fonte, em inglês quando a fonte é em inglês).

Status:
  confirmado  – o texto exibido corresponde ao que a(s) fonte(s) lida(s) afirma(m);
  corrigido   – o texto anterior do atlas divergia da fonte; o texto exibido segue a fonte (ver 'antes');
  ressalva    – a fonte é parcial, ambígua ou discrepante internamente; a ressalva consta em 'nota';
  observacao  – observação das lâminas feita pelos autores do atlas (não é afirmação de literatura).
"""

STATUS = ("confirmado", "corrigido", "ressalva", "observacao")


def C(sec, text, st, refs, ev="", nota="", key=None, antes=""):
    assert st in STATUS, st
    assert isinstance(refs, (list, tuple))
    return dict(sec=sec, text=text, st=st, refs=list(refs), ev=ev, nota=nota, key=key, antes=antes)


def R(texto_antigo, motivo, campo=""):
    """Afirmação do texto anterior que foi RETIRADA (sem fonte lida) — fica só na auditoria."""
    return dict(antes=texto_antigo, motivo=motivo, campo=campo)


SEM_FONTE = "Nenhuma das fontes lidas nesta revisão sustenta esta afirmação."
