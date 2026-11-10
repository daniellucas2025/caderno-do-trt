import copy
# -*- coding: utf-8 -*-
"""
Gerador da Plataforma Oficial de Metas de Estudos - TRT-7 (Estudos DL)
VERSAO BASE CANONICA DEFINITIVA (v3.3.0) - Aprovada pelo Usuario

DIRETRIZ DE ARQUITETURA PERMANENTE:
- Todas as proximas alteracoes, melhorias e inclusao de materias devem OBRIGATORIAMENTE
  manter e herdar este layout, organizacao visual e hierarquia.
- Topbar em 2 niveis balanceados (Navegacao/Ciclo no topo, Ferramentas + Busca Centralizada na subrow).
- Banner do Quadro limpo e direto, sem repeticao de legendas estaticas (apenas botoes de filtro).
- Matriz compacta com todas as 9 disciplinas visiveis.
- Metas extras do HTML rigorosamente posicionadas no final de cada disciplina, abrindo sob demanda.
"""

import os
import re
import json
import argparse
import unicodedata
from pathlib import Path
from html.parser import HTMLParser

class ExtratorInfoHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.h1 = ""
        self.in_title = False
        self.in_h1 = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'title' and not self.title:
            self.in_title = True
        elif tag.lower() == 'h1' and not self.h1:
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag.lower() == 'title':
            self.in_title = False
        elif tag.lower() == 'h1':
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_h1:
            self.h1 += data

def limpar_nome_disciplina(nome):
    nome = re.sub(r'_COMPLETO$', '', nome, flags=re.I)
    nome = re.sub(r'\s*-\s*Material Compilado.*$', '', nome, flags=re.I)
    nome = re.sub(r'\s*\|\s*Hotmart.*$', '', nome, flags=re.I)
    return nome.strip()

def normalizar_texto(txt):
    return "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn").lower().strip()

def extrair_aulas_do_html(conteudo_html, nome_arquivo):
    info = ExtratorInfoHTML()
    try:
        info.feed(conteudo_html[:50000])
    except Exception:
        pass

    nome_disc = ""
    if info.h1 and info.h1.strip():
        nome_disc = info.h1.strip()
    elif info.title and info.title.strip():
        nome_disc = info.title.strip()
    else:
        nome_disc = Path(nome_arquivo).stem

    nome_disc = limpar_nome_disciplina(nome_disc)
    aulas_extraidas = []

    tab_btns = re.findall(r'<button class="tab-btn[^"]*"[^>]*>(.*?)</button>', conteudo_html, re.I | re.S)
    tab_panels = re.findall(r'<section id="mod-tab-(\d+)" class="tab-panel[^"]*">(.*?)</section>', conteudo_html, re.I | re.S)

    if tab_panels:
        for idx_str, panel_html in tab_panels:
            idx = int(idx_str)
            nome_mod = tab_btns[idx].strip() if idx < len(tab_btns) else f"Módulo {idx + 1}"
            cards = re.findall(r'<article class="aula-card">(.*?)</article>', panel_html, re.I | re.S)
            for c_idx, card_html in enumerate(cards):
                tit_match = re.search(r'<h2 class="aula-titulo">(.*?)</h2>', card_html, re.I | re.S)
                titulo_aula = tit_match.group(1).strip() if tit_match else f"Aula {c_idx + 1}"
                corpo_match = re.search(r'<div class="aula-corpo">(.*?)</div>', card_html, re.I | re.S)
                corpo_html = corpo_match.group(1).strip() if corpo_match else card_html

                aulas_extraidas.append({
                    "modulo": nome_mod,
                    "titulo": titulo_aula,
                    "html": corpo_html
                })
    else:
        articles = re.findall(r'<article[^>]*>(.*?)</article>', conteudo_html, re.I | re.S)
        if articles:
            for a_idx, art_html in enumerate(articles):
                tit = re.search(r'<h[1-4][^>]*>(.*?)</h[1-4]>', art_html, re.I | re.S)
                t_aula = tit.group(1).strip() if tit else f"Tópico {a_idx + 1}"
                aulas_extraidas.append({
                    "modulo": "Geral",
                    "titulo": t_aula,
                    "html": art_html
                })

    return nome_disc, aulas_extraidas

# ==============================================================================
# CATÁLOGO DE METAS COM MAPEAMENTO DETERMINÍSTICO E PRECISO (CONFORME PDF)
# ==============================================================================
METAS_CATALOGO = [
    # 1. Direito Constitucional (DC) - 15 Metas
    {
        "sigla": "DC",
        "disciplina": "Direito Constitucional",
        "arquivo_alvo": "Direito Constitucional_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": False, "assuntos": ["Conceito de Constituição", "Eficácia e aplicabilidade das normas", "Interpretação constitucional", "Leitura da Constituição (arts. 1º a 4º)", "Princípios fundamentais"], "chaves": ["conceito de constituicao", "eficacia e aplicabilidade", "principios fundamentais"]},
            {"numero": 2, "revisao": False, "prioritaria": True, "assuntos": ["★ Classificação dos direitos e garantias fundamentais", "★ Leitura da Constituição (art. 5º)", "★ Direitos e deveres individuais e coletivos", "★ Remédios constitucionais"], "chaves": ["direitos e deveres individuais e coletivos (art. 5º)"]},
            {"numero": 3, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da Constituição (arts. 6º a 11)", "Direitos sociais", "Leitura da Constituição (arts. 12 e 13)", "Nacionalidade"], "chaves": ["direitos sociais (arts. 6º ao 11)", "nacionalidade (arts. 12 e 13)"]},
            {"numero": 4, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da Constituição (arts. 14 a 16)", "Direitos políticos", "Leitura da Constituição (art. 17)", "Partidos políticos"], "chaves": ["direitos politicos (arts. 14 a 16)", "partidos politicos (art. 17)"]},
            {"numero": 5, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 6, "revisao": False, "prioritaria": True, "assuntos": ["★ União - Estados - Municípios (arts. 18 a 31)", "Distrito Federal e Territórios (arts. 32 e 33)", "Intervenção (arts. 34 a 36)"], "chaves": ["uniao, estados e municipios", "distrito federal e territorios", "intervencao (arts. 34 a 36)"]},
            {"numero": 7, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da Constituição (arts. 37 a 41)", "★ Administração Pública e servidores públicos"], "chaves": ["administracao publica e servidores publicos (arts. 37 a 41)"]},
            {"numero": 8, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da Constituição (arts. 59 a 69)", "Processo Legislativo"], "chaves": ["processo legislativo (arts. 59 a 69)"]},
            {"numero": 9, "revisao": False, "prioritaria": False, "assuntos": ["Fiscalização (arts. 70 a 75)", "Poder Executivo (arts. 76 a 86)", "Ministros e Conselhos (arts. 87 a 91)"], "chaves": ["fiscalizacao contabil", "presidente e vice-presidente"]},
            {"numero": 10, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 11, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da Constituição (arts. 92 a 100)", "★ Poder Judiciário - Disposições gerais"], "chaves": ["disposicoes gerais (arts. 92 a 100)"]},
            {"numero": 12, "revisao": False, "prioritaria": True, "assuntos": ["★ Supremo Tribunal Federal - STF (arts. 101 a 103-A)", "★ Conselho Nacional de Justiça - CNJ (art. 103-B)", "★ Superior Tribunal de Justiça - STJ (arts. 104 e 105)"], "chaves": ["supremo tribunal federal", "conselho nacional de justica", "superior tribunal de justica"]},
            {"numero": 13, "revisao": False, "prioritaria": True, "assuntos": ["★ Justiça do Trabalho (arts. 111 a 117)", "Funções essenciais à Justiça (arts. 127 a 135)"], "chaves": ["justica do trabalho (arts. 111 a 117)", "funcoes essenciais a justica"]},
            {"numero": 14, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 15, "revisao": False, "prioritaria": False, "extra": True, "subtitulo": "Meta Extra • Controle de Constitucionalidade", "assuntos": ["Controle de constitucionalidade"], "chaves": ["controle de constitucionalidade"]}
        ]
    },

    # 2. Português (PORT) - 18 Metas
    {
        "sigla": "PORT",
        "disciplina": "Português",
        "arquivo_alvo": "Português_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": False, "assuntos": ["Ortografia", "Acentuação", "Porquês"], "chaves": ["ortografia", "acentuacao", "por que, por que"]},
            {"numero": 2, "revisao": False, "prioritaria": True, "assuntos": ["Formação de palavras", "★ Morfologia - Substantivo - Artigo - Numeral - Adjetivo - Advérbio - Preposição - Interjeição", "★ Morfologia - Conjunção (e Tabela de Conectivos)"], "chaves": ["formacao de palavras", "substantivo, artigo, numeral"]},
            {"numero": 3, "revisao": False, "prioritaria": True, "assuntos": ["★ Morfologia - Pronome (e Colocação Pronominal)"], "chaves": ["pronome (e colocacao pronominal)"]},
            {"numero": 4, "revisao": False, "prioritaria": True, "assuntos": ["★ Morfologia - Verbo"], "chaves": ["verbo"]},
            {"numero": 5, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 6, "revisao": False, "prioritaria": False, "assuntos": ["Sintaxe"], "chaves": ["sintaxe"]},
            {"numero": 7, "revisao": False, "prioritaria": False, "assuntos": ["Período composto (coordenação e subordinação)"], "chaves": ["periodo composto (coordenacao e subordinacao)"]},
            {"numero": 8, "revisao": False, "prioritaria": True, "assuntos": ["★ Pontuação"], "chaves": ["pontuacao"]},
            {"numero": 9, "revisao": False, "prioritaria": False, "assuntos": ["Funções do QUE e de outros pronomes", "Vozes verbais e funções do SE"], "chaves": ["funcoes do que e de outros pronomes", "vozes verbais e funcoes do se"]},
            {"numero": 10, "revisao": False, "prioritaria": True, "assuntos": ["★ Concordância", "★ Regência", "★ Crase"], "chaves": ["concordancia", "regencia", "crase"]},
            {"numero": 11, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 12, "revisao": False, "prioritaria": True, "assuntos": ["★ Interpretação e compreensão textual"], "chaves": ["interpretacao e compreensao textual"]},
            {"numero": 13, "revisao": False, "prioritaria": True, "assuntos": ["★ Semântica e significação das palavras"], "chaves": ["semantica e significacao das palavras"]},
            {"numero": 14, "revisao": False, "prioritaria": False, "assuntos": ["Coesão e coerência", "Tipos e gêneros textuais"], "chaves": ["coesao e coerencia", "tipos e generos textuais"]},
            {"numero": 15, "revisao": False, "prioritaria": True, "assuntos": ["★ Análise e reescrita de frases"], "chaves": ["analise e reescritura de frases"]},
            {"numero": 16, "revisao": False, "prioritaria": False, "assuntos": ["Discurso direto e indireto", "Figuras de linguagem"], "chaves": ["discurso direto e indireto", "figuras de linguagem"]},
            {"numero": 17, "revisao": False, "prioritaria": False, "assuntos": ["Manual de Redação da Presidência da República (Redação Oficial - até a página 48)"], "chaves": ["redacao oficial"]},
            {"numero": 18, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 3. Direito do Trabalho (DT) - 23 Metas
    {
        "sigla": "DT",
        "disciplina": "Direito do Trabalho",
        "arquivo_alvo": "Direito do Trabalho_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": False, "assuntos": ["Conceito e Fontes", "Princípios do Direito do Trabalho"], "chaves": ["conceito e fontes do direito do trabalho", "principios do direito do trabalho"]},
            {"numero": 2, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da Constituição (arts. 6º a 11)", "Direitos Constitucionais dos Trabalhadores"], "chaves": ["direitos constitucionais dos trabalhadores"]},
            {"numero": 3, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 1º a 12)", "Relação de Trabalho e Relação de Emprego", "Empregador - Grupo Econômico - Sucessão - Sócio Retirante - Terceirização"], "chaves": ["relacao de trabalho e relacao de emprego", "empregador, grupo economico"]},
            {"numero": 4, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 442 a 456-A)", "Contrato de Trabalho - Características - Prazo Determinado - Trabalho Intermitente"], "chaves": ["caracteristicas, prazo determinado, trabalho intermitente"]},
            {"numero": 5, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 6, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 468 a 470) - Alteração do Contrato", "Leitura da CLT (arts. 471 a 476-A) - Suspensão e Interrupção do Contrato"], "chaves": ["alteracao do contrato", "suspensao e interrupcao do contrato"]},
            {"numero": 7, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 477 a 486)", "★ Extinção do Contrato - Obrigações do empregador - Justa causa", "★ Rescisão indireta - Culpa recíproca - Distrato ou acordo - Tabela de verbas rescisórias"], "chaves": ["formas de extincao e verbas rescisorias"]},
            {"numero": 8, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 487 a 491)", "★ Aviso Prévio"], "chaves": ["aviso previo"]},
            {"numero": 9, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 10, "revisao": False, "prioritaria": True, "assuntos": ["★ Estabilidade da Gestante", "★ CIPA e outros casos de estabilidade"], "chaves": ["estabilidade da gestante"]},
            {"numero": 11, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 57 a 75)", "★ Jornada de Trabalho - Horas in itinere - Tempo à disposição", "★ Horas extras - Compensação - Banco de horas - Jornada 12x36", "★ Períodos de descanso - Intervalos - DSR", "Trabalho noturno - Quadro de horário - Registro de ponto"], "chaves": ["jornada, horas extras, intervalos, trabalho noturno"]},
            {"numero": 12, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 75-A a 75-F) - Teletrabalho", "★ Leitura da CLT (arts. 129 a 149) - Férias"], "chaves": ["teletrabalho", "ferias"]},
            {"numero": 13, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 14, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 76 a 128) - Salário mínimo", "Leitura da CLT (arts. 457 a 467) - Salário e Remuneração - Gorjetas - Salário in natura", "13º salário - Pagamento - Descontos salariais"], "chaves": ["salario minimo", "salario e remuneracao, gorjetas"]},
            {"numero": 15, "revisao": False, "prioritaria": True, "assuntos": ["★ Equiparação salarial", "★ Leitura da CLT (arts. 189 a 197)", "★ Insalubridade e periculosidade"], "chaves": ["equiparacao salarial", "adicionais de insalubridade e periculosidade"]},
            {"numero": 16, "revisao": False, "prioritaria": False, "assuntos": ["Fundo de Garantia do Tempo de Serviço - FGTS"], "chaves": ["fundo de garantia por tempo de servico"]},
            {"numero": 17, "revisao": False, "prioritaria": False, "assuntos": ["Convenção OIT nº 87", "Organização sindical (arts. 511 a 514)", "Leitura da CLT (arts. 611 a 625) - Negociações coletivas (ACT e CCT)"], "chaves": ["negociacoes coletivas"]},
            {"numero": 18, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 19, "revisao": False, "prioritaria": False, "assuntos": ["Prescrição e Decadência", "Proteção do trabalho da mulher (arts. 372 a 401)"], "chaves": ["prescricao e decadencia", "protecao do trabalho da mulher"]},
            {"numero": 20, "revisao": False, "prioritaria": False, "assuntos": ["Proteção do trabalho do menor (arts. 402 a 441)", "Leitura da CLT (arts. 625-A a 625-H) - Comissões de Conciliação Prévia", "Leitura da CLT (arts. 223-A a 223-G) - Indenização por dano moral (extrapatrimonial)"], "chaves": ["protecao do trabalho do menor", "comissoes de conciliacao previa", "indenizacao por dano moral"]},
            {"numero": 21, "revisao": False, "prioritaria": False, "assuntos": ["Lei nº 7.783 - Greve e atividades essenciais", "Lei nº 6.019 - Trabalho Temporário e Terceirização", "Lei nº 12.023 - Trabalho Avulso Não Portuário"], "chaves": []},
            {"numero": 22, "revisao": False, "prioritaria": True, "assuntos": ["★ Compilado de jurisprudência trabalhista"], "chaves": ["jurisprudencia relativa ao direito do trabalho"]},
            {"numero": 23, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 4. Direito Administrativo (DA) - 24 Metas UNIFICADAS (Doutrina + Legislação)
    {
        "sigla": "DA",
        "disciplina": "Direito Administrativo",
        "arquivo_alvo": "Direito Administrativo_COMPLETO.html",
        "metas": [
            # Doutrina (Metas 1 a 6)
            {"numero": 1, "subtitulo": "Doutrina", "revisao": False, "prioritaria": False, "assuntos": ["Conceito de Direito Administrativo e Administração Pública", "Princípios explícitos ou expressos", "Princípios implícitos"], "chaves": ["conceitos e principios explicitos e implicitos"]},
            {"numero": 2, "subtitulo": "Doutrina", "revisao": False, "prioritaria": True, "assuntos": ["★ Poderes administrativos"], "chaves": ["poderes administrativos"]},
            {"numero": 3, "subtitulo": "Doutrina", "revisao": False, "prioritaria": True, "assuntos": ["★ Atos administrativos (parte 1)"], "chaves": ["atos administrativos"]},
            {"numero": 4, "subtitulo": "Doutrina", "revisao": False, "prioritaria": True, "assuntos": ["★ Atos administrativos (parte 2)"], "chaves": ["atos administrativos"]},
            {"numero": 5, "subtitulo": "Doutrina", "revisao": False, "prioritaria": False, "assuntos": ["Controle da Administração Pública", "Controle externo e procedimentos de tomada de contas", "Responsabilidade civil do Estado", "Bens públicos"], "chaves": ["controle da administracao publica", "controle externo e procedimentos de tomada de contas"]},
            {"numero": 6, "subtitulo": "Doutrina", "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            
            # Legislação (Metas 7 a 24)
            {"numero": 7, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["Agentes públicos", "★ Regime dos servidores públicos (Lei nº 8.112) - arts. 1º a 39", "★ Regime dos servidores públicos (Lei nº 8.112) - arts. 40 a 80"], "chaves": ["agentes publicos", "regime dos servidores publicos (lei nº 8.112)"]},
            {"numero": 8, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Regime dos servidores públicos (Lei nº 8.112) - arts. 81 a 115", "★ Regime dos servidores públicos (Lei nº 8.112) - arts. 116 a 142"], "chaves": ["regime dos servidores publicos (lei nº 8.112)"]},
            {"numero": 9, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Regime dos servidores públicos (Lei nº 8.112) - arts. 143 a 253"], "chaves": ["regime dos servidores publicos (lei nº 8.112)"]},
            {"numero": 10, "subtitulo": "Legislação", "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 11, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Licitações (Lei nº 14.133) - arts. 1º a 17"], "chaves": ["licitacoes e contratos (lei nº 14.133/2021)"]},
            {"numero": 12, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Licitações (Lei nº 14.133) - arts. 18 a 71"], "chaves": ["licitacoes e contratos (lei nº 14.133/2021)"]},
            {"numero": 13, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Licitações (Lei nº 14.133) - arts. 72 a 88"], "chaves": ["licitacoes e contratos (lei nº 14.133/2021)"]},
            {"numero": 14, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Contratos Administrativos (Lei nº 14.133) - arts. 89 a 154"], "chaves": ["licitacoes e contratos (lei nº 14.133/2021)"]},
            {"numero": 15, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Contratos Administrativos (Lei nº 14.133) - arts. 155 a 194"], "chaves": ["licitacoes e contratos (lei nº 14.133/2021)"]},
            {"numero": 16, "subtitulo": "Legislação", "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 17, "subtitulo": "Legislação", "revisao": False, "prioritaria": False, "assuntos": ["Decreto nº 11.531 - Convênios", "Parcerias com as organizações da sociedade civil (Lei nº 13.019)"], "chaves": []},
            {"numero": 18, "subtitulo": "Legislação", "revisao": False, "prioritaria": False, "assuntos": ["Serviços públicos", "Concessão e permissão (Lei nº 8.987)", "Parcerias público-privadas (Lei nº 11.079)", "Direitos dos usuários (Lei nº 13.460)"], "chaves": []},
            {"numero": 19, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Processo administrativo (Lei nº 9.784)"], "chaves": ["processo administrativo federal (lei nº 9.784)"]},
            {"numero": 20, "subtitulo": "Legislação", "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 21, "subtitulo": "Legislação", "revisao": False, "prioritaria": True, "assuntos": ["★ Improbidade administrativa (Lei nº 8.429)"], "chaves": ["improbidade administrativa (lei nº 8.429)"]},
            {"numero": 22, "subtitulo": "Legislação", "revisao": False, "prioritaria": False, "assuntos": ["Decreto-Lei nº 4.657 - LINDB", "Lei nº 11.416 - Plano de Carreira no Judiciário Federal", "Lei nº 12.527 - Lei de Acesso à Informação - LAI"], "chaves": ["lei de introducao as normas do direito brasileiro", "lei nº 11.416 - plano de carreira no judiciario federal"]},
            {"numero": 23, "subtitulo": "Legislação", "revisao": False, "prioritaria": False, "assuntos": ["Lei nº 13.709 - Lei Geral de Proteção de Dados (LGPD)", "Lei nº 13.869 - Abuso de Autoridade"], "chaves": ["lei de abuso de autoridade (lei nº 13.869)"]},
            {"numero": 24, "subtitulo": "Legislação", "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 5. Matemática e Raciocínio Lógico (RLM) - 13 Metas
    {
        "sigla": "RLM",
        "disciplina": "Matemática e Raciocínio Lógico",
        "arquivo_alvo": "Matematica e Rlm_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": True, "assuntos": ["★ Conjuntos numéricos e operações básicas"], "chaves": ["conjuntos numericos e operacoes basicas"]},
            {"numero": 2, "revisao": False, "prioritaria": False, "assuntos": ["Múltiplos e divisores - MMC e MDC"], "chaves": ["multiplos e divisores, mmc e mdc"]},
            {"numero": 3, "revisao": False, "prioritaria": True, "assuntos": ["★ Frações e números decimais"], "chaves": ["fracoes e numeros decimais"]},
            {"numero": 4, "revisao": False, "prioritaria": True, "assuntos": ["★ Equações do 1º grau - Sistema de equações do 1º grau"], "chaves": ["equacoes do 1º grau e sistema de equacoes"]},
            {"numero": 5, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 6, "revisao": False, "prioritaria": True, "assuntos": ["★ Proporcionalidade e regra de três simples"], "chaves": ["proporcionalidade e regra de tres simples"]},
            {"numero": 7, "revisao": False, "prioritaria": True, "assuntos": ["★ Porcentagem"], "chaves": ["porcentagem"]},
            {"numero": 8, "revisao": False, "prioritaria": False, "assuntos": ["Noções de estatística - Média - Mediana - Moda - Amplitude - Desvio - Variância", "Interpretação de gráficos e tabelas"], "chaves": ["media, mediana, moda", "interpretacao de graficos e tabelas"]},
            {"numero": 9, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 10, "revisao": False, "prioritaria": False, "assuntos": ["Raciocínio lógico proposicional - Tabela-verdade - Negação - Equivalência"], "chaves": ["raciocinio logico proposicional"]},
            {"numero": 11, "revisao": False, "prioritaria": True, "assuntos": ["★ Lógica geral e associação de informações"], "chaves": ["logica geral e associacao de informacoes"]},
            {"numero": 12, "revisao": False, "prioritaria": False, "assuntos": ["Diagramas lógicos - Diagramas de Venn"], "chaves": ["diagramas logicos"]},
            {"numero": 13, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 6. Direito Processual do Trabalho (DPT) - 19 Metas
    {
        "sigla": "DPT",
        "disciplina": "Direito Processual do Trabalho",
        "arquivo_alvo": "Processo do Trabalho_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": False, "assuntos": ["Organização da Justiça do Trabalho", "Competência da Justiça do Trabalho"], "chaves": ["organizacao e competencia da justica do trabalho"]},
            {"numero": 2, "revisao": False, "prioritaria": False, "assuntos": ["Ministério Público do Trabalho - MPT"], "chaves": []},
            {"numero": 3, "revisao": False, "prioritaria": False, "assuntos": ["Fontes", "Princípios gerais", "Princípios comuns ao DPC e ao DPT", "Princípios peculariares ao DPT"], "chaves": ["fontes e principios"]},
            {"numero": 4, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 763 a 788) - Atos - Termos - Prazos - Distribuição", "Leitura da CLT (arts. 789 a 790-B) - Custas e Emolumentos"], "chaves": ["atos, termos, prazos e distribuicao", "custas e emolumentos"]},
            {"numero": 5, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 6, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 791 a 793-D)", "★ Partes e Procuradores"], "chaves": ["partes e procuradores"]},
            {"numero": 7, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 794 a 798) - Nulidades", "Leitura da CLT (arts. 799 a 802) - Exceções", "Leitura da CLT (arts. 813 a 817) - Audiências"], "chaves": ["audiencias"]},
            {"numero": 8, "revisao": False, "prioritaria": False, "assuntos": ["Leitura da CLT (arts. 818 a 830) - Provas", "Leitura da CLT (arts. 831 a 836) - Decisão"], "chaves": []},
            {"numero": 9, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 10, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 837 a 852-I)", "★ Dissídios Individuais", "★ Procedimento Sumaríssimo"], "chaves": ["dissidios individuais"]},
            {"numero": 11, "revisao": False, "prioritaria": False, "assuntos": ["Incidente de Desconsideração da Personalidade Jurídica", "Inquérito para Apuração de Falta Grave", "Ação Rescisória", "Mandado de Segurança", "Ação Civil Pública", "Dissidios coletivos e sentença normativa"], "chaves": []},
            {"numero": 12, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 876 a 892)", "★ Execução", "Execução contra a Fazenda Pública", "Lei nº 8.009 - Impenhorabilidade do bem de família"], "chaves": ["execucao (iniciativa, liquidacao, penhora"]},
            {"numero": 13, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 14, "revisao": False, "prioritaria": True, "assuntos": ["★ Leitura da CLT (arts. 893 a 902)", "★ Teoria geral dos recursos"], "chaves": ["teoria geral dos recursos"]},
            {"numero": 15, "revisao": False, "prioritaria": True, "assuntos": ["★ Embargos no TST", "★ Recurso ordinário", "★ Recurso de revista", "★ Agravos", "★ Embargos de declaração e recurso adesivo"], "chaves": ["recursos em especie"]},
            {"numero": 16, "revisao": False, "prioritaria": False, "assuntos": ["Lei nº 11.419 - Informatização do processo judicial", "Resolução CNJ nº 185 - PJE", "Resolução CSJT nº 185 - PJE"], "chaves": ["lei nº 11.419 - informatizacao do processo judicial"]},
            {"numero": 17, "revisao": False, "prioritaria": False, "assuntos": ["Instrução Normativa TST nº 38", "Instrução Normativa TST nº 39", "Instrução Normativa TST nº 40"], "chaves": []},
            {"numero": 18, "revisao": False, "prioritaria": True, "assuntos": ["★ Compilado de jurisprudência processual trabalhista"], "chaves": ["jurisprudencia relativa ao processo do trabalho"]},
            {"numero": 19, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 7. Direitos Humanos (DH) - 19 Metas
    {
        "sigla": "DH",
        "disciplina": "Direitos Humanos",
        "arquivo_alvo": "Direitos Humanos_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": False, "assuntos": ["Conceito - Classificação - Características dos Direitos Humanos", "Evolução histórica dos Direitos Humanos", "Dimensões dos Direitos Humanos"], "chaves": ["conceito, classificacao e caracteristicas dos direitos humanos", "evolucao historica dos direitos humanos"]},
            {"numero": 2, "revisao": False, "prioritaria": True, "assuntos": ["★ Direitos Humanos e Constituição Federal"], "chaves": []},
            {"numero": 3, "revisao": False, "prioritaria": True, "assuntos": ["★ Declaração Universal dos Direitos Humanos - DUDH"], "chaves": ["declaracao universal dos direitos humanos", "dudh"]},
            {"numero": 4, "revisao": False, "prioritaria": True, "assuntos": ["★ Pacto Internacional dos Direitos Civis e Políticos - PIDCP"], "chaves": ["pacto internacional dos direitos civis e politicos - pidcp"]},
            {"numero": 5, "revisao": False, "prioritaria": False, "assuntos": ["Pacto Internacional dos Direitos Econômicos Sociais e Culturais - PIDESC"], "chaves": ["pacto internacional dos direitos economicos sociais e culturais - pidesc"]},
            {"numero": 6, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 7, "revisao": False, "prioritaria": True, "assuntos": ["★ Convenção Americana sobre Direitos Humanos - CADH (Pacto de São José da Costa Rica)", "★ Protocolo adicional à Convenção Americana sobre Direitos Humanos (Protocolo de San Salvador)"], "chaves": ["convencao americana sobre direitos humanos - cadh", "protocolo adicional a convencao americana"]},
            {"numero": 8, "revisao": False, "prioritaria": False, "assuntos": ["Grupos vulneráveis e minorias", "Convenção sobre a eliminação de todas as formas de discriminação racial"], "chaves": ["grupos vulneraveis e minorias", "convencao sobre a eliminacao de todas as formas de discriminacao racial"]},
            {"numero": 9, "revisao": False, "prioritaria": False, "assuntos": ["Convenção sobre a eliminação de todas as formas de discriminação contra a mulher"], "chaves": ["convencao sobre a eliminacao de todas as formas de discriminacao contra a mulher"]},
            {"numero": 10, "revisao": False, "prioritaria": False, "assuntos": ["Convenção sobre os direitos da criança"], "chaves": ["convencao sobre os direitos da crianca"]},
            {"numero": 11, "revisao": False, "prioritaria": True, "assuntos": ["★ Convenção sobre os direitos da pessoa com deficiência"], "chaves": ["convencao sobre os direitos da pessoa com deficiencia"]},
            {"numero": 12, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 13, "revisao": False, "prioritaria": False, "assuntos": ["Declaração das Nações Unidas sobre os direitos dos povos indígenas", "Resolução CSJT nº 368", "Resolução CNJ nº 492"], "chaves": ["declaracao das nacoes unidas sobre os direitos dos povos indigenas", "resolucao cnj nº 492"]},
            {"numero": 14, "revisao": False, "prioritaria": False, "assuntos": ["Mecanismos de proteção aos Direitos Humanos", "Convenção relativa à proteção do patrimônio (Declaração de Estocolmo)"], "chaves": ["mecanismos de protecao aos direitos humanos"]},
            {"numero": 15, "revisao": False, "prioritaria": False, "assuntos": ["Convenção sobre a diversidade biológica", "Declaração Americana dos Direitos e Deveres do Homem"], "chaves": []},
            {"numero": 16, "revisao": False, "prioritaria": False, "assuntos": ["Tribunal Penal Internacional (Estatuto de Roma)"], "chaves": ["tribunal penal internacional (estatuto de roma)"]},
            {"numero": 17, "revisao": False, "prioritaria": False, "assuntos": ["Carta das Nações Unidas (Estatuto da Corte Internacional de Justiça)"], "chaves": ["carta das nacoes unidas (estatuto da corte internacional de justica)"]},
            {"numero": 18, "revisao": False, "prioritaria": False, "assuntos": ["Protocolos para Atuação e Julgamento na Justiça do Trabalho"], "chaves": ["protocolos para atuacao e julgamento na justica do trabalho"]},
            {"numero": 19, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 8. Administração e Gestão de Pessoas (ADM) - 17 Metas
    {
        "sigla": "ADM",
        "disciplina": "Administração e Gestão de Pessoas",
        "arquivo_alvo": "Administração_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": True, "assuntos": ["Conceitos introdutórios", "★ Teorias de administração", "Funções da administração"], "chaves": ["conceitos introdutorios", "teorias de administracao", "funcoes da administracao"]},
            {"numero": 2, "revisao": False, "prioritaria": True, "assuntos": ["★ Conceito e níveis de planejamento", "★ Missão - Visão - Valores - Análise SWOT", "★ Balanced Scorecard - BSC e OKR"], "chaves": ["missao, visao, valores, swot, bsc, okr"]},
            {"numero": 3, "revisao": False, "prioritaria": True, "assuntos": ["★ Organização - Estrutura - Organograma", "★ Tipos de organização e modelos estruturais", "★ Departamentalização"], "chaves": ["organizacao, estrutura e departamentalizacao"]},
            {"numero": 4, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 5, "revisao": False, "prioritaria": False, "assuntos": ["Comportamento - Cultura - Clima - Mudança"], "chaves": ["comportamento, cultura, clima e mudanca organizacional"]},
            {"numero": 6, "revisao": False, "prioritaria": True, "assuntos": ["★ Liderança"], "chaves": ["lideranca"]},
            {"numero": 7, "revisao": False, "prioritaria": True, "assuntos": ["★ Motivação"], "chaves": ["motivacao"]},
            {"numero": 8, "revisao": False, "prioritaria": True, "assuntos": ["★ Controle", "★ Gestão da qualidade"], "chaves": ["controle", "gestao da qualidade"]},
            {"numero": 9, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 10, "revisao": False, "prioritaria": True, "assuntos": ["Convergências e diferenças (gestão pública x gestão privada)", "★ Excelência nos serviços públicos - Gestão por resultados", "Gestão de contratos"], "chaves": ["convergencias e diferencas (gestao publica x gestao privada)", "excelencia nos servicos publicos e gestao por resultados", "gestao de contratos"]},
            {"numero": 11, "revisao": False, "prioritaria": True, "assuntos": ["★ Gestão de pessoas"], "chaves": ["gestao de pessoas"]},
            {"numero": 12, "revisao": False, "prioritaria": True, "assuntos": ["★ Gestão de desempenho e avaliação de desempenho", "Gestão por competências e mapeamento de competências"], "chaves": ["gestao de desempenho", "gestao por competencias"]},
            {"numero": 13, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 14, "revisao": False, "prioritaria": False, "assuntos": ["Gestão de processos"], "chaves": ["gestao de processos"]},
            {"numero": 15, "revisao": False, "prioritaria": False, "assuntos": ["Gestão de projetos e gestão de riscos"], "chaves": ["gestao de projetos e gestao de riscos"]},
            {"numero": 16, "revisao": False, "prioritaria": False, "assuntos": ["Comunicação", "Processo decisório"], "chaves": ["comunicacao", "processo decisorio"]},
            {"numero": 17, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    },

    # 9. Informática (INFO) - 12 Metas
    {
        "sigla": "INFO",
        "disciplina": "Informática",
        "arquivo_alvo": "Informática_COMPLETO.html",
        "metas": [
            {"numero": 1, "revisao": False, "prioritaria": True, "assuntos": ["★ Sistema operacional Windows"], "chaves": ["windows, arquivos e pastas"]},
            {"numero": 2, "revisao": False, "prioritaria": True, "assuntos": ["★ Gerenciamento de arquivos e pastas"], "chaves": ["windows, arquivos e pastas"]},
            {"numero": 3, "revisao": False, "prioritaria": False, "assuntos": ["Microsoft 365 - OneDrive - OneNote - Teams - Outlook - Powerpoint"], "chaves": ["microsoft 365"]},
            {"numero": 4, "revisao": False, "prioritaria": True, "assuntos": ["★ Word"], "chaves": ["word"]},
            {"numero": 5, "revisao": False, "prioritaria": True, "assuntos": ["★ Excel"], "chaves": ["excel"]},
            {"numero": 6, "revisao": False, "prioritaria": True, "assuntos": ["★ Google Workspace - Docs - Sheets - Slides - Gmail - Calendar - Meet"], "chaves": ["google workspace"]},
            {"numero": 7, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []},
            {"numero": 8, "revisao": False, "prioritaria": False, "assuntos": ["Redes de computadores - Internet e intranet - Protocolos - Computação em nuvem"], "chaves": ["redes de computadores, internet e intranet"]},
            {"numero": 9, "revisao": False, "prioritaria": True, "assuntos": ["★ Navegadores - Google Chrome - Mozilla Firefox - Microsoft Edge"], "chaves": ["navegadores"]},
            {"numero": 10, "revisao": False, "prioritaria": False, "assuntos": ["Pesquisa na internet - Redes sociais - Grupos de discussão"], "chaves": ["pesquisa na internet, redes sociais e grupos de discussao"]},
            {"numero": 11, "revisao": False, "prioritaria": True, "assuntos": ["★ Segurança da informação - Malwares - Antivírus - Firewall - Backup"], "chaves": ["malwares, antivirus, firewall, backup"]},
            {"numero": 12, "revisao": True, "prioritaria": False, "assuntos": ["Revisão"], "chaves": []}
        ]
    }
]

# ==============================================================================
# DISCIPLINAS OFICIAIS DO PDF PENDENTES DE ARQUIVO HTML (CIVIL, PROC. CIVIL, LEGISLAÇÃO)
# Quando o usuário adicionar o arquivo HTML correspondente na pasta METAS,
# a plataforma o reconhecerá AUTOMATICAMENTE com as metas, revisões e prioridades do PDF oficial!
# ==============================================================================
CATALOGO_PENDENTES_PDF = json.loads(r'''{
  "CIV": {
    "sigla": "CIV",
    "disciplina": "Direito Civil",
    "arquivo_alvo": "Direito Civil_COMPLETO.html",
    "metas": [
      {
        "numero": 1,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Pessoas naturais (arts. 1º ao 39)"
        ],
        "chaves": [
          "pessoas naturais"
        ]
      },
      {
        "numero": 2,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Pessoas jurídicas (arts. 40 a 69)"
        ],
        "chaves": [
          "pessoas jurídicas"
        ]
      },
      {
        "numero": 3,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Domicílio (arts. 70 a 78)",
          "Bens (arts. 79 a 103)"
        ],
        "chaves": [
          "domicílio"
        ]
      },
      {
        "numero": 4,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Fatos jurídicos - Negócio jurídico - Atos jurídicos lícitos e ilícitos (arts. 104 a 188)"
        ],
        "chaves": [
          "fatos jurídicos"
        ]
      },
      {
        "numero": 5,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Prescrição e decadência (arts. 189 a 211)",
          "Prova dos fatos jurídicos (arts. 212 a 232)"
        ],
        "chaves": [
          "prescrição e decadência",
          "prova dos fatos jurídicos"
        ]
      },
      {
        "numero": 6,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 7,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Direito das obrigações (arts. 233 a 420)"
        ],
        "chaves": [
          "direito das obrigações"
        ]
      },
      {
        "numero": 8,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Contratos em geral (arts. 421 a 480)"
        ],
        "chaves": [
          "contratos em geral"
        ]
      },
      {
        "numero": 9,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Contratos em espécie - Compra e venda - Doação - Locação - Empréstimo (arts. 481 a 592)"
        ],
        "chaves": [
          "contratos em espécie"
        ]
      },
      {
        "numero": 10,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Contratos em espécie - Prestação de serviço - Empreitada - Depósito - Mandato",
          "(arts. 593 a 756)",
          "Contratos em espécie - Fiança - Transação (arts. 803 a 853)"
        ],
        "chaves": [
          "contratos em espécie"
        ]
      },
      {
        "numero": 11,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Responsabilidade civil (arts. 927 a 954)",
          "Direito de empresa - Nome empresarial (arts. 1.155 a 1.168)"
        ],
        "chaves": [
          "responsabilidade civil",
          "direito de empresa"
        ]
      },
      {
        "numero": 12,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 13,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Direito das coisas - Posse (arts. 1.196 a 1.224)"
        ],
        "chaves": [
          "direito das coisas"
        ]
      },
      {
        "numero": 14,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Direitos reais - Propriedade - Aquisição - Perda (arts. 1.225 a 1.276)",
          "Direitos de vizinhança (arts. 1.277 a 1.313)",
          "Condomínio geral - Condomínio edilício (arts. 1.314 a 1.358-A)",
          "Condomínio em multipropriedade - Propriedade resolúvel - Propriedade fiduciária - Fundo de",
          "investimento (arts. 1.358-B a 1.368-F)"
        ],
        "chaves": [
          "direitos reais",
          "direitos de vizinhança",
          "condomínio geral",
          "condomínio em multipropriedade",
          "investimento"
        ]
      },
      {
        "numero": 15,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Direitos reais de gozo ou fruição - Superfície - Servidões - Usufruto - Uso - Habitação - Direito do",
          "promitente comprador (arts. 1.369 a 1.418)",
          "Direitos reais sobre a coisa alheia - Penhor - Hipoteca - Anticrese - Laje (arts. 1.419 a 1.510-E)"
        ],
        "chaves": [
          "direitos reais de gozo ou fruição",
          "promitente comprador",
          "direitos reais sobre a coisa alheia"
        ]
      },
      {
        "numero": 16,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 17,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Direito de família - Direito pessoal - Casamento - Relações de parentesco (arts. 1.511 a 1.638)"
        ],
        "chaves": [
          "direito de família"
        ]
      },
      {
        "numero": 18,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Direito patrimonial - Regime de bens entre os cônjuges (arts. 1.639 a 1.688)",
          "Alimentos - Bem de família - União estável - Tutela e curatela (arts. 1.689 a 1.783-A)"
        ],
        "chaves": [
          "direito patrimonial",
          "alimentos"
        ]
      },
      {
        "numero": 19,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Direitos das sucessões - Sucessão em geral - Sucessão legítima - Sucessão testamentária",
          "(arts. 1.784 a 1.990)",
          "Inventário e partilha (arts. 1.991 a 2.027)"
        ],
        "chaves": [
          "direitos das sucessões",
          "inventário e partilha"
        ]
      },
      {
        "numero": 20,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      }
    ]
  },
  "DPC": {
    "sigla": "DPC",
    "disciplina": "Direito Processual Civil",
    "arquivo_alvo": "Direito Processual Civil_COMPLETO.html",
    "metas": [
      {
        "numero": 1,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Conceito de Direito Processual Civil",
          "Leitura do CPC (arts. 1º ao 15)",
          "Princípios e aplicação das normas processuais",
          "Leitura do CPC (arts. 16 a 20)",
          "Leitura do CPC (arts. 21 a 41)",
          "Jurisdição e Ação"
        ],
        "chaves": [
          "conceito de direito processual civil",
          "leitura do cpc",
          "princípios e aplicação das normas processuais",
          "jurisdição e ação"
        ]
      },
      {
        "numero": 2,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Leitura do CPC (arts. 42 a 69)",
          "★ Competência"
        ],
        "chaves": [
          "leitura do cpc",
          "competência"
        ]
      },
      {
        "numero": 3,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Sujeitos do processo - Pressupostos - Capacidade - Partes e Procuradores - Gratuidade da",
          "Justiça (arts. 70 a 112)"
        ],
        "chaves": [
          "sujeitos do processo",
          "justiça"
        ]
      },
      {
        "numero": 4,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Litisconsórcio (arts. 113 a 118)",
          "Intervenção de terceiros (arts. 119 a 138)"
        ],
        "chaves": [
          "litisconsórcio",
          "intervenção de terceiros"
        ]
      },
      {
        "numero": 5,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 6,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Juiz - Impedimento e Suspeição - Auxiliares da Justiça - Mediação e Conciliação",
          "(arts. 139 a 175)",
          "Ministério Público - Advocacia Pública - Defensoria Pública (arts. 176 a 187)"
        ],
        "chaves": [
          "ministério público"
        ]
      },
      {
        "numero": 7,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Atos processuais - Forma - Tempo - Lugar - Prazos (arts. 188 a 235)"
        ],
        "chaves": [
          "atos processuais"
        ]
      },
      {
        "numero": 8,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Comunicação dos atos processuais (arts. 236 a 275)",
          "Nulidades - Distribuição e registro - Valor da causa (arts. 276 a 293)"
        ],
        "chaves": [
          "comunicação dos atos processuais",
          "nulidades"
        ]
      },
      {
        "numero": 9,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Tutela provisória (arts. 294 a 311)",
          "Formação - Suspensão - Extinção do processo (arts. 312 a 317)"
        ],
        "chaves": [
          "tutela provisória",
          "formação"
        ]
      },
      {
        "numero": 10,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 11,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Processo de conhecimento - Procedimento comum - Petição inicial - Contestação",
          "(arts. 318 a 368)"
        ],
        "chaves": [
          "processo de conhecimento"
        ]
      },
      {
        "numero": 12,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Provas (arts. 369 a 484)"
        ],
        "chaves": [
          "provas"
        ]
      },
      {
        "numero": 13,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Sentença e coisa julgada - Liquidação de sentença (arts. 485 a 512)",
          "Cumprimento de sentença (arts. 513 a 538)"
        ],
        "chaves": [
          "sentença e coisa julgada",
          "cumprimento de sentença"
        ]
      },
      {
        "numero": 14,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Ação de consignação em pagamento (arts. 539 a 549)",
          "Ações possessórias (arts. 554 a 568)",
          "Embargos de terceiro (arts. 674 a 681)",
          "Ação monitória (arts. 700 a 702)"
        ],
        "chaves": [
          "ação de consignação em pagamento",
          "ações possessórias",
          "embargos de terceiro",
          "ação monitória"
        ]
      },
      {
        "numero": 15,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 16,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "Execução em geral (arts. 771 a 796)",
          "★ Diversas espécies de execução (arts. 797 a 913)"
        ],
        "chaves": [
          "execução em geral",
          "diversas espécies de execução"
        ]
      },
      {
        "numero": 17,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Embargos à execução (arts. 914 a 920)",
          "Suspensão e extinção do processo de execução (arts. 921 a 925)",
          "Ação rescisória (arts. 966 a 975)"
        ],
        "chaves": [
          "embargos à execução",
          "suspensão e extinção do processo de execução",
          "ação rescisória"
        ]
      },
      {
        "numero": 18,
        "revisao": false,
        "prioritaria": true,
        "assuntos": [
          "★ Recursos - Disposições gerais (arts. 994 a 1.008)",
          "★ Apelação (arts. 1.009 a 1.014)",
          "★ Agravo de instrumento (arts. 1.015 a 1.020)",
          "Agravo interno (art. 1.021)",
          "Embargos de declaração (arts. 1.022 a 1.026)",
          "Recursos para o STF e STJ (arts. 1.027 a 1.044)"
        ],
        "chaves": [
          "recursos",
          "apelação",
          "agravo de instrumento",
          "agravo interno",
          "embargos de declaração",
          "recursos para o stf e stj"
        ]
      },
      {
        "numero": 19,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Lei nº 7.347 - Ação Civil Pública",
          "Lei nº 9.099 - Juizados Especiais Cíveis",
          "Lei nº 12.016 - Mandado de Segurança",
          "Lei nº 13.140 - Mediação"
        ],
        "chaves": [
          "lei nº 7.347",
          "lei nº 9.099",
          "lei nº 12.016",
          "lei nº 13.140"
        ]
      },
      {
        "numero": 20,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      }
    ]
  },
  "LEG": {
    "sigla": "LEG",
    "disciplina": "Legislação Específica (TRT-7)",
    "arquivo_alvo": "Legislação_COMPLETO.html",
    "metas": [
      {
        "numero": 1,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Noções de Sustentabilidade (Resolução CNJ nº 400)"
        ],
        "chaves": [
          "noções de sustentabilidade",
          "resolução cnj nº 400"
        ]
      },
      {
        "numero": 2,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Resolução CNJ nº 351 (Política de Prevenção e Enfrentamento do Assédio e da Discriminação)"
        ],
        "chaves": [
          "resolução csjt nº 360",
          "resolução cnj nº 351",
          "assédio"
        ]
      },
      {
        "numero": 3,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Resolução CSJT nº 360 (Política de Prevenção e Enfrentamento no âmbito da Justiça do Trabalho)"
        ],
        "chaves": [
          "resolução csjt nº 360"
        ]
      },
      {
        "numero": 4,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão"
        ],
        "chaves": []
      },
      {
        "numero": 5,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Código de Conduta e Valores Éticos do TRT-7 (Portaria GP TRT-7 nº 4.573)"
        ],
        "chaves": [
          "código de conduta e valores éticos do trt",
          "portaria gp trt-4 nº 4.573"
        ]
      },
      {
        "numero": 6,
        "revisao": false,
        "prioritaria": false,
        "assuntos": [
          "Regimento Interno do TRT-7"
        ],
        "chaves": [
          "regimento interno do trt"
        ]
      },
      {
        "numero": 7,
        "revisao": true,
        "prioritaria": false,
        "assuntos": [
          "Revisão Final"
        ],
        "chaves": []
      }
    ]
  }
}''')

DISCIPLINAS_AUSENTES_PDF = [
    {"sigla": "CIV", "nome": "Direito Civil", "metas_qtd": 20, "motivo": "Arquivo HTML não encontrado na pasta METAS"},
    {"sigla": "DPC", "nome": "Direito Processual Civil", "metas_qtd": 20, "motivo": "Arquivo HTML não encontrado na pasta METAS"},
    {"sigla": "LEG", "nome": "Legislação Específica (TRT-7)", "metas_qtd": 8, "motivo": "Arquivo HTML não encontrado na pasta METAS"}
]

def detectar_novas_disciplinas(metas_dir, catalogo_existente, ausentes_lista):
    """Varre a pasta METAS em busca de arquivos HTML novos adicionados pelo usuário.
    1. Se o arquivo for uma das disciplinas oficiais do PDF que faltavam (Civil, Processo Civil, Legislação),
       ele é reconhecido EXATAMENTE conforme o PDF oficial de metas (com todas as metas, revisões, estrelas
       de prioridade e assuntos do PDF). Tópicos excedentes no HTML entram como Metas Extras ao final.
    2. Se o arquivo for uma disciplina totalmente nova (ex: Direito Penal), cria automaticamente a disciplina,
       atribui sigla inteligente e distribui os tópicos com revisões periódicas estratégicas.
    """
    arquivos_conhecidos = {d.get("arquivo_alvo") for d in catalogo_existente if d.get("arquivo_alvo")}
    arquivos_ignorar = {"index.html", "plataforma_metas.html", "estudos_unificado.html"}

    novas_disciplinas = []
    ausentes_restantes = list(ausentes_lista or [])

    for arq in sorted(metas_dir.glob("*.html")):
        if arq.name.lower() in arquivos_ignorar:
            continue
        if arq.name in arquivos_conhecidos:
            continue

        conteudo = arq.read_text(encoding="utf-8", errors="ignore")
        nome_extraido, aulas = extrair_aulas_do_html(conteudo, arq.name)
        if not aulas:
            continue

        nome_disciplina = nome_extraido
        if not nome_disciplina or nome_disciplina.lower().startswith("tópico") or nome_disciplina.lower().startswith("modulo"):
            nome_disciplina = arq.stem.replace("_COMPLETO", "").replace("_", " ").strip()

        nome_norm = normalizar_texto(nome_disciplina + " " + arq.stem)

        # ----------------------------------------------------------------------
        # CASO 1: DISCIPLINA DO PDF OFICIAL (Civil, Processual Civil, Legislação)
        # ----------------------------------------------------------------------
        sigla_oficial = None
        if ("process" in nome_norm and "civil" in nome_norm) or "dpc" in nome_norm:
            sigla_oficial = "DPC"
        elif "civil" in nome_norm and "process" not in nome_norm:
            sigla_oficial = "CIV"
        elif "legisla" in nome_norm or "especifica" in nome_norm or "trt" in nome_norm:
            sigla_oficial = "LEG"

        if sigla_oficial and sigla_oficial in CATALOGO_PENDENTES_PDF:
            disc_pdf = copy.deepcopy(CATALOGO_PENDENTES_PDF[sigla_oficial])
            sigla = disc_pdf["sigla"]
            nome_disciplina = disc_pdf["disciplina"]
            metas_oficiais = disc_pdf["metas"]

            print(f"   [🌟 DISCIPLINA OFICIAL DO PDF RECONHECIDA] {nome_disciplina} ({sigla}) em {arq.name} com {len(metas_oficiais)} metas oficiais!")

            aulas_vinculadas = set()
            for m in metas_oficiais:
                m["id"] = f"{sigla.lower()}-meta-{m['numero']}"
                m["sigla"] = sigla
                m["disciplina"] = nome_disciplina
                m["aulas_conteudo"] = []
                m["extra"] = False
                if m.get("revisao"):
                    m["orientacao_revisao"] = (
                        "As metas de revisão são como paradas estratégicas para a memorização e solidificação do conhecimento. "
                        "Volte em cada tópico estudado até então na matéria, faça a revisão e acesse novamente os links para treinar com mais algumas questões. "
                        "Revisar não é reestudar. Portanto, seja prático: dê prioridade aos esquemas, aos grifos, às decorebas, aos trechos que sempre são cobrados, "
                        "aos temas em que você está inseguro ou ainda não gravou muito bem e, principalmente, àquilo que você está mais errando nas questões."
                    )
                else:
                    chaves = [normalizar_texto(c) for c in m.get("chaves", [])]
                    for chave in chaves:
                        for aula in aulas:
                            tit_norm = normalizar_texto(aula["titulo"])
                            if chave in tit_norm or tit_norm in chave:
                                if aula not in m["aulas_conteudo"]:
                                    m["aulas_conteudo"].append(aula)
                                    aulas_vinculadas.add(aula["titulo"])

            # Tópicos excedentes no HTML viram Metas Extras no final da matéria
            aulas_extras = [a for a in aulas if a["titulo"] not in aulas_vinculadas]
            ultimo_num = max([m["numero"] for m in metas_oficiais]) if metas_oficiais else 0
            for e_idx, extra_aula in enumerate(aulas_extras):
                novo_num = ultimo_num + e_idx + 1
                metas_oficiais.append({
                    "numero": novo_num,
                    "extra": True,
                    "revisao": False,
                    "prioritaria": False,
                    "subtitulo": "Meta Extra • Conteúdo Complementar do HTML",
                    "assuntos": [extra_aula["titulo"]],
                    "chaves": [],
                    "id": f"{sigla.lower()}-meta-extra-{e_idx + 1}",
                    "sigla": sigla,
                    "disciplina": nome_disciplina,
                    "aulas_conteudo": [extra_aula]
                })

            novas_disciplinas.append({
                "sigla": sigla,
                "disciplina": nome_disciplina,
                "arquivo_alvo": arq.name,
                "metas": metas_oficiais
            })

            # Remove da lista de ausentes pois agora está ativa!
            ausentes_restantes = [d for d in ausentes_restantes if d["sigla"] != sigla]
            continue

        # ----------------------------------------------------------------------
        # CASO 2: DISCIPLINA TOTALMENTE NOVA (Fora do PDF TRT-7)
        # ----------------------------------------------------------------------
        palavras = [p for p in re.findall(r'[A-Za-zÀ-ÿ]+', nome_disciplina) if len(p) > 2 and p.lower() not in {"de", "do", "da", "dos", "das", "para", "com", "em"}]
        if len(palavras) >= 2:
            sigla = "".join(p[0].upper() for p in palavras[:4])
        elif palavras:
            sigla = palavras[0][:4].upper()
        else:
            sigla = "NOVA"

        siglas_existentes = {d["sigla"] for d in catalogo_existente} | {d["sigla"] for d in novas_disciplinas}
        sigla_base = sigla
        contador = 1
        while sigla in siglas_existentes:
            sigla = f"{sigla_base}{contador}"
            contador += 1

        print(f"   [🌟 NOVA DISCIPLINA DETECTADA] {nome_disciplina} ({sigla}) em {arq.name} com {len(aulas)} tópicos")

        metas_nova = []
        meta_num = 1
        for idx, aula in enumerate(aulas):
            metas_nova.append({
                "numero": meta_num,
                "revisao": False,
                "prioritaria": ("★" in aula["titulo"] or "importante" in aula["titulo"].lower()),
                "assuntos": [aula["titulo"]],
                "chaves": [],
                "id": f"{sigla.lower()}-meta-{meta_num}",
                "sigla": sigla,
                "disciplina": nome_disciplina,
                "aulas_conteudo": [aula],
                "extra": False
            })
            meta_num += 1

            if (idx + 1) % 4 == 0 and (idx + 1) < len(aulas):
                metas_nova.append({
                    "numero": meta_num,
                    "revisao": True,
                    "prioritaria": False,
                    "assuntos": ["Revisão Estratégica"],
                    "chaves": [],
                    "id": f"{sigla.lower()}-meta-{meta_num}",
                    "sigla": sigla,
                    "disciplina": nome_disciplina,
                    "aulas_conteudo": [],
                    "extra": False,
                    "orientacao_revisao": (
                        "Parada estratégica para memorização e consolidação dos tópicos anteriores da disciplina. "
                        "Revise seus resumos, faça questões de fixação e anote os pontos de dúvida."
                    )
                })
                meta_num += 1

        metas_nova.append({
            "numero": meta_num,
            "revisao": True,
            "prioritaria": False,
            "assuntos": ["Revisão Geral da Disciplina"],
            "chaves": [],
            "id": f"{sigla.lower()}-meta-{meta_num}",
            "sigla": sigla,
            "disciplina": nome_disciplina,
            "aulas_conteudo": [],
            "extra": False,
            "orientacao_revisao": "Revisão geral de fechamento da matéria."
        })

        novas_disciplinas.append({
            "sigla": sigla,
            "disciplina": nome_disciplina,
            "arquivo_alvo": arq.name,
            "metas": metas_nova
        })

        ausentes_restantes = [
            d for d in ausentes_restantes 
            if normalizar_texto(d["nome"]) not in normalizar_texto(nome_disciplina) 
            and normalizar_texto(nome_disciplina) not in normalizar_texto(d["nome"])
        ]

    return novas_disciplinas, ausentes_restantes

def vincular_conteudo_as_metas(catalogo, metas_dir, ausentes_lista=None):
    """Vincula exatamente os tópicos do PDF com o conteúdo dos arquivos HTML da pasta METAS de forma determinística
    e cria Metas Extras para quaisquer tópicos presentes no HTML que não constem no rol oficial do PDF.
    Também detecta e inclui automaticamente novas disciplinas adicionadas na pasta METAS.
    """
    print("[*] Vinculando conteúdos HTML às Metas oficiais do PDF de forma determinística...")
    total_metas = 0
    total_com_conteudo = 0
    total_extras = 0

    for disc_info in catalogo:
        arquivo_path = metas_dir / disc_info["arquivo_alvo"]
        aulas_disponiveis = []
        if arquivo_path.exists():
            conteudo = arquivo_path.read_text(encoding="utf-8", errors="ignore")
            _, aulas_disponiveis = extrair_aulas_do_html(conteudo, arquivo_path.name)
            print(f"   [+] {disc_info['disciplina']}: {len(aulas_disponiveis)} tópicos carregados de {arquivo_path.name}")
        else:
            print(f"   [!] {disc_info['arquivo_alvo']} NÃO ENCONTRADO em {metas_dir}")

        for meta in disc_info["metas"]:
            total_metas += 1
            meta["id"] = f"{disc_info['sigla'].lower()}-meta-{meta['numero']}"
            meta["sigla"] = disc_info["sigla"]
            meta["disciplina"] = disc_info["disciplina"]
            meta["aulas_conteudo"] = []
            meta["extra"] = meta.get("extra", False)
            if meta["extra"]:
                total_extras += 1
            chaves = [normalizar_texto(c) for c in meta.get("chaves", [])]

            if meta["revisao"]:
                meta["orientacao_revisao"] = (
                    "As metas de revisão são como paradas estratégicas para a memorização e solidificação do conhecimento. "
                    "Volte em cada tópico estudado até então na matéria, faça a revisão e acesse novamente os links para treinar com mais algumas questões. "
                    "Revisar não é reestudar. Portanto, seja prático: dê prioridade aos esquemas, aos grifos, às decorebas, aos trechos que sempre são cobrados, "
                    "aos temas em que você está inseguro ou ainda não gravou muito bem e, principalmente, àquilo que você está mais errando nas questões. "
                    "É um ótimo momento para reforçar os seus grifos e anotações, bem como para enriquecer o seu caderno de erros."
                )
            else:
                # Associar exatamente as aulas que batem com as chaves definidas
                for chave in chaves:
                    for aula in aulas_disponiveis:
                        tit_norm = normalizar_texto(aula["titulo"])
                        if chave in tit_norm or tit_norm in chave:
                            if aula not in meta["aulas_conteudo"]:
                                meta["aulas_conteudo"].append(aula)

                if meta["aulas_conteudo"]:
                    total_com_conteudo += 1

        # CRIAÇÃO AUTOMÁTICA DE METAS EXTRAS: Tópicos que constam no HTML mas não foram mapeados no PDF oficial
        aulas_vinculadas_titulos = set()
        for meta in disc_info["metas"]:
            for aula in meta.get("aulas_conteudo", []):
                aulas_vinculadas_titulos.add(aula["titulo"])

        aulas_extras = [a for a in aulas_disponiveis if a["titulo"] not in aulas_vinculadas_titulos]
        if aulas_extras:
            ultimo_num = max([m["numero"] for m in disc_info["metas"]]) if disc_info["metas"] else 0
            for e_idx, extra_aula in enumerate(aulas_extras):
                novo_num = ultimo_num + e_idx + 1
                tit_extra = extra_aula["titulo"]
                if "sem t" in tit_extra.lower() and "tulo" in tit_extra.lower():
                    tit_extra = "Dimensões e Evolução dos Direitos Humanos (Complementar)"
                meta_extra = {
                    "numero": novo_num,
                    "extra": True,
                    "revisao": False,
                    "prioritaria": False,
                    "subtitulo": "Meta Extra • Conteúdo Complementar do HTML",
                    "assuntos": [tit_extra],
                    "chaves": [],
                    "id": f"{disc_info['sigla'].lower()}-meta-extra-{e_idx + 1}",
                    "sigla": disc_info["sigla"],
                    "disciplina": disc_info["disciplina"],
                    "aulas_conteudo": [extra_aula]
                }
                disc_info["metas"].append(meta_extra)
                total_metas += 1
                total_com_conteudo += 1
                total_extras += 1

    # Detecção e inclusão automática de novas disciplinas colocadas na pasta METAS
    novas_discs, ausentes_finais = detectar_novas_disciplinas(metas_dir, catalogo, ausentes_lista)
    if novas_discs:
        catalogo.extend(novas_discs)
        for nd in novas_discs:
            total_metas += len(nd["metas"])
            total_com_conteudo += sum(1 for m in nd["metas"] if m.get("aulas_conteudo"))

    print(f"[OK] Total de Metas na plataforma: {total_metas} ({total_extras} Metas Extras criadas a partir dos HTMLs)")
    print(f"     Disciplinas ativas no catálogo: {len(catalogo)}")
    print(f"     Metas com conteúdo teórico HTML vinculado: {total_com_conteudo}")
    return catalogo, ausentes_finais

def gerar_html_plataforma(catalogo_com_conteudo, disciplinas_ausentes, caminho_saida):
    """Gera a interface completa da Plataforma de Metas"""

    dados_json = json.dumps(catalogo_com_conteudo, ensure_ascii=False)
    ausentes_json = json.dumps(disciplinas_ausentes, ensure_ascii=False)
    
    # Carregar dados dos editais TJAA e AJAJ mapeados
    editais_path = Path(__file__).resolve().parent / "editais_mapped.json"
    if not editais_path.exists():
        editais_path = Path(__file__).resolve().parent.parent / "Mapeamento-Edital" / "editais_mapped.json"
    if editais_path.exists():
        with open(editais_path, "r", encoding="utf-8") as f:
            editais_data = json.load(f)
    else:
        editais_data = {}
    editais_json = json.dumps(editais_data, ensure_ascii=False)

    template_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estudos DL • Plataforma de Metas TRT-7</title>
    <!-- Configurações PWA & Mobile -->
    <meta name="theme-color" content="#090a0f">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Estudos DL">
    <link rel="manifest" href="manifest.json">
    <link rel="icon" type="image/svg+xml" href="icon.svg">
    <link rel="apple-touch-icon" href="icon-192.png">
    <!-- Firebase SDK Compat (v10.8.0) -->
    <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore-compat.js"></script>
    <!-- Detecção e Fixação de Layout Mobile Independente do Navegador -->
    <script>
        function verificarLayoutMobile() {{
            const modo = localStorage.getItem('trt4_layout_modo') || 'auto';
            if (modo === 'pc') {{
                document.documentElement.classList.remove('layout-mobile', 'is-small-mobile');
                document.documentElement.classList.add('layout-pc');
                return;
            }}
            
            // Dimensão física real da tela do dispositivo (hardware)
            const menorLadoFisico = Math.min(window.screen.width, window.screen.height);
            const isSmartphoneFisico = menorLadoFisico <= 860;
            const isMobileUA = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
            const isTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
            const isStandalone = window.matchMedia && (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true);
            const isNarrowWindow = window.innerWidth <= 860;
            
            // É celular se a tela física for pequena, se for PWA standalone, UA mobile com touch, ou largura <= 860
            const ehCelular = (modo === 'celular') || isSmartphoneFisico || (isMobileUA && isTouch) || isStandalone || isNarrowWindow;
            
            if (ehCelular) {{
                document.documentElement.classList.add('layout-mobile');
                document.documentElement.classList.remove('layout-pc');
                if (menorLadoFisico <= 480 || window.innerWidth <= 480) {{
                    document.documentElement.classList.add('is-small-mobile');
                }} else {{
                    document.documentElement.classList.remove('is-small-mobile');
                }}
                
                // Força viewport nativo sem escala reduzida
                let vp = document.querySelector('meta[name="viewport"]');
                if (vp) {{
                    vp.setAttribute('content', 'width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0, user-scalable=yes, viewport-fit=cover');
                }}
            }} else {{
                document.documentElement.classList.remove('layout-mobile', 'is-small-mobile');
                document.documentElement.classList.remove('layout-pc');
            }}
        }}

        // Execução síncrona imediata antes da renderização do body
        verificarLayoutMobile();
        window.addEventListener('resize', verificarLayoutMobile);
        window.addEventListener('orientationchange', verificarLayoutMobile);
    </script>
    <style>
        :root {{
            --bg-body: #090a0f;
            --bg-card: #12151f;
            --bg-card-hover: #171b28;
            --bg-surface: #1a1e2d;
            --border: #23293d;
            --border-light: #2d354e;
            --primary: #3b82f6;
            --primary-hover: #60a5fa;
            --primary-alpha: rgba(59, 130, 246, 0.12);
            --accent-green: #10b981;
            --accent-green-alpha: rgba(16, 185, 129, 0.15);
            --accent-gold: #f59e0b;
            --accent-gold-alpha: rgba(245, 158, 11, 0.16);
            --accent-red: #ef4444;
            --text-heading: #f8fafc;
            --text-body: #cbd5e1;
            --text-muted: #8492a6;
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
            --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.5);
            --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        body.theme-amoled {{
            --bg-body: #000000;
            --bg-card: #080808;
            --bg-card-hover: #121212;
            --bg-surface: #181818;
            --border: #222222;
            --border-light: #333333;
        }}

        body.theme-sepia {{
            --bg-body: #f7f1e5;
            --bg-card: #fffdf9;
            --bg-card-hover: #f3ece0;
            --bg-surface: #eae1d0;
            --border: #dfd4c0;
            --border-light: #c8b99d;
            --primary: #b45309;
            --primary-hover: #92400e;
            --primary-alpha: rgba(180, 83, 9, 0.12);
            --accent-green: #047857;
            --accent-green-alpha: rgba(4, 120, 87, 0.15);
            --accent-gold: #b45309;
            --text-heading: #292524;
            --text-body: #44403c;
            --text-muted: #78716c;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }}

        body.theme-light {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --bg-surface: #e2e8f0;
            --border: #cbd5e1;
            --border-light: #94a3b8;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --primary-alpha: rgba(37, 99, 235, 0.1);
            --accent-green: #059669;
            --accent-green-alpha: rgba(5, 150, 105, 0.12);
            --accent-gold: #d97706;
            --text-heading: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{
            overflow-x: hidden;
            max-width: 100vw;
            background: var(--bg-body);
            color: var(--text-body);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            min-height: 100vh;
        }}

        /* TOPBAR */
                /* TOPBAR REFINADA */
        .topbar {{
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 8px 24px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: var(--transition);
            box-sizing: border-box;
            width: 100%;
        }}
        .topbar-main-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            width: 100%;
        }}
        .topbar-subrow {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-top: 6px;
            margin-top: 6px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            width: 100%;
        }}
        .topbar-tools {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-shrink: 0;
        }}
        /* BUSCA CENTRALIZADA */
        .topbar-search-container {{
            position: relative;
            max-width: 440px;
            min-width: 320px;
            width: 100%;
            margin: 0 auto;
        }}
        .topbar-subrow-spacer {{
            width: 290px;
            flex-shrink: 0;
            display: block;
        }}
        @media (max-width: 1200px) {{
            .topbar-subrow-spacer {{ display: none; }}
        }}
        .search-input-box {{
            position: relative;
            display: flex;
            align-items: center;
            background: var(--bg-body);
            border: 1px solid var(--border);
            border-radius: 9999px;
            padding: 0 12px;
            height: 32px;
            transition: var(--transition);
        }}
        .search-input-box:focus-within {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
            background: var(--bg-card);
        }}
        .search-icon {{
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-right: 8px;
            user-select: none;
        }}
        .topbar-search-input {{
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-heading);
            font-size: 0.80rem;
            font-weight: 500;
            padding: 5px 0;
            font-family: inherit;
        }}
        .topbar-search-input::placeholder {{
            color: var(--text-muted);
            opacity: 0.8;
            font-size: 0.78rem;
        }}
        .btn-clear-search {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 1.1rem;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
        }}
        .btn-clear-search:hover {{ color: var(--text-heading); }}
        .search-shortcut-hint {{
            font-size: 0.65rem;
            font-weight: 700;
            color: var(--text-muted);
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 1px 5px;
            user-select: none;
            margin-left: 6px;
        }}
        .search-dropdown-results {{
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            right: 0;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
            max-height: 480px;
            overflow-y: auto;
            z-index: 1000;
            padding: 8px;
        }}
        .topbar-brand {{
            display: flex; align-items: center; gap: 12px; cursor: pointer;
        }}
        .topbar-logo {{
            width: 42px; height: 42px; border-radius: 12px;
            background: linear-gradient(135deg, #111827, #0b0f19);
            border: 1.5px solid #38bdf8;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 4px 14px rgba(56, 189, 248, 0.28);
            position: relative;
            transition: var(--transition);
        }}
        .topbar-brand:hover .topbar-logo {{
            transform: scale(1.05);
            border-color: #818cf8;
            box-shadow: 0 6px 20px rgba(129, 140, 248, 0.38);
        }}
        .topbar-logo-badge {{
            font-size: 1.15rem; font-weight: 900;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.04em;
            line-height: 1;
        }}
        .topbar-title h1 {{ font-size: 0.92rem; font-weight: 800; color: var(--text-heading); letter-spacing: -0.01em; }}
        .topbar-title p {{ font-size: 0.66rem; color: var(--text-muted); }}

        /* BUSCA GLOBAL NO TOPO (AO LADO DO BOTÃO INSTALAR APP) */
        .topbar-search-container {{
            position: relative;
            width: 190px;
            margin: 0;
            transition: width 0.25s ease;
        }}
        .topbar-search-container:focus-within {{
            width: 280px;
        }}
        .search-input-box {{
            position: relative;
            display: flex;
            align-items: center;
            background: var(--bg-body);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0 8px;
            height: 32px;
            transition: var(--transition);
        }}
        .search-input-box:focus-within {{
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
            background: var(--bg-card);
        }}
        .search-icon {{
            font-size: 0.80rem;
            color: var(--text-muted);
            margin-right: 6px;
            user-select: none;
        }}
        .topbar-search-input {{
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-heading);
            font-size: 0.78rem;
            font-weight: 500;
            padding: 4px 0;
            font-family: inherit;
        }}
        .topbar-search-input::placeholder {{
            color: var(--text-muted);
            opacity: 0.8;
            font-size: 0.75rem;
        }}
        .btn-clear-search {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 1rem;
            cursor: pointer;
            padding: 0 4px;
            line-height: 1;
        }}
        .btn-clear-search:hover {{ color: var(--text-heading); }}
        .search-shortcut-hint {{
            font-size: 0.62rem;
            font-weight: 700;
            color: var(--text-muted);
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 1px 4px;
            user-select: none;
            margin-left: 4px;
        }}

        /* DROPDOWN DE RESULTADOS */
        .search-dropdown-results {{
            position: absolute;
            top: calc(100% + 6px);
            right: 0;
            width: 440px;
            max-width: 90vw;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
            max-height: 480px;
            overflow-y: auto;
            z-index: 1000;
            padding: 8px;
        }}
        .search-result-group-title {{
            font-size: 0.70rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            padding: 6px 8px 4px 8px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 4px;
        }}
        .search-result-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: var(--transition);
            gap: 10px;
        }}
        .search-result-item:hover {{
            background: var(--bg-surface);
        }}
        .search-result-left {{
            display: flex;
            flex-direction: column;
            gap: 2px;
            overflow: hidden;
        }}
        .search-result-title {{
            font-size: 0.84rem;
            font-weight: 700;
            color: var(--text-heading);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .search-result-subtitle {{
            font-size: 0.73rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .search-result-snippet {{
            font-size: 0.72rem;
            color: var(--text-body);
            background: var(--bg-body);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 2px 6px;
            margin-top: 3px;
            font-family: inherit;
        }}
        .search-result-badges {{
            display: flex;
            align-items: center;
            gap: 5px;
            flex-shrink: 0;
        }}
        .search-result-disc-badge {{
            font-size: 0.68rem;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 6px;
            background: var(--primary-alpha);
            color: var(--primary);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }}
        .search-result-disc-badge.extra {{
            background: rgba(139, 92, 246, 0.15);
            color: #c4b5fd;
            border-color: rgba(139, 92, 246, 0.4);
        }}
        .search-result-item mark {{
            background: rgba(245, 158, 11, 0.3);
            color: #fbbf24;
            padding: 0 2px;
            border-radius: 2px;
            font-weight: 700;
        }}
        .search-empty-state {{
            padding: 16px;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.82rem;
        }}

        /* PROGRESSO GLOBAL NA TOPBAR */
        .topbar-progress-wrap {{
            display: flex; align-items: center; gap: 12px;
            background: var(--bg-card); border: 1px solid var(--border);
            padding: 6px 14px; border-radius: 30px;
        }}
        .topbar-progress-text {{ font-size: 0.80rem; font-weight: 700; color: var(--text-heading); }}
        .topbar-progress-bar {{
            width: 110px; height: 7px; background: var(--border); border-radius: 999px; overflow: hidden;
        }}
        .topbar-progress-fill {{
            height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent-green));
            width: 0%; border-radius: 999px; transition: width 0.3s ease;
        }}

        /* BOTÃO PRÓXIMA META DO CICLO */
        .btn-next-cycle {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: #ffffff; border: none; padding: 7px 16px; border-radius: 20px;
            font-size: 0.83rem; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 7px;
            box-shadow: 0 3px 12px rgba(16, 185, 129, 0.3); transition: var(--transition);
        }}
        .btn-next-cycle:hover {{ transform: translateY(-1px); box-shadow: 0 5px 16px rgba(16, 185, 129, 0.45); }}

        /* ABAS DE NAVEGAÇÃO */
        .topbar-tabs {{
            display: flex; background: var(--bg-body); border: 1px solid var(--border); border-radius: 10px; padding: 3px; gap: 4px;
        }}
        .topbar-tab-btn {{
            background: transparent; border: none; color: var(--text-muted);
            padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 700; cursor: pointer;
            transition: var(--transition);
        }}
        .topbar-tab-btn.active {{
            background: var(--primary); color: #ffffff; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        }}

        /* FERRAMENTAS */
        .topbar-tools {{ display: flex; align-items: center; gap: 8px; }}
        .pomo-badge {{
            display: flex; align-items: center; gap: 6px; background: var(--bg-card);
            border: 1px solid var(--border); padding: 5px 12px; border-radius: 8px; font-size: 0.82rem; font-weight: 700;
        }}
        .btn-tool {{
            background: var(--bg-card); border: 1px solid var(--border); color: var(--text-body);
            padding: 6px 10px; border-radius: 8px; font-size: 0.78rem; font-weight: 600; cursor: pointer;
            transition: var(--transition);
        }}
        .btn-tool:hover {{ border-color: var(--primary); color: var(--primary); }}
        .btn-pwa-install {{
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            color: #ffffff !important;
            border-color: #60a5fa !important;
            animation: pulse-pwa 2s infinite ease-in-out;
        }}
        .btn-pwa-install:hover {{
            background: linear-gradient(135deg, #1d4ed8, #6d28d9);
            transform: translateY(-1px);
        }}
        @keyframes pulse-pwa {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }}
            50% {{ box-shadow: 0 0 0 5px rgba(59, 130, 246, 0); }}
        }}
        .btn-cloud-sync {{
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.35);
            color: #93c5fd;
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
        }}
        .btn-cloud-sync:hover {{
            background: rgba(59, 130, 246, 0.25);
            border-color: #60a5fa;
            color: #ffffff;
        }}
        .btn-cloud-sync.synced {{
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.4);
            color: #6ee7b7;
        }}
        .btn-cloud-sync.syncing {{
            background: rgba(245, 158, 11, 0.15);
            border-color: rgba(245, 158, 11, 0.5);
            color: #fde047;
        }}
        .btn-cloud-sync.offline {{
            background: rgba(239, 68, 68, 0.12);
            border-color: rgba(239, 68, 68, 0.35);
            color: #fca5a5;
        }}
        .theme-select {{
            background: var(--bg-card); border: 1px solid var(--border); color: var(--text-body);
            padding: 5px 8px; border-radius: 8px; font-size: 0.78rem; cursor: pointer; outline: none;
        }}

        /* CONTAINER PRINCIPAL */
        .main-container {{
            max-width: 1560px; margin: 0 auto; padding: 12px 18px 50px 18px;
        }}

        /* SEÇÃO QUADRO DE METAS (MATRIZ COMPACTA) */
        .quadro-section {{ display: block; }}
        .quadro-header-banner {{
            background: var(--bg-card); border: 1px solid var(--border); border-left: 3px solid var(--accent-green);
            border-radius: var(--radius-sm); padding: 7px 14px; margin-bottom: 12px;
            display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
        }}
        .quadro-header-info {{ display: flex; align-items: center; gap: 8px; }}
        .quadro-header-info h2 {{ font-size: 0.92rem; font-weight: 800; color: var(--text-heading); margin: 0; }}
        .quadro-header-info p {{ display: none; }}

        .quadro-banner-controls {{
            display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
        }}
        .quadro-legenda {{
            display: flex; align-items: center; gap: 10px; font-size: 0.72rem; font-weight: 600; color: var(--text-muted);
        }}
        .legenda-item {{ display: flex; align-items: center; gap: 5px; }}
        .legenda-dot {{ width: 8px; height: 8px; border-radius: 2px; display: inline-block; }}
        .legenda-dot.revisao {{ background: var(--accent-green); }}
        .legenda-dot.prioritaria {{ background: var(--accent-gold); }}
        .legenda-dot.concluida {{ background: #2563eb; }}
        .legenda-dot.extra {{ background: #8b5cf6; }}

        .quadro-filtros {{
            display: flex; align-items: center; gap: 4px;
        }}
        .filtro-btn {{
            background: var(--bg-surface); border: 1px solid var(--border); color: var(--text-muted);
            padding: 3px 8px; border-radius: 5px; font-size: 0.70rem; font-weight: 700; cursor: pointer;
            transition: var(--transition);
        }}
        .filtro-btn:hover {{ border-color: var(--primary); color: var(--text-heading); }}
        .filtro-btn.active {{
            background: var(--primary); color: #fff; border-color: var(--primary);
        }}
        .filtro-btn.filtro-extra.active {{
            background: #8b5cf6; border-color: #8b5cf6;
        }}
        .matriz-cell.dimmed {{
            opacity: 0.15; filter: grayscale(1); transform: none !important; pointer-events: none;
        }}

        /* TABELA DA MATRIZ DO CICLO */
        .matriz-container {{
            background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 8px 12px; box-shadow: var(--shadow); overflow-x: auto;
        }}
        .matriz-table {{
            width: 100%; border-collapse: separate; border-spacing: 3px; min-width: 980px;
        }}
        .matriz-row-header {{
            text-align: left; padding: 4px 8px; font-size: 0.74rem; font-weight: 800;
            color: var(--text-heading); white-space: nowrap; width: 160px;
            border-right: 1px solid var(--border); line-height: 1.25;
        }}
        .matriz-cell {{
            background: var(--bg-body); border: 1px solid var(--border);
            border-radius: 5px; padding: 4px 2px; text-align: center;
            font-size: 0.67rem; font-weight: 800; cursor: pointer; transition: var(--transition);
            min-width: 35px; position: relative; user-select: none;
        }}
        .matriz-cell:hover {{
            transform: scale(1.12); border-color: var(--primary); box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 5;
        }}
        .matriz-cell.revisao {{
            border-color: rgba(16, 185, 129, 0.5);
            background: rgba(16, 185, 129, 0.12);
            color: var(--accent-green);
        }}
        .matriz-cell.extra {{
            border-color: rgba(139, 92, 246, 0.5);
            background: rgba(139, 92, 246, 0.12);
            color: #c4b5fd;
        }}
        .matriz-cell.extra:hover {{
            border-color: #a78bfa;
            background: rgba(139, 92, 246, 0.25);
        }}
        .matriz-cell.prioritaria::after {{
            content: '★'; position: absolute; top: 0px; right: 2px; font-size: 0.55rem; color: var(--accent-gold);
        }}
        .matriz-cell.concluida {{
            background: rgba(59, 130, 246, 0.25) !important;
            border-color: var(--primary) !important;
            color: #ffffff !important;
        }}
        .matriz-cell.concluida.revisao {{
            background: rgba(16, 185, 129, 0.35) !important;
            border-color: var(--accent-green) !important;
            color: #ffffff !important;
        }}
        .matriz-cell.concluida.extra {{
            background: rgba(139, 92, 246, 0.35) !important;
            border-color: #8b5cf6 !important;
            color: #ffffff !important;
        }}
        .matriz-cell-badge {{ font-size: 0.55rem; opacity: 0.85; display: block; line-height: 1; margin-top: 1px; }}

        /* PAINEL DE METAS EXTRAS NO FINAL DE CADA DISCIPLINA (QUADRO DE METAS) */
        .quadro-metas-extras-panel {{
            margin-top: 14px; background: var(--bg-card); border: 1px solid var(--border);
            border-radius: var(--radius-md); padding: 12px 16px; box-shadow: var(--shadow);
        }}
        .quadro-extras-header-title {{
            display: flex; align-items: flex-start; gap: 14px; margin-bottom: 20px;
            border-bottom: 1px solid var(--border); padding-bottom: 14px;
        }}
        .quadro-extras-header-title h3 {{
            font-size: 1.15rem; font-weight: 800; color: #c4b5fd; margin-bottom: 4px;
            display: flex; align-items: center; gap: 8px;
        }}
        .quadro-extras-header-title p {{
            font-size: 0.84rem; color: var(--text-muted);
        }}
        .quadro-extras-disc-group {{
            background: var(--bg-body); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 16px; margin-bottom: 16px; transition: var(--transition);
        }}
        .quadro-extras-disc-group:hover {{
            border-color: rgba(139, 92, 246, 0.4);
        }}
        .quadro-extras-disc-title {{
            font-size: 0.95rem; font-weight: 800; color: var(--text-heading); margin-bottom: 12px;
            display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
        }}
        .quadro-extras-cards-list {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 12px;
        }}
        .quadro-extra-card-item {{
            background: var(--bg-card); border: 1px solid rgba(139, 92, 246, 0.3);
            border-left: 4px solid #8b5cf6; border-radius: 10px; padding: 12px 14px;
            display: flex; flex-direction: column; justify-content: space-between; gap: 10px;
            transition: var(--transition);
        }}
        .quadro-extra-card-item:hover {{
            border-color: #a78bfa; transform: translateY(-2px);
            box-shadow: 0 4px 14px rgba(139, 92, 246, 0.15);
        }}
        .quadro-extra-card-item.concluida {{
            border-left-color: var(--accent-green); background: rgba(16, 185, 129, 0.05);
        }}
        .quadro-extra-item-top {{
            display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;
        }}
        .quadro-extra-item-nome {{
            font-size: 0.88rem; font-weight: 800; color: #e0e7ff; line-height: 1.35;
        }}
        .quadro-extra-item-sub {{
            font-size: 0.74rem; color: var(--text-muted); margin-top: 3px;
        }}
        .quadro-extra-item-actions {{
            display: flex; align-items: center; justify-content: space-between;
            margin-top: 6px; padding-top: 8px; border-top: 1px solid var(--border);
        }}
        .btn-estudar-extra {{
            background: rgba(139, 92, 246, 0.15); border: 1px solid #8b5cf6; color: #c4b5fd;
            padding: 5px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 700;
            cursor: pointer; transition: var(--transition);
        }}
        .btn-estudar-extra:hover {{
            background: #8b5cf6; color: #fff;
        }}

        /* SEÇÃO DE ESTUDO DA META */
        .meta-view-section {{ display: none; }}
        .meta-view-header {{
            background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 16px 22px; margin-bottom: 16px; border-left: 4px solid var(--primary);
            box-shadow: var(--shadow); position: relative;
        }}
        .meta-view-header.is-revisao {{ border-left-color: var(--accent-green); }}
        .meta-view-header.is-extra {{ border-left-color: #8b5cf6; }}
        .meta-breadcrumbs {{
            display: flex; align-items: center; gap: 8px; font-size: 0.80rem; color: var(--text-muted); margin-bottom: 8px;
        }}
        .meta-breadcrumbs a {{ color: var(--primary); cursor: pointer; text-decoration: none; font-weight: 700; }}
        .meta-breadcrumbs a:hover {{ text-decoration: underline; }}

        .meta-header-row {{
            display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;
        }}
        .meta-header-titles h2 {{
            font-size: 1.35rem; font-weight: 800; color: var(--text-heading); display: flex; align-items: center; gap: 10px;
        }}
        .badge-subtitulo {{
            background: var(--bg-surface); color: var(--text-muted); border: 1px solid var(--border);
            font-size: 0.72rem; padding: 2px 8px; border-radius: 8px; font-weight: 700;
        }}
        .badge-star {{
            background: var(--accent-gold-alpha); color: var(--accent-gold); border: 1px solid rgba(245, 158, 11, 0.3);
            font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; font-weight: 800;
        }}
        .badge-rev {{
            background: var(--accent-green-alpha); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3);
            font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; font-weight: 800;
        }}
        .badge-extra {{
            background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139, 92, 246, 0.45);
            font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; font-weight: 800;
        }}

        .btn-toggle-meta {{
            background: var(--bg-body); border: 2px solid var(--border); color: var(--text-heading);
            padding: 8px 18px; border-radius: 20px; font-size: 0.86rem; font-weight: 800; cursor: pointer;
            display: flex; align-items: center; gap: 8px; transition: var(--transition);
        }}
        .btn-toggle-meta.checked {{
            background: var(--accent-green); border-color: var(--accent-green); color: #fff;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
        }}

        /* CARD OFICIAL DE TÓPICOS DO PDF */
        .meta-pdf-assuntos-card {{
            background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 16px 20px; margin-bottom: 18px; box-shadow: var(--shadow);
        }}
        .meta-pdf-assuntos-header {{
            font-size: 0.88rem; font-weight: 800; color: var(--text-heading); margin-bottom: 12px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .meta-pdf-assuntos-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
        .meta-item-label {{
            display: flex; align-items: center; justify-content: space-between;
            background: var(--bg-body); border: 1px solid var(--border); border-radius: 8px;
            padding: 8px 14px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: var(--transition);
        }}
        .meta-item-label:hover {{ border-color: var(--primary); }}
        .meta-item-left {{ display: flex; align-items: center; gap: 10px; }}
        .meta-item-left input[type="checkbox"] {{ width: 16px; height: 16px; accent-color: var(--primary); }}
        .badge-conteudo-ok {{
            background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3);
            font-size: 0.70rem; padding: 2px 7px; border-radius: 6px; font-weight: 800;
        }}
        .badge-lei-seca {{
            background: rgba(59, 130, 246, 0.12); color: var(--primary); border: 1px solid rgba(59, 130, 246, 0.25);
            font-size: 0.70rem; padding: 2px 7px; border-radius: 6px; font-weight: 700;
        }}

        /* PAINEL DE CONTROLE DE QUESTÕES DA META */
        .meta-control-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 20px;
        }}
        .meta-widget-card {{
            background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 14px 18px; box-shadow: var(--shadow);
        }}
        .meta-widget-title {{
            font-size: 0.82rem; font-weight: 800; color: var(--text-heading); text-transform: uppercase;
            letter-spacing: 0.04em; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;
        }}
        .questoes-inputs-row {{
            display: flex; align-items: center; gap: 12px;
        }}
        .questoes-field {{ display: flex; flex-direction: column; gap: 4px; flex: 1; }}
        .questoes-field label {{ font-size: 0.72rem; color: var(--text-muted); font-weight: 700; }}
        .questoes-field input {{
            background: var(--bg-body); border: 1px solid var(--border); color: var(--text-heading);
            padding: 7px 10px; border-radius: 8px; font-size: 0.90rem; font-weight: 700; outline: none; width: 100%;
        }}
        .questoes-field input:focus {{ border-color: var(--primary); }}
        .questoes-stat-badge {{
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            background: var(--bg-body); border: 1px solid var(--border); border-radius: 10px;
            padding: 6px 14px; min-width: 90px;
        }}
        .questoes-stat-val {{ font-size: 1.15rem; font-weight: 900; }}
        .questoes-stat-val.otimo {{ color: var(--accent-green); }}
        .questoes-stat-val.medio {{ color: var(--accent-gold); }}
        .questoes-stat-val.baixo {{ color: var(--accent-red); }}

        /* CHECKLIST DE REVISÃO ESTRATÉGICA */
        .revisao-box {{
            background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.25);
            border-radius: var(--radius-md); padding: 18px 22px; margin-bottom: 20px;
        }}
        .revisao-box h3 {{
            color: var(--accent-green); font-size: 1.05rem; font-weight: 800; margin-bottom: 8px;
            display: flex; align-items: center; gap: 8px;
        }}
        .revisao-box p {{ font-size: 0.85rem; color: var(--text-body); margin-bottom: 12px; line-height: 1.6; }}
        .checklist-item {{
            display: flex; align-items: center; gap: 10px; font-size: 0.86rem; font-weight: 600;
            padding: 6px 0; cursor: pointer; user-select: none;
        }}
        .checklist-item input[type="checkbox"] {{
            width: 17px; height: 17px; accent-color: var(--accent-green); cursor: pointer;
        }}

        /* CADERNO DE ERROS DA META */
        .caderno-erros-area {{
            width: 100%; min-height: 85px; background: var(--bg-body); border: 1px solid var(--border);
            border-radius: 8px; color: var(--text-body); padding: 10px 12px; font-size: 0.85rem;
            font-family: inherit; resize: vertical; outline: none; transition: var(--transition);
        }}
        .caderno-erros-area:focus {{ border-color: var(--primary); }}

        /* PAINEL DE SUBTÓPICOS ESTILO CADERNO APROVADO */
        .subtopicos-quick-panel {{
            background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 14px 18px; margin-bottom: 18px; box-shadow: var(--shadow);
        }}
        .subtopicos-panel-top {{
            display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;
        }}
        .subtopicos-panel-title {{
            font-size: 0.82rem; font-weight: 800; color: var(--text-heading); text-transform: uppercase; letter-spacing: 0.05em;
            display: flex; align-items: center; gap: 6px;
        }}
        .btn-toggle-subtopics-mode {{
            background: var(--bg-surface); border: 1px solid var(--border); color: var(--text-muted);
            padding: 4px 10px; border-radius: 6px; font-size: 0.74rem; font-weight: 700; cursor: pointer;
            transition: var(--transition);
        }}
        .btn-toggle-subtopics-mode:hover {{
            border-color: var(--primary); color: var(--text-heading);
        }}
        .subtopicos-pills-container {{
            display: flex; gap: 8px; flex-wrap: wrap;
        }}
        .subtopico-pill {{
            background: var(--bg-body); border: 1px solid var(--border); color: var(--text-body);
            padding: 8px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 600; cursor: pointer;
            display: inline-flex; align-items: center; gap: 6px; transition: var(--transition);
        }}
        .subtopico-pill:hover {{
            border-color: var(--primary); color: var(--primary); transform: translateY(-1px);
        }}
        .subtopico-pill.active {{
            background: linear-gradient(135deg, var(--primary), #1d4ed8); color: #fff !important;
            border-color: transparent; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
        }}
        .subtopico-pill.concluido {{
            border-color: rgba(16, 185, 129, 0.5); color: var(--accent-green);
        }}
        .subtopico-pill.active.concluido {{
            background: linear-gradient(135deg, #059669, #10b981); color: #fff !important;
        }}

        .aula-header-action-row {{
            display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border);
            padding-bottom: 12px; margin-bottom: 16px; flex-wrap: wrap; gap: 12px;
        }}
        .aula-header-title-box {{
            display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
        }}
        .aula-header-badge {{
            background: var(--bg-surface); border: 1px solid var(--border); color: var(--text-muted);
            padding: 3px 8px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;
        }}
        .aula-card-subtitulo {{
            font-size: 1.15rem; font-weight: 800; color: var(--text-heading); margin: 0;
        }}
        .aula-concluida-toggle {{
            display: inline-flex; align-items: center; gap: 8px; font-size: 0.84rem; font-weight: 700;
            color: var(--text-heading); cursor: pointer; background: var(--bg-surface); padding: 6px 12px;
            border-radius: 8px; border: 1px solid var(--border); transition: var(--transition); user-select: none;
        }}
        .aula-concluida-toggle:hover {{
            border-color: var(--accent-green);
        }}
        .aula-concluida-toggle input[type="checkbox"] {{
            width: 16px; height: 16px; accent-color: var(--accent-green); cursor: pointer;
        }}

        /* CONTEÚDO DAS AULAS VINCULADAS */
        .aulas-content-wrapper {{ margin-top: 16px; display: flex; flex-direction: column; gap: 16px; }}
        .aula-card-render {{
            background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md);
            padding: 22px 26px; box-shadow: var(--shadow);
        }}
        .aula-card-render h3 {{
            font-size: 1.15rem; font-weight: 800; color: var(--text-heading); margin-bottom: 14px;
            padding-bottom: 8px; border-bottom: 1px solid var(--border);
        }}
        .aula-body-text {{ font-size: 0.95rem; line-height: 1.75; color: var(--text-body); }}
        .aula-body-text h1, .aula-body-text h2, .aula-body-text h3 {{ color: var(--text-heading); margin: 18px 0 10px 0; }}
        .aula-body-text p {{ margin-bottom: 12px; }}
        .aula-body-text table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 0.88rem; }}
        .aula-body-text th, .aula-body-text td {{ border: 1px solid var(--border); padding: 9px 12px; }}
        .aula-body-text th {{ background: var(--bg-surface); color: var(--text-heading); }}
        .aula-body-text a {{ color: var(--primary); text-decoration: underline; }}
        .aula-body-text ul, .aula-body-text ol {{ margin-left: 24px; margin-bottom: 12px; }}

        /* NAVEGAÇÃO INFERIOR DA META */
        .meta-nav-footer {{
            display: flex; align-items: center; justify-content: space-between; margin-top: 24px;
            padding-top: 16px; border-top: 1px solid var(--border);
        }}
        .btn-nav-meta {{
            background: var(--bg-card); border: 1px solid var(--border); color: var(--text-body);
            padding: 8px 16px; border-radius: 10px; font-size: 0.84rem; font-weight: 700; cursor: pointer;
            transition: var(--transition);
        }}
        .btn-nav-meta:hover {{ border-color: var(--primary); color: var(--primary); transform: translateY(-1px); }}

        /* SEÇÃO DE DISCIPLINAS */
        .disciplinas-section {{ display: none; }}
        
        /* VISÃO: METAS ORGANIZADAS POR DISCIPLINA */
        .disciplinas-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .disciplinas-filtros-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .disc-filter-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: var(--radius-sm);
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
        }}
        .disc-filter-btn:hover {{
            color: var(--text-heading);
            border-color: var(--border-hover);
        }}
        .disc-filter-btn.active {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}
        .disciplina-bloco {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 20px;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }}
        .disciplina-bloco:hover {{
            border-color: var(--border-hover);
        }}
        .disc-bloco-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }}
        .disc-bloco-left {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .disc-sigla-tag {{
            background: var(--bg-hover);
            color: var(--text-heading);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
            font-size: 0.85rem;
            font-weight: 800;
            border: 1px solid var(--border);
            letter-spacing: 0.5px;
        }}
        .disc-nome-titulo {{
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-heading);
            margin: 0;
        }}
        .disc-bloco-right {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .disc-progresso-badge {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--accent-green);
            background: rgba(16, 185, 129, 0.1);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}
        .disc-progress-mini-bar {{
            width: 140px;
            height: 8px;
            background: var(--bg-hover);
            border-radius: 999px;
            overflow: hidden;
        }}
        .disc-progress-mini-fill {{
            height: 100%;
            background: var(--accent-green);
            border-radius: 999px;
            transition: width 0.3s ease;
        }}
        .disc-metas-cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }}
        .disc-meta-card {{
            background: var(--bg-body);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 12px 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 10px;
            cursor: pointer;
            transition: var(--transition);
            position: relative;
        }}
        .disc-meta-card:hover {{
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        .disc-meta-card.concluida {{
            border-color: rgba(16, 185, 129, 0.4);
            background: rgba(16, 185, 129, 0.03);
        }}
        .disc-meta-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 8px;
        }}
        .disc-meta-badge-num {{
            font-size: 0.80rem;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 4px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            color: var(--text-heading);
        }}
        .disc-meta-badge-num.rev {{
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.4);
            color: var(--accent-green);
        }}
        .disc-meta-badge-num.extra {{
            background: rgba(168, 85, 247, 0.15);
            border-color: rgba(168, 85, 247, 0.4);
            color: #c084fc;
        }}
        .disc-meta-badge-prio {{
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--accent-orange);
            background: rgba(249, 115, 22, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(249, 115, 22, 0.25);
        }}
        .disc-meta-assuntos {{
            font-size: 0.84rem;
            color: var(--text-body);
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            font-weight: 500;
        }}
        .disc-meta-bottom {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 4px;
            padding-top: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .btn-check-disc-meta {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            transition: var(--transition);
        }}
        .btn-check-disc-meta:hover {{
            border-color: var(--accent-green);
            color: var(--accent-green);
        }}
        .btn-check-disc-meta.checked {{
            background: rgba(16, 185, 129, 0.15);
            border-color: var(--accent-green);
            color: var(--accent-green);
        }}
        .btn-estudar-disc-meta {{
            font-size: 0.75rem;
            color: var(--primary);
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .diag-title {{ font-size: 1.10rem; font-weight: 800; color: var(--text-heading); margin-bottom: 8px; }}
        .diag-badge-missing {{
            background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.3);
            font-size: 0.72rem; padding: 2px 8px; border-radius: 8px; font-weight: 800;
        }}

        /* MODAL / TOAST */
        .toast-notify {{
            position: fixed; bottom: 24px; right: 24px; background: var(--bg-card);
            border: 1px solid var(--border); border-left: 4px solid var(--accent-green);
            padding: 12px 18px; border-radius: 10px; box-shadow: var(--shadow-hover);
            font-size: 0.85rem; font-weight: 700; color: var(--text-heading);
            display: none; align-items: center; gap: 8px; z-index: 1000;
        }}

        /* ==========================================================================
           RESPONSIVIDADE MOBILE REFINADA (SMARTPHONES & TABLETS)
           ========================================================================== */
        @media (max-width: 860px) {{
            .hide-mobile {{
                display: none !important;
            }}

            /* 1. TOPBAR & CABEÇALHO COMPACTO */
            .topbar {{
                padding: 6px 10px;
                position: sticky;
                top: 0;
            }}
            .topbar-main-row {{
                flex-wrap: wrap;
                align-items: center;
                justify-content: space-between;
                gap: 6px;
            }}
            .topbar-brand {{
                order: 1;
                gap: 8px;
            }}
            .topbar-logo {{
                width: 34px;
                height: 34px;
                border-radius: 10px;
            }}
            .topbar-logo-badge {{
                font-size: 0.95rem;
            }}
            .topbar-title h1 {{
                font-size: 0.84rem;
                margin: 0;
            }}
            .topbar-title p {{
                display: none; /* Oculta slogan no mobile para economizar altura */
            }}
            .topbar-cycle-group {{
                order: 2;
                display: flex;
                align-items: center;
                gap: 6px;
                margin: 0;
            }}
            .topbar-progress-wrap {{
                padding: 3px 8px;
                gap: 6px;
            }}
            .topbar-progress-text {{
                font-size: 0.70rem;
            }}
            .topbar-progress-bar {{
                width: 50px;
                height: 5px;
            }}
            .btn-next-cycle {{
                padding: 5px 10px;
                font-size: 0.74rem;
                border-radius: 16px;
            }}
            .btn-next-cycle span {{
                white-space: nowrap;
            }}

            /* ABAS EM LINHA DEDICADA COM SCROLL HORIZONTAL POR TOQUE */
            .topbar-tabs {{
                order: 3;
                width: 100%;
                display: flex;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                flex-wrap: nowrap;
                gap: 4px;
                padding: 3px;
                margin-top: 3px;
            }}
            .topbar-tabs::-webkit-scrollbar {{
                display: none;
            }}
            .topbar-tab-btn {{
                flex: 1 0 auto;
                white-space: nowrap;
                padding: 6px 10px;
                font-size: 0.78rem;
                font-weight: 700;
                text-align: center;
                border-radius: 7px;
            }}

            /* LINHA 2: FERRAMENTAS & BUSCA */
            .topbar-subrow {{
                flex-direction: column;
                align-items: stretch;
                gap: 6px;
                padding-top: 5px;
                margin-top: 4px;
            }}
            .topbar-tools {{
                display: flex;
                align-items: center;
                justify-content: flex-start;
                width: 100%;
                gap: 8px;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                padding-bottom: 2px;
            }}
            .topbar-tools::-webkit-scrollbar {{
                display: none;
            }}
            .pomo-badge {{
                padding: 4px 8px;
                font-size: 0.76rem;
                gap: 4px;
                flex-shrink: 0;
            }}
            .pomo-badge .btn-tool {{
                padding: 3px 6px;
                font-size: 0.72rem;
            }}
            .theme-select {{
                padding: 4px 6px;
                font-size: 0.74rem;
                flex-shrink: 0;
            }}
            .btn-cloud-sync {{
                padding: 5px 10px;
                font-size: 0.76rem;
                font-weight: 700;
                flex-shrink: 0;
                white-space: nowrap;
            }}
            .btn-layout-toggle {{
                padding: 4px 6px;
                font-size: 0.74rem;
                flex-shrink: 0;
            }}
            .btn-layout-toggle #layout-toggle-text {{
                display: none;
            }}
            .btn-pwa-install {{
                padding: 4px 8px;
                font-size: 0.74rem;
                flex-shrink: 0;
            }}
            .topbar-search-container {{
                width: 100% !important;
                max-width: 100% !important;
                min-width: 0 !important;
                margin: 0;
            }}
            .search-input-box {{
                height: 34px;
            }}
            .topbar-subrow-spacer {{
                display: none !important;
            }}
            .search-dropdown-results {{
                width: 100%;
                left: 0;
                right: 0;
                max-width: 100%;
            }}

            /* 2. CONTAINER PRINCIPAL */
            .main-container {{
                padding: 8px 8px 50px 8px;
            }}

            /* 3. QUADRO DE METAS (MATRIZ NO MOBILE) */
            .quadro-header-banner {{
                padding: 8px 10px;
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
            }}
            .quadro-header-info {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .quadro-banner-controls {{
                width: 100%;
            }}
            .quadro-filtros {{
                display: flex;
                width: 100%;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                flex-wrap: nowrap;
                gap: 6px;
            }}
            .quadro-filtros::-webkit-scrollbar {{
                display: none;
            }}
            .filtro-btn {{
                flex: 0 0 auto;
                padding: 5px 12px;
                font-size: 0.74rem;
                white-space: nowrap;
            }}

            /* MATRIZ COM COLUNA STICKY FIXA E TOUCH CONFORTÁVEL */
            .matriz-container {{
                padding: 0;
                border-radius: var(--radius-sm);
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            .matriz-table {{
                border-spacing: 0;
                border-collapse: separate;
                min-width: 820px;
            }}
            .matriz-row-header {{
                position: sticky;
                left: 0;
                z-index: 20;
                background-color: var(--bg-card) !important;
                width: 86px;
                min-width: 86px;
                max-width: 90px;
                padding: 8px 6px;
                box-shadow: 4px 0 10px rgba(0, 0, 0, 0.55);
                border-right: 2px solid var(--border);
                border-bottom: 2px solid var(--bg-body);
            }}
            .matriz-disc-name {{
                font-size: 0.58rem !important;
                max-width: 76px !important;
                line-height: 1.1;
                margin-top: 2px;
                color: var(--text-muted);
            }}
            .matriz-cell {{
                min-width: 44px;
                height: 42px;
                font-size: 0.74rem;
                padding: 4px 2px;
                border: 1px solid var(--border);
                border-bottom: 2px solid var(--bg-body);
                border-right: 2px solid var(--bg-body);
                box-sizing: border-box;
            }}

            /* 4. SEÇÃO ESTUDO DA META NO MOBILE */
            .meta-view-header {{
                padding: 12px 14px;
            }}
            .meta-breadcrumbs {{
                flex-wrap: wrap;
                font-size: 0.76rem;
                gap: 4px;
            }}
            .meta-header-row {{
                flex-direction: column;
                align-items: stretch;
                gap: 12px;
            }}
            .meta-header-titles h2 {{
                font-size: 1.15rem;
                flex-wrap: wrap;
            }}
            .btn-toggle-meta {{
                width: 100%;
                justify-content: center;
                padding: 12px 18px;
                font-size: 0.92rem;
            }}
            .meta-control-grid {{
                grid-template-columns: 1fr;
                gap: 12px;
            }}
            .meta-pdf-assuntos-card {{
                padding: 12px 14px;
            }}
            .meta-item-label {{
                padding: 10px 12px;
                font-size: 0.84rem;
            }}
            .questoes-inputs-row {{
                flex-wrap: wrap;
            }}
            .subtopicos-pills-container {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                flex-wrap: nowrap;
                padding-bottom: 4px;
            }}
            .subtopicos-pills-container::-webkit-scrollbar {{
                display: none;
            }}
            .subtopico-pill {{
                flex: 0 0 auto;
                white-space: nowrap;
                padding: 8px 12px;
                font-size: 0.80rem;
            }}

            /* 5. VISÃO DISCIPLINAS NO MOBILE */
            .disc-header-card {{
                padding: 12px 14px;
            }}
            .disc-filtro-pills {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
                flex-wrap: nowrap;
                padding-bottom: 4px;
            }}
            .disc-filtro-pills::-webkit-scrollbar {{
                display: none;
            }}
            .disc-filtro-pill {{
                flex: 0 0 auto;
                white-space: nowrap;
            }}
            .disc-metas-cards-grid {{
                grid-template-columns: 1fr !important;
            }}
        }}

        @media (max-width: 480px) {{
            .topbar-progress-bar {{
                display: none; /* Em telas < 480px, mantém o número mas esconde a barra gráfica para caber tudo */
            }}
            .topbar-title h1 {{
                font-size: 0.80rem;
            }}
            .topbar-tab-btn {{
                padding: 5px 8px;
                font-size: 0.74rem;
            }}
            .matriz-row-header {{
                width: 78px;
                min-width: 78px;
                max-width: 82px;
                padding: 4px 4px;
            }}
            .matriz-disc-name {{
                font-size: 0.55rem !important;
                max-width: 68px !important;
            }}
        }}

        /* ==========================================================================
           MODO MOBILE FORÇADO (CLASSE .layout-mobile)
           Garante visualização mobile perfeita independente de alternância desktop no navegador
           ========================================================================== */
        html.layout-mobile .hide-mobile {{ display: none !important; }}
        html.layout-mobile .topbar {{ padding: 6px 10px; position: sticky; top: 0; }}
        html.layout-mobile .topbar-main-row {{ flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 6px; }}
        html.layout-mobile .topbar-brand {{ order: 1; gap: 8px; }}
        html.layout-mobile .topbar-logo {{ width: 34px; height: 34px; border-radius: 10px; }}
        html.layout-mobile .topbar-logo-badge {{ font-size: 0.95rem; }}
        html.layout-mobile .topbar-title h1 {{ font-size: 0.84rem; margin: 0; }}
        html.layout-mobile .topbar-title p {{ display: none; }}
        html.layout-mobile .topbar-cycle-group {{ order: 2; display: flex; align-items: center; gap: 6px; margin: 0; }}
        html.layout-mobile .topbar-progress-wrap {{ padding: 3px 8px; gap: 6px; }}
        html.layout-mobile .topbar-progress-text {{ font-size: 0.70rem; }}
        html.layout-mobile .topbar-progress-bar {{ width: 50px; height: 5px; }}
        html.layout-mobile .btn-next-cycle {{ padding: 5px 10px; font-size: 0.74rem; border-radius: 16px; }}
        html.layout-mobile .btn-next-cycle span {{ white-space: nowrap; }}
        .show-mobile-only {{ display: none; }}
        html.layout-mobile .show-mobile-only {{ display: inline !important; }}
        html.layout-mobile .hide-mobile {{ display: none !important; }}
        html.layout-mobile .topbar-tabs {{ order: 3; width: 100%; display: flex; justify-content: space-between; align-items: stretch; gap: 3px; padding: 3px 0; margin-top: 4px; overflow-x: visible; }}
        html.layout-mobile .topbar-tabs::-webkit-scrollbar {{ display: none; }}
        html.layout-mobile .topbar-tab-btn {{ flex: 1 1 0; min-width: 0; white-space: nowrap; padding: 6px 2px; font-size: 0.72rem; font-weight: 700; text-align: center; border-radius: 7px; display: flex; align-items: center; justify-content: center; gap: 2px; }}
        html.layout-mobile .topbar-subrow {{ flex-direction: column; align-items: stretch; gap: 6px; padding-top: 5px; margin-top: 4px; }}
        html.layout-mobile .topbar-tools {{ display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 4px; overflow-x: visible; padding-bottom: 2px; }}
        html.layout-mobile .topbar-tools::-webkit-scrollbar {{ display: none; }}
        html.layout-mobile .pomo-badge {{ padding: 3px 5px; font-size: 0.72rem; gap: 3px; flex-shrink: 0; }}
        html.layout-mobile .pomo-badge .btn-tool {{ padding: 2px 4px; font-size: 0.68rem; }}
        html.layout-mobile .theme-select {{ padding: 3px 4px; font-size: 0.70rem; flex-shrink: 0; }}
        html.layout-mobile .btn-layout-toggle {{ padding: 3px 6px; font-size: 0.72rem; flex-shrink: 0; display: inline-flex !important; align-items: center; }}
        html.layout-mobile .btn-layout-toggle #layout-toggle-text {{ display: none; }}
        html.layout-mobile .btn-cloud-sync {{ padding: 3px 7px; font-size: 0.72rem; font-weight: 700; flex-shrink: 0; white-space: nowrap; max-width: none !important; overflow: visible !important; display: inline-flex !important; align-items: center; gap: 4px; }}
        html.layout-mobile .topbar-search-container {{ width: 100% !important; max-width: 100% !important; min-width: 0 !important; margin: 0; }}
        html.layout-mobile .search-input-box {{ height: 34px; }}
        html.layout-mobile .topbar-subrow-spacer {{ display: none !important; }}
        html.layout-mobile .search-dropdown-results {{ width: 100%; left: 0; right: 0; max-width: 100%; }}
        html.layout-mobile .main-container {{ padding: 8px 8px 50px 8px; }}
        html.layout-mobile .quadro-header-banner {{ padding: 8px 10px; flex-direction: column; align-items: stretch; gap: 8px; }}
        html.layout-mobile .quadro-header-info {{ display: flex; justify-content: space-between; align-items: center; }}
        html.layout-mobile .quadro-banner-controls {{ width: 100%; }}
        html.layout-mobile .quadro-filtros {{ display: flex; width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; flex-wrap: nowrap; gap: 6px; }}
        html.layout-mobile .quadro-filtros::-webkit-scrollbar {{ display: none; }}
        html.layout-mobile .filtro-btn {{ flex: 0 0 auto; padding: 5px 12px; font-size: 0.74rem; white-space: nowrap; }}
        html.layout-mobile .matriz-container {{ padding: 0; border-radius: var(--radius-sm); overflow-x: auto; -webkit-overflow-scrolling: touch; }}
        html.layout-mobile .matriz-table {{ border-spacing: 0; border-collapse: separate; min-width: 820px; }}
        html.layout-mobile .matriz-row-header {{ position: sticky; left: 0; z-index: 20; background-color: var(--bg-card) !important; width: 86px; min-width: 86px; max-width: 90px; padding: 8px 6px; box-shadow: 4px 0 10px rgba(0, 0, 0, 0.55); border-right: 2px solid var(--border); border-bottom: 2px solid var(--bg-body); }}
        html.layout-mobile .matriz-disc-name {{ font-size: 0.58rem !important; max-width: 76px !important; line-height: 1.1; margin-top: 2px; color: var(--text-muted); }}
        html.layout-mobile .matriz-cell {{ min-width: 44px; height: 42px; font-size: 0.74rem; padding: 4px 2px; border: 1px solid var(--border); border-bottom: 2px solid var(--bg-body); border-right: 2px solid var(--bg-body); box-sizing: border-box; }}
        html.layout-mobile .meta-view-header {{ padding: 12px 14px; }}
        html.layout-mobile .meta-breadcrumbs {{ flex-wrap: wrap; font-size: 0.76rem; gap: 4px; }}
        html.layout-mobile .meta-header-row {{ flex-direction: column; align-items: stretch; gap: 12px; }}
        html.layout-mobile .meta-header-titles h2 {{ font-size: 1.15rem; flex-wrap: wrap; }}
        html.layout-mobile .btn-toggle-meta {{ width: 100%; justify-content: center; padding: 12px 18px; font-size: 0.92rem; }}
        html.layout-mobile .meta-control-grid {{ grid-template-columns: 1fr; gap: 12px; }}
        html.layout-mobile .meta-pdf-assuntos-card {{ padding: 12px 14px; }}
        html.layout-mobile .meta-item-label {{ padding: 10px 12px; font-size: 0.84rem; }}
        html.layout-mobile .questoes-inputs-row {{ flex-wrap: wrap; }}
        html.layout-mobile .subtopicos-pills-container {{ overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; flex-wrap: nowrap; padding-bottom: 4px; }}
        html.layout-mobile .subtopicos-pills-container::-webkit-scrollbar {{ display: none; }}
        html.layout-mobile .subtopico-pill {{ flex: 0 0 auto; white-space: nowrap; padding: 8px 12px; font-size: 0.80rem; }}
        html.layout-mobile .disc-header-card {{ padding: 12px 14px; }}
        html.layout-mobile .disc-filtro-pills {{ overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; flex-wrap: nowrap; padding-bottom: 4px; }}
        html.layout-mobile .disc-filtro-pills::-webkit-scrollbar {{ display: none; }}
        html.layout-mobile .disc-filtro-pill {{ flex: 0 0 auto; white-space: nowrap; }}
        html.layout-mobile .disc-metas-cards-grid {{ grid-template-columns: 1fr !important; }}

        html.layout-mobile.is-small-mobile .topbar-progress-bar {{ display: none; }}
        html.layout-mobile.is-small-mobile .topbar-title h1 {{ font-size: 0.80rem; }}
        html.layout-mobile.is-small-mobile .topbar-tab-btn {{ padding: 5px 8px; font-size: 0.74rem; }}
        html.layout-mobile.is-small-mobile .matriz-row-header {{ width: 78px; min-width: 78px; max-width: 82px; padding: 4px 4px; }}
        html.layout-mobile.is-small-mobile .matriz-disc-name {{ font-size: 0.55rem !important; max-width: 68px !important; }}

        /* ESTILO DO BOTÃO DE ALTERNÂNCIA DE LAYOUT */
        .btn-layout-toggle {{
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.35);
            color: #93c5fd;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        .btn-layout-toggle:hover {{
            background: rgba(59, 130, 246, 0.25);
            border-color: #60a5fa;
            color: #ffffff;
        }}

        /* =====================================================================
           ESTILOS DO PAINEL MEU EDITAL (TJAA vs AJAJ)
           ===================================================================== */
        .edital-section {{
            display: flex;
            flex-direction: column;
            gap: 18px;
            animation: fadeIn 0.25s ease-out;
        }}

        .edital-header-banner {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
            border: 1px solid var(--border);
            border-left: 4px solid #38bdf8;
            border-radius: var(--radius-md);
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 14px;
            box-shadow: var(--shadow);
        }}

        .edital-header-info h2 {{
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--text-heading);
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0;
        }}

        .edital-header-info p {{
            font-size: 0.84rem;
            color: var(--text-muted);
            margin: 4px 0 0 0;
        }}



        /* CARGO SELECTOR TABS */
        .edital-cargo-tabs {{
            display: flex;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 4px;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .edital-cargo-tab-btn {{
            flex: 1 1 auto;
            min-width: 150px;
            padding: 10px 18px;
            font-size: 0.86rem;
            font-weight: 700;
            border: 1px solid transparent;
            background: transparent;
            color: var(--text-muted);
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}

        .edital-cargo-tab-btn:hover {{
            color: var(--text-heading);
            background: rgba(255, 255, 255, 0.05);
        }}

        .edital-cargo-tab-btn.active-tjaa {{
            background: linear-gradient(135deg, #1d4ed8, #2563eb);
            color: #ffffff;
            border-color: #3b82f6;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        }}

        .edital-cargo-tab-btn.active-ajaj {{
            background: linear-gradient(135deg, #6d28d9, #7c3aed);
            color: #ffffff;
            border-color: #8b5cf6;
            box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4);
        }}

        .edital-cargo-tab-btn.active-comp {{
            background: linear-gradient(135deg, #0f766e, #0d9488);
            color: #ffffff;
            border-color: #14b8a6;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.4);
        }}

        /* DASHBOARD KPI CARDS */
        .edital-kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
        }}

        .edital-kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }}

        .edital-kpi-card:hover {{
            border-color: var(--border-light);
            transform: translateY(-2px);
        }}

        .edital-kpi-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .edital-kpi-main {{
            display: flex;
            align-items: baseline;
            gap: 8px;
        }}

        .edital-kpi-value {{
            font-size: 1.85rem;
            font-weight: 900;
            color: var(--text-heading);
            line-height: 1;
        }}

        .edital-kpi-sub {{
            font-size: 0.80rem;
            color: var(--text-muted);
        }}

        .edital-progress-bar-wrap {{
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 999px;
            overflow: hidden;
            margin-top: 4px;
        }}

        .edital-progress-bar-fill {{
            height: 100%;
            border-radius: 999px;
            transition: width 0.4s ease;
        }}

        /* CONTROLS & FILTERS */
        .edital-controls-bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 10px 14px;
        }}

        .edital-search-box {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 6px 12px;
            flex: 1 1 260px;
        }}

        .edital-search-input {{
            background: transparent;
            border: none;
            color: var(--text-heading);
            font-size: 0.84rem;
            outline: none;
            width: 100%;
        }}

        .edital-filter-pills {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .edital-filter-btn {{
            padding: 6px 12px;
            font-size: 0.76rem;
            font-weight: 700;
            border-radius: 20px;
            border: 1px solid var(--border);
            background: var(--bg-surface);
            color: var(--text-muted);
            cursor: pointer;
            transition: var(--transition);
        }}

        .edital-filter-btn:hover {{
            color: var(--text-heading);
            border-color: var(--border-light);
        }}

        .edital-filter-btn.active {{
            background: var(--primary-alpha);
            border-color: var(--primary);
            color: #60a5fa;
        }}

        /* ACCORDIONS DE DISCIPLINAS */
        .edital-disc-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow);
            margin-bottom: 12px;
            transition: var(--transition);
        }}

        .edital-disc-header {{
            padding: 14px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(255, 255, 255, 0.015);
            cursor: pointer;
            user-select: none;
            transition: var(--transition);
        }}

        .edital-disc-header:hover {{
            background: rgba(255, 255, 255, 0.04);
        }}

        .edital-disc-title-wrap {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .edital-disc-sigla-badge {{
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.5px;
        }}

        .edital-disc-name {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-heading);
        }}

        .edital-disc-stats {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .edital-disc-counter {{
            font-size: 0.80rem;
            font-weight: 700;
            color: var(--text-muted);
        }}

        .edital-disc-bar-wrap {{
            width: 80px;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 999px;
            overflow: hidden;
        }}

        .edital-disc-chevron {{
            font-size: 0.85rem;
            color: var(--text-muted);
            transition: transform 0.25s ease;
        }}

        .edital-disc-card.collapsed .edital-disc-chevron {{
            transform: rotate(-90deg);
        }}

        .edital-disc-card.collapsed .edital-disc-body {{
            display: none;
        }}

        .edital-disc-body {{
            border-top: 1px solid var(--border);
            padding: 8px 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        /* TOPIC ROW */
        .edital-topic-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            gap: 12px;
            transition: var(--transition);
        }}

        .edital-topic-row:hover {{
            border-color: var(--border-light);
            background: var(--bg-card-hover);
        }}

        .edital-topic-row.is-done {{
            background: rgba(16, 185, 129, 0.06);
            border-color: rgba(16, 185, 129, 0.25);
        }}

        .edital-topic-left {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            flex: 1 1 auto;
        }}

        .edital-topic-chk {{
            appearance: none;
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border: 2px solid var(--border-light);
            border-radius: 6px;
            background: var(--bg-card);
            cursor: pointer;
            flex-shrink: 0;
            margin-top: 2px;
            display: grid;
            place-content: center;
            transition: var(--transition);
        }}

        .edital-topic-chk:checked {{
            background: #10b981;
            border-color: #10b981;
        }}

        .edital-topic-chk:checked::before {{
            content: "✓";
            font-size: 13px;
            font-weight: 900;
            color: white;
        }}

        .edital-topic-content {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .edital-topic-title {{
            font-size: 0.86rem;
            font-weight: 600;
            color: var(--text-heading);
            line-height: 1.4;
        }}

        .edital-topic-row.is-done .edital-topic-title {{
            color: #94a3b8;
            text-decoration: line-through;
            text-decoration-color: rgba(16, 185, 129, 0.5);
        }}

        .edital-topic-badges {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .edital-meta-btn {{
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
            padding: 2px 8px;
            border-radius: 5px;
            font-size: 0.72rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .edital-meta-btn:hover {{
            background: rgba(56, 189, 248, 0.28);
            border-color: #38bdf8;
            transform: translateY(-1px);
        }}

        .edital-meta-btn.meta-done {{
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.4);
            color: #34d399;
        }}

        .edital-exclusive-badge {{
            background: rgba(168, 85, 247, 0.12);
            border: 1px solid rgba(168, 85, 247, 0.3);
            color: #c084fc;
            padding: 2px 7px;
            border-radius: 5px;
            font-size: 0.70rem;
            font-weight: 700;
        }}

        .edital-status-tag {{
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .edital-status-tag.done {{
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .edital-status-tag.pending {{
            background: rgba(245, 158, 11, 0.12);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        /* COMPARATIVO ESTILOS */
        .comp-card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}

        .comp-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 18px;
            box-shadow: var(--shadow);
        }}

        .comp-table-wrap {{
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
        }}

        .comp-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.84rem;
        }}

        .comp-table th {{
            text-align: left;
            padding: 10px 12px;
            background: var(--bg-surface);
            color: var(--text-muted);
            font-weight: 700;
            border-bottom: 1px solid var(--border);
        }}

        .comp-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            color: var(--text-body);
        }}

        .comp-badge-tronco {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 700;
        }}

        .comp-badge-tjaa {{
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 700;
        }}

        .comp-badge-ajaj {{
            background: rgba(168, 85, 247, 0.15);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.3);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 700;
        }}

        /* MOBILE ADJUSTMENTS PARA O EDITAL */
        html.layout-mobile .edital-section {{ gap: 12px; }}
        html.layout-mobile .edital-header-banner {{ padding: 12px; flex-direction: column; align-items: stretch; }}
        html.layout-mobile .edital-cargo-tabs {{ flex-direction: column; }}
        html.layout-mobile .edital-kpi-grid {{ grid-template-columns: 1fr 1fr; gap: 8px; }}
        html.layout-mobile .edital-kpi-card {{ padding: 10px; }}
        html.layout-mobile .edital-kpi-value {{ font-size: 1.35rem; }}
        html.layout-mobile .edital-controls-bar {{ flex-direction: column; align-items: stretch; gap: 8px; }}
        html.layout-mobile .edital-search-box {{ flex: 0 0 auto; width: 100%; box-sizing: border-box; }}
        html.layout-mobile .edital-disc-header {{ padding: 10px 12px; }}
        html.layout-mobile .edital-disc-bar-wrap {{ display: none; }}
        html.layout-mobile .edital-topic-row {{ flex-direction: column; align-items: stretch; gap: 8px; }}
        html.layout-mobile .edital-status-tag {{ align-self: flex-start; }}
        html.layout-mobile .comp-card-grid {{ grid-template-columns: 1fr; }}


        /* BARRA DE ROLAGEM E NAVEGAÇÃO DA MATRIZ */
        .matriz-scroll-hint-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 12px;
            margin-bottom: 8px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            font-size: 0.76rem;
            color: var(--text-muted);
        }}
        .matriz-hint-text {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
        }}
        .matriz-nav-arrows {{
            display: flex;
            gap: 6px;
        }}
        .btn-scroll-arrow {{
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.35);
            color: #93c5fd;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
        }}
        .btn-scroll-arrow:hover {{
            background: rgba(59, 130, 246, 0.28);
            color: #ffffff;
            border-color: #60a5fa;
        }}

        /* SCROLLBAR VISÍVEL E TOUCH NATIVO NA MATRIZ */
        .matriz-container {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 8px 12px;
            box-shadow: var(--shadow);
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            touch-action: pan-x pan-y !important;
            overscroll-behavior-x: contain !important;
            cursor: grab;
            position: relative;
        }}
        .matriz-container.is-dragging {{
            cursor: grabbing;
            user-select: none;
        }}
        .matriz-container::-webkit-scrollbar {{
            height: 8px;
            display: block !important;
        }}
        .matriz-container::-webkit-scrollbar-track {{
            background: rgba(0, 0, 0, 0.3);
            border-radius: 999px;
            margin: 0 10px;
        }}
        .matriz-container::-webkit-scrollbar-thumb {{
            background: linear-gradient(90deg, #2563eb, #38bdf8);
            border-radius: 999px;
        }}
        .matriz-container::-webkit-scrollbar-thumb:hover {{
            background: #60a5fa;
        }}

        html.layout-mobile .matriz-scroll-hint-bar {{
            padding: 5px 8px;
            font-size: 0.72rem;
            margin-bottom: 6px;
        }}
        html.layout-mobile .matriz-container {{
            padding: 0;
            border-radius: var(--radius-sm);
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            touch-action: pan-x pan-y !important;
            overscroll-behavior-x: contain !important;
        }}
        html.layout-mobile .matriz-table {{
            border-spacing: 0;
            border-collapse: separate;
            min-width: 860px;
            touch-action: pan-x pan-y !important;
        }}
        html.layout-mobile .matriz-row-header {{
            position: sticky !important;
            left: 0 !important;
            z-index: 25 !important;
            background-color: var(--bg-card) !important;
            width: 86px;
            min-width: 86px;
            max-width: 90px;
            padding: 8px 6px;
            box-shadow: 4px 0 14px rgba(0, 0, 0, 0.75) !important;
            border-right: 2px solid var(--border) !important;
            border-bottom: 2px solid var(--bg-body) !important;
        }}
        html.layout-mobile .matriz-cell {{
            touch-action: pan-x pan-y !important;
        }}

        /* ==========================================================================
           SIDEBAR DE TRIBUNAIS (TRTs)
           ========================================================================== */
        .btn-trt-pill {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.70rem;
            font-weight: 700;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            padding: 3px 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            vertical-align: middle;
            text-decoration: none;
            line-height: 1.2;
            margin-left: 6px;
        }}
        .btn-trt-pill:hover {{
            background: rgba(56, 189, 248, 0.22);
            border-color: #38bdf8;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(56, 189, 248, 0.25);
        }}
        .btn-trt-pill .trt-arrow {{
            font-size: 0.6rem;
            opacity: 0.8;
            transition: transform 0.2s ease;
        }}
        .btn-trt-pill:hover .trt-arrow {{
            transform: translateY(1px);
        }}

        .sidebar-trt-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.72);
            backdrop-filter: blur(4px);
            opacity: 0;
            visibility: hidden;
            z-index: 9998;
            transition: opacity 0.25s ease, visibility 0.25s ease;
        }}
        .sidebar-trt-overlay.open {{
            opacity: 1;
            visibility: visible;
        }}

        .sidebar-trt {{
            position: fixed;
            top: 0;
            left: 0;
            bottom: 0;
            width: 360px;
            max-width: 88vw;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            box-shadow: 8px 0 32px rgba(0, 0, 0, 0.6);
            z-index: 9999;
            transform: translateX(-100%);
            transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .sidebar-trt.open {{
            transform: translateX(0);
        }}

        .sidebar-trt-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 18px;
            border-bottom: 1px solid var(--border);
            background: var(--bg-surface);
        }}
        .sidebar-trt-title-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .sidebar-trt-icon {{
            font-size: 1.5rem;
            line-height: 1;
        }}
        .sidebar-trt-title-group h2 {{
            font-size: 1rem;
            font-weight: 800;
            color: var(--text-heading);
            margin: 0;
            letter-spacing: -0.01em;
        }}
        .sidebar-trt-title-group p {{
            font-size: 0.68rem;
            color: var(--text-muted);
            margin: 2px 0 0 0;
        }}
        .sidebar-trt-close {{
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            width: 30px;
            height: 30px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.15s ease;
        }}
        .sidebar-trt-close:hover {{
            color: var(--text-heading);
            background: rgba(239, 68, 68, 0.15);
            border-color: #ef4444;
        }}

        .sidebar-trt-body {{
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        /* CARD ATUAL */
        .sidebar-trt-current-card {{
            background: linear-gradient(145deg, rgba(56, 189, 248, 0.1), rgba(129, 140, 248, 0.05));
            border: 1.5px solid rgba(56, 189, 248, 0.35);
            border-radius: 12px;
            padding: 14px;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.1);
        }}
        .current-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .current-pill {{
            font-size: 0.62rem;
            font-weight: 800;
            color: #10b981;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 7px;
            border-radius: 12px;
            letter-spacing: 0.04em;
        }}
        .current-badge {{
            font-size: 0.78rem;
            font-weight: 800;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.15);
            padding: 2px 8px;
            border-radius: 6px;
        }}
        .sidebar-trt-current-card h3 {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--text-heading);
            margin: 0 0 8px 0;
        }}
        .current-details {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}
        .current-details strong {{
            color: var(--text-heading);
        }}
        .current-actions {{
            display: flex;
            gap: 8px;
        }}
        .btn-sidebar-quick {{
            flex: 1;
            padding: 6px 10px;
            font-size: 0.72rem;
            font-weight: 700;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--bg-surface);
            color: var(--text-heading);
            cursor: pointer;
            transition: all 0.15s ease;
            text-align: center;
        }}
        .btn-sidebar-quick:hover {{
            background: var(--border);
            border-color: #38bdf8;
        }}

        /* SEÇÃO LISTA */
        .sidebar-section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.68rem;
            font-weight: 800;
            color: var(--text-muted);
            letter-spacing: 0.05em;
            padding: 0 2px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 6px;
        }}
        .sidebar-trt-count {{
            background: var(--bg-surface);
            padding: 1px 6px;
            border-radius: 8px;
            font-size: 0.62rem;
            border: 1px solid var(--border);
        }}
        .sidebar-trt-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .sidebar-trt-item {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            transition: all 0.2s ease;
        }}
        .sidebar-trt-item:hover {{
            border-color: rgba(56, 189, 248, 0.4);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        .sidebar-trt-item.is-active {{
            border-color: rgba(16, 185, 129, 0.5);
            background: rgba(16, 185, 129, 0.04);
        }}
        .trt-item-left {{
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
            flex: 1;
        }}
        .trt-item-badge {{
            font-size: 0.75rem;
            font-weight: 800;
            padding: 4px 8px;
            border-radius: 6px;
            white-space: nowrap;
            letter-spacing: -0.02em;
        }}
        .badge-trt-blue {{
            background: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}
        .badge-trt-purple {{
            background: rgba(168, 85, 247, 0.15);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }}
        .badge-trt-amber {{
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        .badge-trt-emerald {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        .trt-item-info {{
            min-width: 0;
        }}
        .trt-item-title {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-heading);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
        }}
        .trt-item-sub {{
            font-size: 0.65rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .trt-item-actions {{
            display: flex;
            align-items: center;
            gap: 6px;
            flex-shrink: 0;
        }}
        .btn-trt-action {{
            padding: 4px 8px;
            font-size: 0.68rem;
            font-weight: 700;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text-heading);
            cursor: pointer;
            transition: all 0.15s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .btn-trt-action:hover {{
            border-color: #38bdf8;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
        }}
        .btn-trt-action.btn-trt-current {{
            border-color: rgba(16, 185, 129, 0.4);
            color: #10b981;
            background: rgba(16, 185, 129, 0.08);
            cursor: default;
        }}
        .btn-trt-repo-link {{
            padding: 4px 6px;
            font-size: 0.8rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--bg-card);
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.15s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        .btn-trt-repo-link:hover {{
            border-color: #38bdf8;
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
        }}
        .btn-trt-delete {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 4px;
            font-size: 0.75rem;
            border-radius: 4px;
            transition: color 0.15s;
        }}
        .btn-trt-delete:hover {{
            color: #ef4444;
        }}

        /* FORM NOVO TRT */
        .sidebar-add-container {{
            margin-top: 4px;
        }}
        .btn-add-trt-toggle {{
            width: 100%;
            padding: 10px;
            font-size: 0.78rem;
            font-weight: 700;
            border-radius: 8px;
            border: 1.5px dashed rgba(56, 189, 248, 0.4);
            background: rgba(56, 189, 248, 0.05);
            color: #38bdf8;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        .btn-add-trt-toggle:hover {{
            background: rgba(56, 189, 248, 0.12);
            border-color: #38bdf8;
            transform: translateY(-1px);
        }}
        .form-novo-trt {{
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
            animation: fadeIn 0.2s ease;
        }}
        .form-novo-trt h4 {{
            font-size: 0.8rem;
            font-weight: 800;
            color: var(--text-heading);
            margin: 0;
        }}
        .form-row {{
            display: flex;
            gap: 8px;
        }}
        .form-col {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .form-novo-trt label {{
            font-size: 0.65rem;
            font-weight: 700;
            color: var(--text-muted);
        }}
        .form-novo-trt input, .form-novo-trt select {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 0.75rem;
            color: var(--text-heading);
            outline: none;
            transition: border-color 0.15s;
        }}
        .form-novo-trt input:focus, .form-novo-trt select:focus {{
            border-color: #38bdf8;
        }}
        .form-buttons {{
            display: flex;
            gap: 8px;
            margin-top: 4px;
        }}
        .btn-save-trt {{
            flex: 1;
            padding: 7px;
            font-size: 0.75rem;
            font-weight: 700;
            background: #0284c7;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.15s;
        }}
        .btn-save-trt:hover {{
            background: #0369a1;
        }}
        .btn-cancel-trt {{
            padding: 7px 12px;
            font-size: 0.75rem;
            font-weight: 600;
            background: var(--bg-card);
            color: var(--text-muted);
            border: 1px solid var(--border);
            border-radius: 6px;
            cursor: pointer;
        }}
        .btn-cancel-trt:hover {{
            color: var(--text-heading);
            border-color: var(--text-muted);
        }}

        .sidebar-trt-footer {{
            padding: 12px 16px;
            border-top: 1px solid var(--border);
            background: var(--bg-surface);
        }}
        .sidebar-repo-link {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-heading);
            text-decoration: none;
            padding: 8px 12px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            transition: all 0.2s ease;
        }}
        .sidebar-repo-link:hover {{
            border-color: #38bdf8;
            color: #38bdf8;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
        }}
    
    </style>
</head>
<body class="theme-dark">

    <!-- OVERLAY E SIDEBAR DE TRIBUNAIS (TRTs) -->
    <div id="sidebar-trt-overlay" class="sidebar-trt-overlay" onclick="fecharSidebarTRT()"></div>
    
    <aside id="sidebar-trt" class="sidebar-trt" aria-label="Painel de Tribunais TRT">
        <div class="sidebar-trt-header">
            <div class="sidebar-trt-title-group">
                <span class="sidebar-trt-icon">🏛️</span>
                <div>
                    <h2>Tribunais (TRTs)</h2>
                    <p>Caderno do TRT • Plataformas & Editais</p>
                </div>
            </div>
            <button class="sidebar-trt-close" onclick="fecharSidebarTRT()" title="Fechar Menu (Esc)">✕</button>
        </div>

        <div class="sidebar-trt-body">
            <!-- CARD DO TRIBUNAL ATUALMENTE ATIVO -->
            <div class="sidebar-trt-current-card" id="sidebar-current-card">
                <div class="current-card-header">
                    <span class="current-pill">● TRIBUNAL ATIVO</span>
                    <span class="current-badge" id="sidebar-current-badge">TRT-7 (CE)</span>
                </div>
                <h3 id="sidebar-current-nome">Tribunal Regional do Trabalho da 4ª Região</h3>
                <div class="current-details">
                    <span>🏢 Banca: <strong id="sidebar-current-banca">FCC</strong></span>
                    <span>🎯 Metas: <strong id="sidebar-current-metas">177</strong></span>
                    <span>📚 Cadernos: <strong id="sidebar-current-materias">10 Matérias</strong></span>
                </div>
                <div class="current-actions">
                    <button class="btn-sidebar-quick" onclick="abrirVisaoQuadro(); fecharSidebarTRT();">📊 Ir ao Quadro</button>
                    <button class="btn-sidebar-quick" onclick="abrirVisaoEdital(); fecharSidebarTRT();">📑 Ver Edital</button>
                </div>
            </div>

            <!-- SEÇÃO DE OUTROS TRTS -->
            <div class="sidebar-section-header">
                <span>MEUS TRIBUNAIS & EDITAIS</span>
                <span class="sidebar-trt-count" id="sidebar-trt-count">6 disponíveis</span>
            </div>

            <div class="sidebar-trt-list" id="sidebar-trt-list">
                <!-- Renderizado dinamicamente via JavaScript -->
            </div>

            <!-- BOTÃO ADICIONAR NOVO TRT -->
            <div class="sidebar-add-container">
                <button class="btn-add-trt-toggle" id="btn-add-trt-toggle" onclick="toggleFormNovoTRT()">
                    <span>➕ Adicionar Novo TRT</span>
                </button>
                
                <form id="form-novo-trt" class="form-novo-trt" onsubmit="salvarNovoTRT(event)" style="display: none;">
                    <h4>Cadastrar Novo Tribunal</h4>
                    <div class="form-row">
                        <div class="form-col">
                            <label>Região (Número)</label>
                            <input type="text" id="novo-trt-num" placeholder="Ex: 5, 6, 8" required>
                        </div>
                        <div class="form-col">
                            <label>UF / Estado</label>
                            <input type="text" id="novo-trt-uf" placeholder="Ex: BA, PE, PA" required maxlength="10">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Nome do Tribunal / Região</label>
                        <input type="text" id="novo-trt-regiao" placeholder="Ex: Bahia" required>
                    </div>
                    <div class="form-row">
                        <div class="form-col">
                            <label>Banca</label>
                            <select id="novo-trt-banca">
                                <option value="FCC">FCC</option>
                                <option value="Cebraspe">Cebraspe</option>
                                <option value="FGV">FGV</option>
                                <option value="Vunesp">Vunesp</option>
                                <option value="Outra">Outra</option>
                            </select>
                        </div>
                        <div class="form-col">
                            <label>Status</label>
                            <select id="novo-trt-status">
                                <option value="Disponível">Disponível</option>
                                <option value="Em Estudo">Em Estudo</option>
                                <option value="Planejamento">Planejamento</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Link da Plataforma / Pasta (Opcional)</label>
                        <input type="url" id="novo-trt-url" placeholder="https://... ou caminho local">
                    </div>
                    <div class="form-buttons">
                        <button type="submit" class="btn-save-trt">Salvar Tribunal</button>
                        <button type="button" class="btn-cancel-trt" onclick="toggleFormNovoTRT(false)">Cancelar</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- RODAPÉ DA SIDEBAR -->
        <div class="sidebar-trt-footer">
            <a href="https://github.com/daniellucas2025/caderno-do-trt" target="_blank" rel="noopener noreferrer" class="sidebar-repo-link">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                <span>Repositório Oficial CADERNO DO TRT ↗</span>
            </a>
        </div>
    </aside>

    <!-- TOPBAR -->
    <header class="topbar">
        <!-- LINHA 1 DA TOPBAR: MARCA, NAVEGAÇÃO E CICLO -->
        <div class="topbar-main-row">
            <!-- MARCA ESTUDOS DL -->
            <div class="topbar-brand" title="Estudos DL • Quadro de Metas">
                <div class="topbar-logo" onclick="abrirVisaoQuadro()" style="cursor: pointer;">
                    <span class="topbar-logo-badge">DL</span>
                </div>
                <div class="topbar-title">
                    <div style="display: flex; align-items: center; gap: 4px;">
                        <h1 onclick="abrirVisaoQuadro()" style="cursor: pointer; margin: 0;">Estudos DL</h1>
                        <button class="btn-trt-pill" id="btn-trt-pill" onclick="toggleSidebarTRT(event)" title="Abrir Menu de Tribunais (TRTs)">
                            <span class="trt-icon">🏛️</span>
                            <span class="trt-text">TRT-7</span>
                            <span class="trt-arrow">▾</span>
                        </button>
                    </div>
                    <p onclick="abrirVisaoQuadro()" style="cursor: pointer; margin: 0;">Metas de Estudos • Caderno do Aprovado</p>
                </div>
            </div>

            <!-- ABAS DE NAVEGAÇÃO -->
            <nav class="topbar-tabs">
                <button class="topbar-tab-btn active" id="tab-btn-quadro" onclick="abrirVisaoQuadro()">📊 Quadro <span class="hide-mobile">de Metas</span></button>
                <button class="topbar-tab-btn" id="tab-btn-estudo" onclick="abrirVisaoEstudo()">🎯 Estudo <span class="hide-mobile">da Meta</span></button>
                <button class="topbar-tab-btn" id="tab-btn-disciplinas" onclick="abrirVisaoDisciplinas()">📚 <span class="hide-mobile">Disciplinas</span><span class="show-mobile-only">Matérias</span></button>
                <button class="topbar-tab-btn" id="tab-btn-diag" onclick="abrirVisaoDiagnostico()">📋 <span class="hide-mobile">O que Falta?</span><span class="show-mobile-only">Faltas</span></button>
                <button class="topbar-tab-btn" id="tab-btn-edital" onclick="abrirVisaoEdital()">📑 <span class="hide-mobile">Meu </span>Edital</button>
            </nav>

            <!-- CICLO & PROGRESSO -->
            <div class="topbar-cycle-group">
                <div class="topbar-progress-wrap">
                    <span class="topbar-progress-text" id="topbar-metas-txt">0 / 170 (0%)</span>
                    <div class="topbar-progress-bar">
                        <div class="topbar-progress-fill" id="topbar-progress-fill"></div>
                    </div>
                </div>

                <button class="btn-next-cycle" onclick="irParaProximaMeta()">
                    <span>▶ Continuar Ciclo</span>
                </button>
            </div>
        </div>

        <!-- LINHA 2 DA TOPBAR: FERRAMENTAS À ESQUERDA + BUSCA CENTRALIZADA -->
        <div class="topbar-subrow">
            <!-- FERRAMENTAS À ESQUERDA -->
            <div class="topbar-tools">
                <div class="pomo-badge">
                    <span>⏱</span>
                    <span id="pomo-timer-val">25:00</span>
                    <button class="btn-tool" id="btn-pomo-toggle" onclick="togglePomodoro()">▶</button>
                    <button class="btn-tool" onclick="resetPomodoro()">⟲</button>
                </div>

                <select class="theme-select" onchange="mudarTema(this.value)">
                    <option value="dark">Dark</option>
                    <option value="amoled">AMOLED</option>
                    <option value="sepia">Sépia</option>
                    <option value="light">Claro</option>
                </select>

                <!-- SINCRONIZAÇÃO NUVEM COM GOOGLE -->
                <button class="btn-cloud-sync" id="btn-cloud-sync" onclick="tratarCliqueNuvem()" title="Sincronização em Nuvem (Google Firebase)">
                    <span id="cloud-sync-icon">☁️</span>
                    <span id="cloud-sync-text">Conectar Google</span>
                </button>

                <!-- ALTERNADOR DE MODO VISUAL (CELULAR / COMPUTADOR) -->
                <button class="btn-tool btn-layout-toggle" id="btn-layout-toggle" onclick="alternarModoVisual()" title="Alternar Modo de Visualização (Celular / Computador)">
                    <span id="layout-toggle-icon">📱</span>
                    <span id="layout-toggle-text">Celular</span>
                </button>

                <button class="btn-tool btn-pwa-install" id="btn-pwa-install" onclick="instalarPwa()" style="display:none;" title="Instalar Aplicativo no Celular ou Computador">📲 Instalar App</button>
            </div>

            <!-- CAMPO DE BUSCA CENTRALIZADO -->
            <div class="topbar-search-container">
                <div class="search-input-box">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="global-search-input" class="topbar-search-input" 
                           placeholder="Buscar por tópico, lei, meta ou conteúdo... (Ctrl+K)" 
                           autocomplete="off" oninput="executarBuscaGlobal(this.value)">
                    <button class="btn-clear-search" id="btn-clear-search" onclick="limparBusca()" style="display:none;" title="Limpar busca">×</button>
                    <span class="search-shortcut-hint">/</span>
                </div>
                <div class="search-dropdown-results" id="search-dropdown-results" style="display:none;"></div>
            </div>

            <!-- ESPAÇADOR DIREITO PARA EQUILÍBRIO VISUAL DA BUSCA CENTRALIZADA -->
            <div class="topbar-subrow-spacer"></div>
        </div>
    </header>

    <!-- ÁREA PRINCIPAL -->
    <main class="main-container">

        <!-- 1. VISÃO: QUADRO DE METAS (MATRIZ DO CICLO) -->
        <section class="quadro-section" id="view-quadro">
            <div class="quadro-header-banner">
                <div class="quadro-header-info">
                    <h2>📊 Quadro de Metas</h2>
                    <span style="font-size:0.75rem; color:var(--text-muted); font-weight:600;">• Ciclo Oficial TRT-7</span>
                </div>
                <div class="quadro-banner-controls">
                    <div class="quadro-filtros">
                        <button class="filtro-btn active" id="btn-filtro-todos" onclick="filtrarQuadro('todos')">Todas</button>
                        <button class="filtro-btn" id="btn-filtro-prio" onclick="filtrarQuadro('prio')">★ Prioritárias</button>
                        <button class="filtro-btn" id="btn-filtro-rev" onclick="filtrarQuadro('rev')">🟢 Revisões</button>
                        <button class="filtro-btn filtro-extra" id="btn-filtro-extra" onclick="filtrarQuadro('extra')">⭐ Extras</button>
                    </div>
                </div>
            </div>

            <!-- BARRA DE ROLAGEM HORIZONTAL DAS METAS (DISCIPLINAS FIXAS) -->
            <div class="matriz-scroll-hint-bar">
                <span class="matriz-hint-text">↔️ Deslize para ver as 24 metas (disciplinas fixas à esquerda)</span>
                <div class="matriz-nav-arrows">
                    <button class="btn-scroll-arrow" onclick="rolarMatrizQuadro(-240)" title="Rolar para metas anteriores">◀ Metas</button>
                    <button class="btn-scroll-arrow" onclick="rolarMatrizQuadro(240)" title="Rolar para próximas metas">Metas ▶</button>
                </div>
            </div>

            <div class="matriz-container" id="matriz-container-el">
                <table class="matriz-table" id="matriz-metas-table">
                    <!-- Gerado via JavaScript -->
                </table>
            </div>


        </section>

        <!-- 2. VISÃO: ESTUDO DA META -->
        <section class="meta-view-section" id="view-estudo">
            <div class="meta-view-header" id="meta-view-header-el">
                <div class="meta-breadcrumbs">
                    <a onclick="abrirVisaoQuadro()">🏠 Quadro de Metas</a>
                    <span>&gt;</span>
                    <span id="breadcrumb-disc-nome">Direito Constitucional</span>
                    <span>&gt;</span>
                    <strong id="breadcrumb-meta-nome">Meta 1</strong>
                </div>

                <div class="meta-header-row">
                    <div class="meta-header-titles">
                        <h2 id="meta-card-title">🎯 Meta 1 — Direito Constitucional</h2>
                        <span class="badge-subtitulo" id="meta-badge-subtitulo" style="display:none;"></span>
                        <span class="badge-star" id="meta-badge-star" style="display:none;">★ Prioritária no Edital</span>
                        <span class="badge-rev" id="meta-badge-rev" style="display:none;">🟢 Revisão Estratégica</span>
                        <span class="badge-extra" id="meta-badge-extra" style="display:none;">⭐ Meta Extra</span>
                    </div>

                    <button class="btn-toggle-meta" id="btn-toggle-meta-status" onclick="toggleMetaAtualConcluida()">
                        <span id="btn-toggle-meta-icon">⚪</span>
                        <span id="btn-toggle-meta-txt">Marcar como Concluída</span>
                    </button>
                </div>
            </div>

            <!-- CARD OFICIAL DE TÓPICOS DO PDF -->
            <div class="meta-pdf-assuntos-card" id="card-pdf-assuntos">
                <div class="meta-pdf-assuntos-header">
                    <span>📖 Em cada meta, estude os seguintes tópicos no Caderno do Aprovado:</span>
                </div>
                <ul class="meta-pdf-assuntos-list" id="lista-pdf-assuntos-el">
                    <!-- Tópicos do PDF gerados dinamicamente -->
                </ul>
            </div>

            <!-- CONTROLE DE QUESTÕES E CADERNO DE ERROS -->
            <div class="meta-control-grid">
                <!-- RASTREADOR DE QUESTÕES -->
                <div class="meta-widget-card">
                    <div class="meta-widget-title">📝 Questões da Meta</div>
                    <div class="questoes-inputs-row">
                        <div class="questoes-field">
                            <label>Feitas</label>
                            <input type="number" min="0" id="input-questoes-feitas" placeholder="0" oninput="salvarQuestoesMeta()">
                        </div>
                        <div class="questoes-field">
                            <label>Acertos</label>
                            <input type="number" min="0" id="input-questoes-acertos" placeholder="0" oninput="salvarQuestoesMeta()">
                        </div>
                        <div class="questoes-stat-badge">
                            <span style="font-size:0.68rem; color:var(--text-muted); font-weight:700;">ACERTO</span>
                            <span class="questoes-stat-val" id="questoes-pct-val">0%</span>
                        </div>
                    </div>
                </div>

                <!-- MINI CADERNO DE ERROS DA META -->
                <div class="meta-widget-card">
                    <div class="meta-widget-title">💡 Caderno de Erros & Pegadinhas</div>
                    <textarea class="caderno-erros-area" id="input-caderno-erros" placeholder="Anote pegadinhas da banca, artigos que você errou ou mnemônicos..." oninput="salvarCadernoErrosMeta()"></textarea>
                </div>
            </div>

            <!-- BLOCO ESPECIAL SE FOR META DE REVISÃO -->
            <div class="revisao-box" id="box-meta-revisao" style="display:none;">
                <h3>🟢 Parada Estratégica de Revisão</h3>
                <p id="revisao-texto-orientacao">Revise os esquemas e grifos das metas anteriores antes de prosseguir.</p>
                <div id="revisao-checklist-container">
                    <!-- Checklists gerados dinamicamente -->
                </div>
            </div>

            <!-- CONTEÚDO DAS AULAS / TÓPICOS -->
            <div class="aulas-content-wrapper" id="meta-aulas-wrapper">
                <!-- Aulas renderizadas aqui -->
            </div>

            <!-- NAVEGAÇÃO INFERIOR -->
            <div class="meta-nav-footer">
                <button class="btn-nav-meta" onclick="navegarMetaRelativa(-1)">⬅ Meta Anterior</button>
                <button class="btn-nav-meta" onclick="abrirVisaoQuadro()">📊 Voltar ao Quadro de Metas</button>
                <button class="btn-nav-meta" onclick="navegarMetaRelativa(1)">Próxima Meta ➔</button>
            </div>
        </section>

        <!-- 3. VISÃO: DISCIPLINAS -->
        <section class="disciplinas-section" id="view-disciplinas">
            <div class="quadro-header-banner">
                <div class="quadro-header-info">
                    <h2>📚 Metas Organizadas por Disciplina</h2>
                    <p>Visão vertical completa: estude matéria por matéria com todos os tópicos e status detalhados.</p>
                </div>
            </div>
            <div class="disciplinas-grid" id="disciplinas-grid-el">
                <!-- Cards de disciplinas gerados via JS -->
            </div>
        </section>

        <!-- 4. VISÃO: O QUE FALTA NO EDITAL (DIAGNÓSTICO) -->
        <section class="diagnostico-section" id="view-diagnostico">
            <div class="quadro-header-banner" style="border-left-color: var(--accent-red);">
                <div class="quadro-header-info">
                    <h2>📋 Diagnóstico do Edital: O que Falta</h2>
                    <p>Comparação completa entre o Guia Oficial do TRT-7 (208 Metas) e a sua pasta METAS.</p>
                </div>
            </div>

            <div class="diag-card">
                <div class="diag-title" style="color:var(--accent-red);">❌ Disciplinas do PDF Ausentes na pasta METAS (48 Metas Faltando)</div>
                <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">Estas matérias constam no Guia do TRT-7, mas ainda não possuem arquivo compilado na pasta <code>METAS/</code>:</p>
                <div style="display:flex; flex-direction:column; gap:8px;" id="lista-disciplinas-ausentes-el">
                    <!-- Gerado via JS -->
                </div>
            </div>

            <div class="diag-card">
                <div class="diag-title" style="color:var(--accent-gold);">⚠️ Tópicos Específicos a Complementar em Direito Administrativo</div>
                <ul style="font-size:0.86rem; color:var(--text-body); margin-left:20px; line-height:1.7;">
                    <li><strong>Bens Públicos & Responsabilidade Civil:</strong> Necessitam de leitura complementar da teoria e questões.</li>
                    <li><strong>Decreto nº 11.531 (Convênios) e Lei nº 13.019 (Parcerias OSC):</strong> Meta 17.</li>
                    <li><strong>Serviços Públicos (Leis 8.987, 11.079 e 13.460):</strong> Meta 18.</li>
                    <li><strong>Lei de Acesso à Informação - LAI (Lei nº 12.527):</strong> Meta 22.</li>
                    <li><strong>Lei Geral de Proteção de Dados - LGPD (Lei nº 13.709):</strong> Meta 23.</li>
                </ul>
            </div>

            <div class="diag-card">
                <div class="diag-title" style="color:#a78bfa;">⭐ Metas Extras Criadas Automaticamente a partir dos HTMLs</div>
                <p style="font-size:0.86rem; color:var(--text-muted); margin-bottom:12px;">
                    Sempre que um tópico presente no arquivo HTML da pasta <code>METAS/</code> não consta no PDF oficial do TRT-7, o sistema cria automaticamente uma <strong>Meta Extra</strong>. Isso preserva 100% dos seus conteúdos teóricos e bônus sem alterar a sequência oficial do PDF:
                </p>
                <div style="display:flex; flex-direction:column; gap:8px;" id="lista-metas-extras-diag">
                    <!-- Gerado dinamicamente via JS -->
                </div>
            </div>

            <div class="diag-card">
                <div class="diag-title" style="color:var(--accent-green);">✅ Disciplinas Estruturadas e Prontas (Metas Oficiais + Extras)</div>
                <p style="font-size:0.86rem; color:var(--text-muted);">
                    Direito Constitucional, Português, Direito do Trabalho, Direito Administrativo Unificado (24 metas), Matemática e RLM, Processo do Trabalho, Direitos Humanos, Administração e Gestão de Pessoas, e Informática. Todas as metas oficiais do PDF estão ativas, e os tópicos complementares do HTML foram convertidos em Metas Extras.
                </p>
            </div>
        </section>


        <!-- 5. VISÃO: MEU EDITAL (DASHBOARD TJAA vs AJAJ) -->
        <section class="edital-section" id="view-meu-edital" style="display:none;">
            <!-- Header Banner -->
            <div class="edital-header-banner">
                <div class="edital-header-info">
                    <h2>📑 Meu Edital • TRT-7 (CE)</h2>
                    <p>Mapeamento completo dos tópicos do edital oficial com as metas do Caderno do Aprovado.</p>
                </div>
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                    <button class="btn-layout-toggle" onclick="sincronizarEditalComMetas()" title="Recalcular tópicos a partir das metas concluídas">🔄 Sincronizar com Metas</button>
                    <button class="btn-layout-toggle" onclick="toggleTodosAccordionsEdital(true)" title="Expandir todas as disciplinas">⏬ Expandir</button>
                    <button class="btn-layout-toggle" onclick="toggleTodosAccordionsEdital(false)" title="Recolher todas as disciplinas">⏫ Recolher</button>
                </div>
            </div>

            <!-- Seletor de Cargo -->
            <div class="edital-cargo-tabs">
                <button class="edital-cargo-tab-btn active-tjaa" id="btn-cargo-tjaa" onclick="setEditalCargo('tjaa')">
                    🏛️ TJAA • Técnico Judiciário <span style="opacity:0.75; font-size:0.75rem;">(116 tópicos)</span>
                </button>
                <button class="edital-cargo-tab-btn" id="btn-cargo-ajaj" onclick="setEditalCargo('ajaj')">
                    ⚖️ AJAJ • Analista Judiciário <span style="opacity:0.75; font-size:0.75rem;">(151 tópicos)</span>
                </button>
                <button class="edital-cargo-tab-btn" id="btn-cargo-comp" onclick="setEditalCargo('comparativo')">
                    🔄 Comparativo TJAA vs AJAJ
                </button>
            </div>

            <!-- KPIs Dashboard (dinâmico via JS) -->
            <div class="edital-kpi-grid" id="edital-kpis-container">
                <!-- Gerado via JS -->
            </div>

            <!-- Barra de Filtros e Busca -->
            <div class="edital-controls-bar" id="edital-controls-container">
                <div class="edital-search-box">
                    <span>🔍</span>
                    <input type="text" id="edital-search-input" class="edital-search-input" 
                           placeholder="Buscar assunto, lei ou número da meta..." 
                           oninput="filtrarTopicosEdital(this.value)">
                    <button class="btn-clear-search" id="btn-clear-edital-search" onclick="limparBuscaEdital()" style="display:none;" title="Limpar busca">×</button>
                </div>
                <div class="edital-filter-pills">
                    <button class="edital-filter-btn active" id="btn-edital-filtro-todos" onclick="setEditalFiltroStatus('todos')">Todos</button>
                    <button class="edital-filter-btn" id="btn-edital-filtro-concluidos" onclick="setEditalFiltroStatus('concluidos')">✅ Concluídos</button>
                    <button class="edital-filter-btn" id="btn-edital-filtro-pendentes" onclick="setEditalFiltroStatus('pendentes')">⏳ Pendentes</button>
                </div>
            </div>

            <!-- Conteúdo Principal: Disciplinas & Tópicos OU Comparativo -->
            <div id="edital-content-area">
                <!-- Gerado via JS -->
            </div>
        </section>

    </main>

    <div class="toast-notify" id="toast-notify">✓ Alterações salvas</div>

    <!-- SCRIPT DA APLICAÇÃO -->
    <script>
        const PLATAFORMA_DATA = {dados_json};
        const DISCIPLINAS_AUSENTES = {ausentes_json};
        const EDITAIS_DATA = {editais_json};

        // ESTADO LOCAL
        let progressoMetas = JSON.parse(localStorage.getItem('trt4_metas_concluidas') || '{{}}');
        let progressoTopicosPdf = JSON.parse(localStorage.getItem('trt4_topicos_pdf_checked') || '{{}}');
        let progressoSubtopicos = JSON.parse(localStorage.getItem('trt4_subtopicos_concluidos') || '{{}}');
        let dadosQuestoes = JSON.parse(localStorage.getItem('trt4_questoes_dados') || '{{}}');
        let dadosCadernoErros = JSON.parse(localStorage.getItem('trt4_caderno_erros') || '{{}}');
        let dadosChecklistRev = JSON.parse(localStorage.getItem('trt4_checklist_revisao') || '{{}}');

        let metaAtivaId = null;
        let subtopicoAtivoPorMeta = {{}};
        let modoExibirTodos = false;
        let listaPlanaMetas = [];

        // Montar lista plana do ciclo oficial
        function construirListaPlanaCiclo() {{
            listaPlanaMetas = [];
            let maxMetas = 0;
            PLATAFORMA_DATA.forEach(d => {{
                if (d.metas.length > maxMetas) maxMetas = d.metas.length;
            }});

            for (let rodada = 1; rodada <= maxMetas; rodada++) {{
                PLATAFORMA_DATA.forEach(d => {{
                    const m = d.metas.find(item => item.numero === rodada);
                    if (m) {{
                        listaPlanaMetas.push(m);
                    }}
                }});
            }}
        }}

        construirListaPlanaCiclo();

        let filtroAtivoQuadro = 'todos';

        function filtrarQuadro(tipo) {{
            filtroAtivoQuadro = tipo;
            document.querySelectorAll('.filtro-btn').forEach(b => b.classList.remove('active'));
            const btn = document.getElementById(`btn-filtro-${{tipo}}`);
            if (btn) btn.classList.add('active');
            renderizarMatriz();
        }}

        // RENDERIZAR TABELA MATRIZ DO CICLO
        function renderizarMatriz() {{
            const table = document.getElementById('matriz-metas-table');
            let maxCols = 0;
            PLATAFORMA_DATA.forEach(d => {{
                if (d.metas.length > maxCols) maxCols = d.metas.length;
            }});

            let html = '';
            PLATAFORMA_DATA.forEach(disc => {{
                const concluidasDisc = disc.metas.filter(m => progressoMetas[m.id]).length;
                const pctDisc = Math.round((concluidasDisc / disc.metas.length) * 100);

                html += `<tr>`;
                html += `<td class="matriz-row-header" title="${{disc.disciplina}}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span>📚 <strong>${{disc.sigla}}</strong></span>
                                <span style="font-size:0.66rem; color:var(--accent-green); font-weight:700;">${{pctDisc}}%</span>
                            </div>
                            <div class="matriz-disc-name" style="font-size:0.66rem; color:var(--text-muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:145px;">
                                ${{disc.disciplina}}
                            </div>
                         </td>`;

                for (let c = 1; c <= maxCols; c++) {{
                    const meta = disc.metas.find(m => m.numero === c);
                    if (meta) {{
                        const isDone = !!progressoMetas[meta.id];
                        let classes = 'matriz-cell';
                        if (meta.revisao) classes += ' revisao';
                        if (meta.prioritaria) classes += ' prioritaria';
                        if (meta.extra) classes += ' extra';
                        if (isDone) classes += ' concluida';

                        if (filtroAtivoQuadro === 'prio' && !meta.prioritaria) classes += ' dimmed';
                        else if (filtroAtivoQuadro === 'rev' && !meta.revisao) classes += ' dimmed';
                        else if (filtroAtivoQuadro === 'extra' && !meta.extra) classes += ' dimmed';

                        const tooltip = meta.assuntos.join(' \\n• ');
                        const badgeTxt = isDone ? '✓' : (meta.extra ? 'EXTRA' : (meta.revisao ? 'REV' : ''));

                        html += `
                            <td class="${{classes}}" onclick="abrirMeta('${{meta.id}}')" title="${{meta.extra ? 'META EXTRA: ' : 'Meta ' + meta.numero + ': '}}${{disc.disciplina}}\\n• ${{tooltip}}">
                                <div>${{disc.sigla}} ${{meta.numero}}</div>
                                <span class="matriz-cell-badge">${{badgeTxt}}</span>
                            </td>
                        `;
                    }} else {{
                        html += `<td style="border:none; background:transparent;"></td>`;
                    }}
                }}
                html += `</tr>`;
            }});

            table.innerHTML = html;
            renderizarQuadroMetasExtras();
        }}

        // RENDERIZAR METAS EXTRAS NO FINAL DE CADA DISCIPLINA (NO QUADRO DE METAS)
        function renderizarQuadroMetasExtras() {{
            const container = document.getElementById('quadro-extras-disciplinas-grid');
            if (!container) return;

            let html = '';
            let totalExtrasCount = 0;

            PLATAFORMA_DATA.forEach(disc => {{
                const metasExtras = disc.metas.filter(m => m.extra);
                if (metasExtras.length === 0) return;

                totalExtrasCount += metasExtras.length;

                let cardsHtml = '';
                metasExtras.forEach(m => {{
                    const isDone = !!progressoMetas[m.id];
                    cardsHtml += `
                        <div class="quadro-extra-card-item ${{isDone ? 'concluida' : ''}}">
                            <div class="quadro-extra-item-top">
                                <div>
                                    <div class="quadro-extra-item-nome">
                                        ⭐ Meta ${{m.numero}}: ${{escapeHtml(m.assuntos[0] || 'Conteúdo Complementar')}}
                                    </div>
                                    <div class="quadro-extra-item-sub">
                                        ${{escapeHtml(m.subtitulo || 'Conteúdo complementar do caderno HTML')}}
                                    </div>
                                </div>
                                <span class="badge-extra" style="font-size:0.68rem; padding:1px 6px;">${{isDone ? '✓ Concluída' : 'EXTRA'}}</span>
                            </div>
                            <div class="quadro-extra-item-actions">
                                <label style="display:inline-flex; align-items:center; gap:6px; font-size:0.75rem; color:var(--text-muted); cursor:pointer;">
                                    <input type="checkbox" ${{isDone ? 'checked' : ''}} onchange="toggleMetaConcluida('${{m.id}}', this.checked)">
                                    <span>${{isDone ? 'Concluída' : 'Marcar Concluída'}}</span>
                                </label>
                                <button class="btn-estudar-extra" onclick="abrirMeta('${{m.id}}')">
                                    ▶ Estudar Meta Extra
                                </button>
                            </div>
                        </div>
                    `;
                }});

                html += `
                    <div class="quadro-extras-disc-group">
                        <div class="quadro-extras-disc-title">
                            <span>📚 ${{disc.sigla}} - ${{disc.disciplina}}</span>
                            <span style="font-size:0.75rem; color:#c4b5fd; font-weight:700;">${{metasExtras.length}} Meta(s) Extra(s) no final</span>
                        </div>
                        <div class="quadro-extras-cards-list">
                            ${{cardsHtml}}
                        </div>
                    </div>
                `;
            }});

            if (totalExtrasCount === 0) {{
                html = '<div style="color:var(--text-muted); font-size:0.85rem;">Nenhuma meta extra identificada nos arquivos HTML.</div>';
            }}

            container.innerHTML = html;
        }}

        function toggleMetaConcluida(metaId, status) {{
            if (status !== undefined) {{
                progressoMetas[metaId] = !!status;
            }} else {{
                progressoMetas[metaId] = !progressoMetas[metaId];
            }}
            const novoStatus = !!progressoMetas[metaId];
            localStorage.setItem('trt4_metas_concluidas', JSON.stringify(progressoMetas));

            // Sincronizar submetas / subtópicos com a conclusão da meta (efeito visual e tracking)
            let metaAlvo = null;
            for (const d of PLATAFORMA_DATA) {{
                const m = d.metas.find(item => item.id === metaId);
                if (m) {{ metaAlvo = m; break; }}
            }}

            if (metaAlvo) {{
                // 1. Subtópicos de conteúdo / aulas
                if (metaAlvo.aulas_conteudo && metaAlvo.aulas_conteudo.length > 0) {{
                    metaAlvo.aulas_conteudo.forEach((_, i) => {{
                        progressoSubtopicos[`${{metaId}}-sub-${{i}}`] = novoStatus;
                    }});
                    localStorage.setItem('trt4_subtopicos_concluidos', JSON.stringify(progressoSubtopicos));
                }}

                // 2. Tópicos do Caderno / PDF listados na meta
                if (metaAlvo.assuntos && metaAlvo.assuntos.length > 0) {{
                    metaAlvo.assuntos.forEach((_, idx) => {{
                        progressoTopicosPdf[`${{metaId}}-topico-${{idx}}`] = novoStatus;
                    }});
                    localStorage.setItem('trt4_topicos_pdf_checked', JSON.stringify(progressoTopicosPdf));
                }}

                // 3. Checklist de revisão (se for meta de revisão)
                if (metaAlvo.revisao) {{
                    for (let idx = 0; idx < 4; idx++) {{
                        dadosChecklistRev[`${{metaId}}-chk-${{idx}}`] = novoStatus;
                    }}
                    localStorage.setItem('trt4_checklist_revisao', JSON.stringify(dadosChecklistRev));
                }}
            }}

            agendarSincronizacaoNuvem();

            if (metaAtivaId === metaId) {{
                atualizarBotaoStatusMeta();
                if (metaAlvo) {{
                    renderizarTopicosDoPdf(metaAlvo);
                    if (metaAlvo.revisao) renderizarChecklistRevisao(metaId);

                    // Atualizar visual das abas/pills de subtópicos da tela atual
                    const aulas = metaAlvo.aulas_conteudo || [];
                    if (aulas.length > 1) {{
                        const pillsContainer = document.querySelector('.subtopicos-pills-container');
                        if (pillsContainer) {{
                            let subIdx = subtopicoAtivoPorMeta[metaId] || 0;
                            let pillsHtml = '';
                            aulas.forEach((a, i) => {{
                                const isSubDone = !!progressoSubtopicos[`${{metaId}}-sub-${{i}}`];
                                const activeClass = (i === subIdx && !modoExibirTodos) ? 'active' : '';
                                const doneClass = isSubDone ? 'concluido' : '';
                                pillsHtml += `
                                    <button class="subtopico-pill ${{activeClass}} ${{doneClass}}" onclick="selecionarSubtopico('${{metaId}}', ${{i}})">
                                        ${{i + 1}}. ${{escapeHtml(a.titulo)}} ${{isSubDone ? '✓' : ''}}
                                    </button>
                                `;
                            }});
                            pillsContainer.innerHTML = pillsHtml;
                        }}
                    }}
                }}
            }}

            atualizarProgressoGlobal();
            renderizarMatriz();
            renderizarDisciplinas();
            if (typeof renderizarDashboardEdital === 'function') renderizarDashboardEdital();
            mostrarToast(novoStatus ? '✓ Meta e submetas concluídas!' : 'Meta desmarcada');
        }}

        // BUSCA GLOBAL NA PLATAFORMA
        function executarBuscaGlobal(query) {{
            const dropdown = document.getElementById('search-dropdown-results');
            const clearBtn = document.getElementById('btn-clear-search');
            const q = query.trim().toLowerCase();

            if (!q) {{
                dropdown.style.display = 'none';
                clearBtn.style.display = 'none';
                return;
            }}

            clearBtn.style.display = 'inline-block';
            dropdown.style.display = 'block';

            const normQ = normalizarBusca(q);
            const resultados = [];

            PLATAFORMA_DATA.forEach(disc => {{
                disc.metas.forEach(meta => {{
                    let score = 0;
                    let matchReason = '';
                    let snippet = '';

                    const discNorm = normalizarBusca(disc.disciplina);
                    const siglaNorm = normalizarBusca(disc.sigla);
                    if (siglaNorm === normQ || discNorm.startsWith(normQ)) {{
                        score += 50;
                        matchReason = `Disciplina: ${{disc.disciplina}}`;
                    }} else if (discNorm.includes(normQ)) {{
                        score += 30;
                        matchReason = `Disciplina: ${{disc.disciplina}}`;
                    }}

                    const metaLabel = `meta ${{meta.numero}}`;
                    const siglaMeta = `${{disc.sigla.toLowerCase()}} ${{meta.numero}}`;
                    const siglaMetaSemEspaco = `${{disc.sigla.toLowerCase()}}${{meta.numero}}`;
                    if (metaLabel.includes(normQ) || siglaMeta.includes(normQ) || siglaMetaSemEspaco === normQ) {{
                        score += 60;
                        matchReason = `Meta ${{meta.numero}} de ${{disc.disciplina}}`;
                    }}

                    meta.assuntos.forEach(ass => {{
                        const assNorm = normalizarBusca(ass);
                        if (assNorm.includes(normQ)) {{
                            score += 45;
                            matchReason = ass.replace('★', '').trim();
                        }}
                    }});

                    let matchedSubIdx = 0;
                    if (meta.aulas_conteudo && meta.aulas_conteudo.length > 0) {{
                        meta.aulas_conteudo.forEach((aula, aIdx) => {{
                            const titNorm = normalizarBusca(aula.titulo);
                            if (titNorm.includes(normQ)) {{
                                score += 40;
                                matchReason = `Tópico: ${{aula.titulo}}`;
                                matchedSubIdx = aIdx;
                            }} else {{
                                const bodyText = aula.html.replace(/<[^>]+>/g, ' ');
                                const bodyNorm = normalizarBusca(bodyText);
                                const pos = bodyNorm.indexOf(normQ);
                                if (pos !== -1 && !snippet) {{
                                    score += 25;
                                    const start = Math.max(0, pos - 40);
                                    const end = Math.min(bodyText.length, pos + q.length + 60);
                                    snippet = '...' + bodyText.substring(start, end).replace(/\\s+/g, ' ').trim() + '...';
                                    if (!matchReason) matchReason = `Conteúdo em: ${{aula.titulo}}`;
                                    matchedSubIdx = aIdx;
                                }}
                            }}
                        }});
                    }}

                    if (score > 0) {{
                        resultados.push({{
                            metaId: meta.id,
                            subIdx: matchedSubIdx,
                            discSigla: disc.sigla,
                            discNome: disc.disciplina,
                            metaNum: meta.numero,
                            extra: meta.extra,
                            revisao: meta.revisao,
                            prio: meta.prioritaria,
                            reason: matchReason || `Meta ${{meta.numero}}`,
                            snippet: snippet,
                            score: score
                        }});
                    }}
                }});
            }});

            resultados.sort((a, b) => b.score - a.score);

            if (resultados.length === 0) {{
                dropdown.innerHTML = `<div class="search-empty-state">Nenhum resultado para "<strong>${{escapeHtml(query)}}</strong>". Tente buscar por lei, artigo, sigla ou tema geral.</div>`;
                return;
            }}

            const limit = resultados.slice(0, 15);
            let html = `<div class="search-result-group-title">Resultados Encontrados (${{resultados.length}})</div>`;

            limit.forEach(res => {{
                const highlightedReason = destacarTermo(res.reason, query);
                const highlightedSnippet = res.snippet ? destacarTermo(res.snippet, query) : '';
                const badgeClass = res.extra ? 'search-result-disc-badge extra' : 'search-result-disc-badge';
                const badgeLabel = res.extra ? `${{res.discSigla}} • Extra` : (res.revisao ? `${{res.discSigla}} • Rev` : `${{res.discSigla}} • M${{res.metaNum}}`);

                html += `
                    <div class="search-result-item" onclick="selecionarResultadoBusca('${{res.metaId}}', ${{res.subIdx !== undefined ? res.subIdx : 0}})">
                        <div class="search-result-left">
                            <div class="search-result-title">${{highlightedReason}}</div>
                            <div class="search-result-subtitle">${{res.discNome}} • Meta ${{res.metaNum}}${{res.extra ? ' (Extra)' : ''}}</div>
                            ${{highlightedSnippet ? `<div class="search-result-snippet">${{highlightedSnippet}}</div>` : ''}}
                        </div>
                        <div class="search-result-badges">
                            <span class="${{badgeClass}}">${{badgeLabel}}</span>
                        </div>
                    </div>
                `;
            }});

            dropdown.innerHTML = html;
        }}

        function normalizarBusca(t) {{
            if (!t) return '';
            return t.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase();
        }}

        function destacarTermo(texto, termo) {{
            if (!termo.trim()) return escapeHtml(texto);
            const regex = new RegExp(`(${{escapeRegex(termo)}})`, 'gi');
            return escapeHtml(texto).replace(regex, '<mark>$1</mark>');
        }}

        function escapeHtml(s) {{
            return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }}

        function escapeRegex(s) {{
            return s.replace(/[-\\/\\\\^$*+?.()|[\\]{{}}]/g, '\\\\$&');
        }}

        function limparBusca() {{
            const input = document.getElementById('global-search-input');
            if (input) input.value = '';
            const dropdown = document.getElementById('search-dropdown-results');
            if (dropdown) dropdown.style.display = 'none';
            const clearBtn = document.getElementById('btn-clear-search');
            if (clearBtn) clearBtn.style.display = 'none';
        }}

        function selecionarResultadoBusca(metaId, subIdx) {{
            limparBusca();
            if (subIdx !== undefined) {{
                subtopicoAtivoPorMeta[metaId] = subIdx;
            }}
            modoExibirTodos = false;
            abrirMeta(metaId);
        }}

        // Fechar dropdown de busca ao clicar fora
        document.addEventListener('click', (e) => {{
            const container = document.querySelector('.topbar-search-container');
            if (container && !container.contains(e.target)) {{
                const dropdown = document.getElementById('search-dropdown-results');
                if (dropdown) dropdown.style.display = 'none';
            }}
        }});

        // Atalhos de teclado (Ctrl+K ou barra / para focar a busca)
        document.addEventListener('keydown', (e) => {{
            if ((e.ctrlKey && e.key.toLowerCase() === 'k') || (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA')) {{
                e.preventDefault();
                const input = document.getElementById('global-search-input');
                if (input) {{
                    input.focus();
                    input.select();
                }}
            }} else if (e.key === 'Escape') {{
                limparBusca();
            }}
        }});

        // ABRIR UMA META ESPECÍFICA
        function abrirMeta(metaId) {{
            let metaEncontrada = null;
            let discPai = null;

            for (const d of PLATAFORMA_DATA) {{
                const m = d.metas.find(item => item.id === metaId);
                if (m) {{
                    metaEncontrada = m;
                    discPai = d;
                    break;
                }}
            }}

            if (!metaEncontrada) return;

            metaAtivaId = metaId;
            abrirVisaoEstudo();

            document.getElementById('breadcrumb-disc-nome').textContent = discPai.disciplina;
            document.getElementById('breadcrumb-meta-nome').textContent = metaEncontrada.extra ? `Meta ${{metaEncontrada.numero}} (Extra)` : `Meta ${{metaEncontrada.numero}}`;
            document.getElementById('meta-card-title').textContent = metaEncontrada.extra ? `⭐ Meta ${{metaEncontrada.numero}} (Extra) — ${{discPai.disciplina}}` : `🎯 Meta ${{metaEncontrada.numero}} — ${{discPai.disciplina}}`;

            const subtituloEl = document.getElementById('meta-badge-subtitulo');
            if (metaEncontrada.subtitulo) {{
                subtituloEl.style.display = 'inline-block';
                subtituloEl.textContent = metaEncontrada.subtitulo;
            }} else {{
                subtituloEl.style.display = 'none';
            }}

            const headerEl = document.getElementById('meta-view-header-el');
            if (metaEncontrada.revisao) headerEl.className = 'meta-view-header is-revisao';
            else if (metaEncontrada.extra) headerEl.className = 'meta-view-header is-extra';
            else headerEl.className = 'meta-view-header';

            document.getElementById('meta-badge-star').style.display = metaEncontrada.prioritaria ? 'inline-block' : 'none';
            document.getElementById('meta-badge-rev').style.display = metaEncontrada.revisao ? 'inline-block' : 'none';
            const badgeExtraEl = document.getElementById('meta-badge-extra');
            if (badgeExtraEl) {{
                badgeExtraEl.style.display = metaEncontrada.extra ? 'inline-block' : 'none';
            }}

            atualizarBotaoStatusMeta();

            // Renderizar Lista Oficial de Tópicos do PDF
            renderizarTopicosDoPdf(metaEncontrada);

            // Carregar dados de questões
            const questaoData = dadosQuestoes[metaId] || {{ feitas: '', acertos: '' }};
            document.getElementById('input-questoes-feitas').value = questaoData.feitas || '';
            document.getElementById('input-questoes-acertos').value = questaoData.acertos || '';
            calcularPercentualQuestoes();

            // Carregar caderno de erros
            document.getElementById('input-caderno-erros').value = dadosCadernoErros[metaId] || '';

            // Bloco de Revisão
            const revBox = document.getElementById('box-meta-revisao');
            if (metaEncontrada.revisao) {{
                revBox.style.display = 'block';
                document.getElementById('revisao-texto-orientacao').textContent = metaEncontrada.orientacao_revisao || '';
                renderizarChecklistRevisao(metaId);
            }} else {{
                revBox.style.display = 'none';
            }}

            // Renderizar aulas / assuntos com suporte a abas de subtópicos estilo Caderno do Aprovado
            const aulasWrapper = document.getElementById('meta-aulas-wrapper');
            let aulasHtml = '';

            const aulas = metaEncontrada.aulas_conteudo || [];
            if (aulas.length > 0) {{
                let subIdx = subtopicoAtivoPorMeta[metaId];
                if (subIdx === undefined || subIdx < 0 || subIdx >= aulas.length) {{
                    subIdx = 0;
                    subtopicoAtivoPorMeta[metaId] = 0;
                }}

                const aulaAtiva = aulas[subIdx];
                document.getElementById('breadcrumb-meta-nome').textContent = `${{metaEncontrada.extra ? 'Meta Extra ' + metaEncontrada.numero : 'Meta ' + metaEncontrada.numero}} > ${{aulaAtiva.titulo}}`;

                // Painel de Subtópicos (se houver mais de 1 subtópico)
                if (aulas.length > 1) {{
                    let pillsHtml = '';
                    aulas.forEach((a, i) => {{
                        const isSubDone = !!progressoSubtopicos[`${{metaId}}-sub-${{i}}`];
                        const activeClass = (i === subIdx && !modoExibirTodos) ? 'active' : '';
                        const doneClass = isSubDone ? 'concluido' : '';
                        pillsHtml += `
                            <button class="subtopico-pill ${{activeClass}} ${{doneClass}}" onclick="selecionarSubtopico('${{metaId}}', ${{i}})">
                                ${{i + 1}}. ${{escapeHtml(a.titulo)}} ${{isSubDone ? '✓' : ''}}
                            </button>
                        `;
                    }});

                    aulasHtml += `
                        <div class="subtopicos-quick-panel">
                            <div class="subtopicos-panel-top">
                                <div class="subtopicos-panel-title">📑 SUBTÓPICOS DESTA META (${{aulas.length}}):</div>
                                <button class="btn-toggle-subtopics-mode" onclick="alternarModoSubtopicos('${{metaId}}')">
                                    ${{modoExibirTodos ? '📑 Exibir em Abas Individuais' : '📖 Exibir Todos Juntos'}}
                                </button>
                            </div>
                            <div class="subtopicos-pills-container">${{pillsHtml}}</div>
                        </div>
                    `;
                }}

                if (modoExibirTodos) {{
                    aulas.forEach((a, i) => {{
                        aulasHtml += `
                            <article class="aula-card-render" style="margin-bottom:20px;">
                                <div class="aula-header-action-row">
                                    <div class="aula-header-title-box">
                                        <span class="aula-header-badge">${{i + 1}} de ${{aulas.length}}</span>
                                        <h3 class="aula-card-subtitulo">${{escapeHtml(a.titulo)}}</h3>
                                    </div>
                                </div>
                                <div class="aula-body-text">${{a.html}}</div>
                            </article>
                        `;
                    }});
                }} else {{
                    aulasHtml += `
                        <article class="aula-card-render">
                            <div class="aula-header-action-row">
                                <div class="aula-header-title-box">
                                    <span class="aula-header-badge">${{subIdx + 1}} de ${{aulas.length}}</span>
                                    <h3 class="aula-card-subtitulo">${{escapeHtml(aulaAtiva.titulo)}}</h3>
                                </div>
                            </div>
                            <div class="aula-body-text">${{aulaAtiva.html}}</div>
                        </article>
                    `;
                }}
            }} else {{
                if (!metaEncontrada.revisao) {{
                    aulasHtml = `
                        <article class="aula-card-render" style="border-left: 4px solid var(--primary);">
                            <h3>📖 Tópico Teórico / Leitura Orientada</h3>
                            <div class="aula-body-text">
                                <p>Este tópico do edital corresponde à <strong>leitura orientada de legislação ou material de apoio</strong> conforme indicado na lista acima.</p>
                                <p style="color:var(--text-muted); font-size:0.85rem;">
                                    💡 <em>Dica: Faça a leitura dos artigos da lei seca indicados e resolva questões de concursos anteriores correspondentes.</em>
                                </p>
                            </div>
                        </article>
                    `;
                }}
            }}

            aulasWrapper.innerHTML = aulasHtml;
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function selecionarSubtopico(metaId, subIdx) {{
            modoExibirTodos = false;
            subtopicoAtivoPorMeta[metaId] = subIdx;
            abrirMeta(metaId);
        }}

        function alternarModoSubtopicos(metaId) {{
            modoExibirTodos = !modoExibirTodos;
            abrirMeta(metaId);
        }}

        function toggleSubtopicoConcluido(metaId, subIdx, checked) {{
            const key = `${{metaId}}-sub-${{subIdx}}`;
            progressoSubtopicos[key] = checked;
            localStorage.setItem('trt4_subtopicos_concluidos', JSON.stringify(progressoSubtopicos));
            agendarSincronizacaoNuvem();

            let metaAlvo = null;
            for (const d of PLATAFORMA_DATA) {{
                const m = d.metas.find(item => item.id === metaId);
                if (m) {{ metaAlvo = m; break; }}
            }}

            if (metaAlvo && metaAlvo.aulas_conteudo && metaAlvo.aulas_conteudo.length > 0) {{
                const todosConcluidos = metaAlvo.aulas_conteudo.every((_, i) => progressoSubtopicos[`${{metaId}}-sub-${{i}}`]);
                if (todosConcluidos && !progressoMetas[metaId]) {{
                    progressoMetas[metaId] = true;
                    localStorage.setItem('trt4_metas_concluidas', JSON.stringify(progressoMetas));
                    mostrarToast(`🎉 Todos os subtópicos concluídos! Meta ${{metaAlvo.numero}} concluída.`);
                }}
            }}

            abrirMeta(metaId);
            renderizarMatriz();
            atualizarProgressoGlobal();
        }}

        // RENDERIZAR TÓPICOS DO PDF NA META
        function renderizarTopicosDoPdf(meta) {{
            const listEl = document.getElementById('lista-pdf-assuntos-el');
            let html = '';

            if (meta.extra) {{
                html += `
                    <div style="margin-bottom:14px; padding:12px 16px; background:rgba(139, 92, 246, 0.12); border:1px solid rgba(139, 92, 246, 0.35); border-left:4px solid #8b5cf6; border-radius:8px; font-size:0.86rem; color:#e0e7ff; line-height:1.5;">
                        <strong>⭐ Informação sobre esta Meta Extra:</strong><br>
                        Este tópico foi identificado no arquivo HTML compilado da pasta <code>METAS/</code>, mas não constava no rol oficial de metas do PDF do TRT-7. O sistema gerou automaticamente esta <strong>Meta Extra</strong> para preservar 100% dos seus materiais e resumos de estudo, permitindo que você estude o conteúdo, resolva questões e marque como concluída sem alterar a numeração oficial das metas do PDF.
                    </div>
                `;
            }}

            const temAulas = meta.aulas_conteudo && meta.aulas_conteudo.length > 0;

            meta.assuntos.forEach((assuntoRaw, idx) => {{
                const itemKey = `${{meta.id}}-topico-${{idx}}`;
                const isChecked = !!progressoTopicosPdf[itemKey];
                const isPrio = assuntoRaw.trim().startsWith('★');
                const assuntoLimpo = assuntoRaw.replace('★', '').trim();

                // Verifica se é um item de leitura de lei seca
                const isLeiSeca = assuntoLimpo.toLowerCase().includes('leitura') || assuntoLimpo.toLowerCase().includes('art') || assuntoLimpo.toLowerCase().includes('lei ');

                let badgeHtml = '';
                if (meta.extra) {{
                    badgeHtml = '<span class="badge-conteudo-ok" style="background:rgba(139, 92, 246, 0.2); color:#c4b5fd; border-color:rgba(139, 92, 246, 0.4);">⭐ Conteúdo Extra do HTML</span>';
                }} else if (meta.revisao) {{
                    badgeHtml = '<span class="badge-conteudo-ok">🟢 Revisão</span>';
                }} else if (temAulas && !isLeiSeca) {{
                    badgeHtml = '<span class="badge-conteudo-ok">✓ Teoria Compilada</span>';
                }} else if (isLeiSeca) {{
                    badgeHtml = '<span class="badge-lei-seca">📄 Lei Seca</span>';
                }} else {{
                    badgeHtml = '<span class="badge-lei-seca">📄 Tópico do Edital</span>';
                }}

                html += `
                    <li>
                        <label class="meta-item-label">
                            <div class="meta-item-left">
                                <input type="checkbox" ${{isChecked ? 'checked' : ''}} onchange="toggleTopicoPdf('${{itemKey}}', this.checked)">
                                <span>${{isPrio ? '<strong style="color:var(--accent-gold);">★</strong> ' : ''}}${{assuntoLimpo}}</span>
                            </div>
                            ${{badgeHtml}}
                        </label>
                    </li>
                `;
            }});

            listEl.innerHTML = html;
        }}

        function toggleTopicoPdf(key, checked) {{
            progressoTopicosPdf[key] = checked;
            localStorage.setItem('trt4_topicos_pdf_checked', JSON.stringify(progressoTopicosPdf));
            agendarSincronizacaoNuvem();
        }}

        function atualizarBotaoStatusMeta() {{
            const btn = document.getElementById('btn-toggle-meta-status');
            const icon = document.getElementById('btn-toggle-meta-icon');
            const txt = document.getElementById('btn-toggle-meta-txt');
            const isDone = !!progressoMetas[metaAtivaId];

            if (isDone) {{
                btn.classList.add('checked');
                icon.textContent = '✓';
                txt.textContent = 'Meta Concluída!';
            }} else {{
                btn.classList.remove('checked');
                icon.textContent = '⚪';
                txt.textContent = 'Marcar como Concluída';
            }}
        }}

        function toggleMetaAtualConcluida() {{
            if (!metaAtivaId) return;
            toggleMetaConcluida(metaAtivaId);
        }}

        function renderizarChecklistRevisao(metaId) {{
            const container = document.getElementById('revisao-checklist-container');
            const itensPadrao = [
                "1. Revisão de esquemas e grifos das matérias anteriores",
                "2. Leitura atenta dos artigos da legislação indicada",
                "3. Resolução de bateria de 15 a 20 questões de fixação",
                "4. Registro das pegadinhas e erros no Caderno de Erros"
            ];

            let html = '';
            itensPadrao.forEach((item, idx) => {{
                const key = `${{metaId}}-chk-${{idx}}`;
                const checked = !!dadosChecklistRev[key];
                html += `
                    <label class="checklist-item">
                        <input type="checkbox" ${{checked ? 'checked' : ''}} onchange="toggleChecklist('${{key}}', this.checked)">
                        <span>${{item}}</span>
                    </label>
                `;
            }});
            container.innerHTML = html;
        }}

        function toggleChecklist(key, checked) {{
            dadosChecklistRev[key] = checked;
            localStorage.setItem('trt4_checklist_revisao', JSON.stringify(dadosChecklistRev));
            agendarSincronizacaoNuvem();
        }}

        function salvarQuestoesMeta() {{
            if (!metaAtivaId) return;
            const feitas = parseInt(document.getElementById('input-questoes-feitas').value) || 0;
            const acertos = parseInt(document.getElementById('input-questoes-acertos').value) || 0;

            dadosQuestoes[metaAtivaId] = {{ feitas, acertos }};
            localStorage.setItem('trt4_questoes_dados', JSON.stringify(dadosQuestoes));
            agendarSincronizacaoNuvem();
            calcularPercentualQuestoes();
        }}

        function calcularPercentualQuestoes() {{
            const feitas = parseInt(document.getElementById('input-questoes-feitas').value) || 0;
            const acertos = parseInt(document.getElementById('input-questoes-acertos').value) || 0;
            const pctEl = document.getElementById('questoes-pct-val');

            if (feitas > 0) {{
                const pct = Math.round((acertos / feitas) * 100);
                pctEl.textContent = `${{pct}}%`;
                pctEl.className = 'questoes-stat-val';
                if (pct >= 80) pctEl.classList.add('otimo');
                else if (pct >= 60) pctEl.classList.add('medio');
                else pctEl.classList.add('baixo');
            }} else {{
                pctEl.textContent = '0%';
                pctEl.className = 'questoes-stat-val';
            }}
        }}

        function salvarCadernoErrosMeta() {{
            if (!metaAtivaId) return;
            dadosCadernoErros[metaAtivaId] = document.getElementById('input-caderno-erros').value;
            localStorage.setItem('trt4_caderno_erros', JSON.stringify(dadosCadernoErros));
            agendarSincronizacaoNuvem();
        }}

        // PRÓXIMA META DO CICLO
        function irParaProximaMeta() {{
            const proxima = listaPlanaMetas.find(m => !progressoMetas[m.id]);
            if (proxima) {{
                abrirMeta(proxima.id);
                mostrarToast(`Abrindo próxima meta: ${{proxima.sigla}} ${{proxima.numero}}`);
            }} else {{
                mostrarToast(`🎉 Parabéns! Você concluiu todas as ${{listaPlanaMetas.length}} metas disponíveis!`);
            }}
        }}

        function navegarMetaRelativa(delta) {{
            if (!metaAtivaId) return;
            const idxAtual = listaPlanaMetas.findIndex(m => m.id === metaAtivaId);
            if (idxAtual !== -1) {{
                const novoIdx = idxAtual + delta;
                if (novoIdx >= 0 && novoIdx < listaPlanaMetas.length) {{
                    abrirMeta(listaPlanaMetas[novoIdx].id);
                }}
            }}
        }}

        // PROGRESSO GLOBAL
        function atualizarProgressoGlobal() {{
            const totalMetas = listaPlanaMetas.length;
            const concluidas = listaPlanaMetas.filter(m => progressoMetas[m.id]).length;
            const pct = totalMetas > 0 ? Math.round((concluidas / totalMetas) * 100) : 0;

            document.getElementById('topbar-metas-txt').textContent = `${{concluidas}} / ${{totalMetas}} (${{pct}}%)`;
            document.getElementById('topbar-progress-fill').style.width = `${{pct}}%`;
        }}

                // VISÃO DISCIPLINAS: METAS ORGANIZADAS POR DISCIPLINA
        let filtroDisciplinaAtiva = 'TODAS';

        function filtrarVisaoDisciplinas(sigla) {{
            filtroDisciplinaAtiva = sigla;
            renderizarDisciplinas();
        }}

        function renderizarDisciplinas() {{
            const container = document.getElementById('disciplinas-grid-el');
            if (!container) return;

            // Barra de filtros rápidos por disciplina no topo
            let filtrosHtml = `<div class="disciplinas-filtros-bar">
                <button class="disc-filter-btn ${{filtroDisciplinaAtiva === 'TODAS' ? 'active' : ''}}" onclick="filtrarVisaoDisciplinas('TODAS')">Todas as Disciplinas (${{PLATAFORMA_DATA.length}})</button>`;
            
            PLATAFORMA_DATA.forEach(d => {{
                filtrosHtml += `<button class="disc-filter-btn ${{filtroDisciplinaAtiva === d.sigla ? 'active' : ''}}" onclick="filtrarVisaoDisciplinas('${{d.sigla}}')">${{d.sigla}}</button>`;
            }});
            filtrosHtml += `</div>`;

            let blocosHtml = `<div class="disciplinas-container">`;

            const disciplinasExibir = filtroDisciplinaAtiva === 'TODAS' 
                ? PLATAFORMA_DATA 
                : PLATAFORMA_DATA.filter(d => d.sigla === filtroDisciplinaAtiva);

            disciplinasExibir.forEach(disc => {{
                const total = disc.metas.length;
                const concluidas = disc.metas.filter(m => progressoMetas[m.id]).length;
                const pct = total > 0 ? Math.round((concluidas / total) * 100) : 0;

                let metasCardsHtml = `<div class="disc-metas-cards-grid">`;
                disc.metas.forEach(meta => {{
                    const concluida = !!progressoMetas[meta.id];
                    let tagClass = 'disc-meta-badge-num';
                    let tagText = `${{disc.sigla}} ${{meta.numero}}`;
                    if (meta.revisao) {{
                        tagClass += ' rev';
                        tagText += ' 🟢 REV';
                    }} else if (meta.extra) {{
                        tagClass += ' extra';
                        tagText += ' ⭐ EXTRA';
                    }}

                    const prioritariaBadge = meta.prioritaria 
                        ? `<span class="disc-meta-badge-prio">★ Prioritária</span>` 
                        : '';

                    let assuntosTxt = meta.assuntos && meta.assuntos.length > 0 
                        ? meta.assuntos.join(' • ') 
                        : (meta.revisao ? 'Revisão estratégica da matéria' : 'Tópico de estudo');

                    metasCardsHtml += `
                        <div class="disc-meta-card ${{concluida ? 'concluida' : ''}}" onclick="abrirMeta('${{meta.id}}')">
                            <div class="disc-meta-top">
                                <span class="${{tagClass}}">${{tagText}}</span>
                                ${{prioritariaBadge}}
                            </div>
                            <div class="disc-meta-assuntos" title="${{escapeHtml(assuntosTxt)}}">${{escapeHtml(assuntosTxt)}}</div>
                            <div class="disc-meta-bottom">
                                <span class="btn-estudar-disc-meta">Estudar ➔</span>
                                <button class="btn-check-disc-meta ${{concluida ? 'checked' : ''}}" onclick="event.stopPropagation(); toggleMetaConcluida('${{meta.id}}', event); renderizarDisciplinas();">
                                    ${{concluida ? '✓ Concluída' : 'Marcar'}}
                                </button>
                            </div>
                        </div>
                    `;
                }});
                metasCardsHtml += `</div>`;

                blocosHtml += `
                    <div class="disciplina-bloco" id="disc-bloco-${{disc.sigla}}">
                        <div class="disc-bloco-header">
                            <div class="disc-bloco-left">
                                <span class="disc-sigla-tag">📚 ${{disc.sigla}}</span>
                                <h3 class="disc-nome-titulo">${{disc.disciplina}}</h3>
                            </div>
                            <div class="disc-bloco-right">
                                <span class="disc-progresso-badge">${{concluidas}} / ${{total}} metas (${{pct}}%)</span>
                                <div class="disc-progress-mini-bar">
                                    <div class="disc-progress-mini-fill" style="width: ${{pct}}%;"></div>
                                </div>
                            </div>
                        </div>
                        ${{metasCardsHtml}}
                    </div>
                `;
            }});

            blocosHtml += `</div>`;
            container.innerHTML = filtrosHtml + blocosHtml;
        }}

        // RENDERIZAR VISÃO DIAGNÓSTICO DO QUE FALTA
        function renderizarDiagnostico() {{
            const listEl = document.getElementById('lista-disciplinas-ausentes-el');
            let html = '';
            DISCIPLINAS_AUSENTES.forEach(item => {{
                html += `
                    <div style="background:var(--bg-body); border:1px solid var(--border); border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>📚 ${{item.sigla}} - ${{item.nome}}</strong>
                            <div style="font-size:0.75rem; color:var(--text-muted);">${{item.motivo}}</div>
                        </div>
                        <span class="diag-badge-missing">${{item.metas_qtd}} Metas no Guia</span>
                    </div>
                `;
            }});
            listEl.innerHTML = html;

            // RENDERIZAR METAS EXTRAS NO DIAGNÓSTICO
            const extraListEl = document.getElementById('lista-metas-extras-diag');
            if (extraListEl) {{
                let extrasHtml = '';
                let countExtras = 0;
                PLATAFORMA_DATA.forEach(disc => {{
                    const metasExtras = disc.metas.filter(m => m.extra);
                    if (metasExtras.length > 0) {{
                        countExtras += metasExtras.length;
                        metasExtras.forEach(m => {{
                            extrasHtml += `
                                <div style="background:var(--bg-body); border:1px solid rgba(139, 92, 246, 0.35); border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap;">
                                    <div>
                                        <div style="font-size:0.88rem; font-weight:800; color:#c4b5fd;">
                                            ⭐ ${{disc.sigla}} • Meta ${{m.numero}} (Extra): ${{m.assuntos[0]}}
                                        </div>
                                        <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">
                                            Disciplina: ${{disc.disciplina}} • Arquivo: ${{disc.arquivo_alvo}}
                                        </div>
                                    </div>
                                    <button class="btn-tool" onclick="abrirMeta('${{m.id}}')" style="border-color:#8b5cf6; color:#c4b5fd; font-weight:700;">
                                        ▶ Estudar Meta Extra
                                    </button>
                                </div>
                            `;
                        }});
                    }}
                }});
                if (countExtras === 0) {{
                    extrasHtml = '<div style="color:var(--text-muted); font-size:0.85rem;">Nenhum conteúdo extra detectado nos arquivos HTML.</div>';
                }}
                extraListEl.innerHTML = extrasHtml;
            }}
        }}

        // CONTROLE DE TELAS
        function abrirVisaoQuadro() {{
            document.getElementById('view-quadro').style.display = 'block';
            document.getElementById('view-estudo').style.display = 'none';
            document.getElementById('view-disciplinas').style.display = 'none';
            document.getElementById('view-diagnostico').style.display = 'none';
            const editalEl = document.getElementById('view-meu-edital');
            if (editalEl) editalEl.style.display = 'none';
            ativarAbaBotao('tab-btn-quadro');
        }}

        function abrirVisaoEstudo() {{
            if (!metaAtivaId && listaPlanaMetas.length > 0) {{
                metaAtivaId = listaPlanaMetas[0].id;
            }}
            document.getElementById('view-quadro').style.display = 'none';
            document.getElementById('view-estudo').style.display = 'block';
            document.getElementById('view-disciplinas').style.display = 'none';
            document.getElementById('view-diagnostico').style.display = 'none';
            const editalEl = document.getElementById('view-meu-edital');
            if (editalEl) editalEl.style.display = 'none';
            ativarAbaBotao('tab-btn-estudo');
        }}

        function abrirVisaoDisciplinas() {{
            document.getElementById('view-quadro').style.display = 'none';
            document.getElementById('view-estudo').style.display = 'none';
            document.getElementById('view-disciplinas').style.display = 'block';
            document.getElementById('view-diagnostico').style.display = 'none';
            const editalEl = document.getElementById('view-meu-edital');
            if (editalEl) editalEl.style.display = 'none';
            ativarAbaBotao('tab-btn-disciplinas');
            renderizarDisciplinas();
        }}

        function abrirVisaoDiagnostico() {{
            document.getElementById('view-quadro').style.display = 'none';
            document.getElementById('view-estudo').style.display = 'none';
            document.getElementById('view-disciplinas').style.display = 'none';
            document.getElementById('view-diagnostico').style.display = 'block';
            const editalEl = document.getElementById('view-meu-edital');
            if (editalEl) editalEl.style.display = 'none';
            ativarAbaBotao('tab-btn-diag');
            renderizarDiagnostico();
        }}

        function ativarAbaBotao(btnId) {{
            document.querySelectorAll('.topbar-tab-btn').forEach(b => b.classList.remove('active'));
            const target = document.getElementById(btnId);
            if (target) target.classList.add('active');
        }}

        // TEMAS
        function mudarTema(tema) {{
            document.body.className = `theme-${{tema}}`;
            localStorage.setItem('trt4_tema', tema);
        }}

        // CONTROLE DE MODO DE VISUALIZAÇÃO (CELULAR / COMPUTADOR) INDEPENDENTE DO NAVEGADOR
        function alternarModoVisual() {{
            const modoAtual = localStorage.getItem('trt4_layout_modo') || 'auto';
            let novoModo = 'celular';
            if (modoAtual === 'celular') novoModo = 'pc';
            else if (modoAtual === 'pc') novoModo = 'auto';
            else novoModo = 'celular';
            
            localStorage.setItem('trt4_layout_modo', novoModo);
            atualizarBotaoLayout(novoModo);
            if (typeof verificarLayoutMobile === 'function') {{
                verificarLayoutMobile();
            }}
            
            const avisos = {{
                'celular': '📱 Modo Celular Ativo (Visualização Fixa para Smartphone)',
                'pc': '💻 Modo Computador Ativo (Visualização Completa de Desktop)',
                'auto': '🔄 Modo Automático (Detecta dispositivo)'
            }};
            mostrarToast(avisos[novoModo] || novoModo);
        }}

        function atualizarBotaoLayout(modo) {{
            const btnIcon = document.getElementById('layout-toggle-icon');
            const btnText = document.getElementById('layout-toggle-text');
            if (!btnIcon || !btnText) return;
            
            if (modo === 'pc') {{
                btnIcon.textContent = '💻';
                btnText.textContent = 'PC';
            }} else if (modo === 'celular') {{
                btnIcon.textContent = '📱';
                btnText.textContent = 'Celular';
            }} else {{
                btnIcon.textContent = '🔄';
                btnText.textContent = 'Auto';
            }}
        }}

        // POMODORO
        let pomoInterval = null;
        let pomoSegundos = 25 * 60;
        let pomoRodando = false;

        function togglePomodoro() {{
            if (pomoRodando) {{
                clearInterval(pomoInterval);
                pomoRodando = false;
                document.getElementById('btn-pomo-toggle').textContent = '▶';
            }} else {{
                pomoRodando = true;
                document.getElementById('btn-pomo-toggle').textContent = '⏸';
                pomoInterval = setInterval(() => {{
                    pomoSegundos--;
                    if (pomoSegundos <= 0) {{
                        clearInterval(pomoInterval);
                        pomoRodando = false;
                        document.getElementById('btn-pomo-toggle').textContent = '▶';
                        alert('⏰ Pomodoro concluído! Hora de descansar 5 minutos.');
                        pomoSegundos = 25 * 60;
                    }}
                    atualizarDisplayPomo();
                }}, 1000);
            }}
        }}

        function resetPomodoro() {{
            clearInterval(pomoInterval);
            pomoRodando = false;
            pomoSegundos = 25 * 60;
            document.getElementById('btn-pomo-toggle').textContent = '▶';
            atualizarDisplayPomo();
        }}

        function atualizarDisplayPomo() {{
            const m = Math.floor(pomoSegundos / 60).toString().padStart(2, '0');
            const s = (pomoSegundos % 60).toString().padStart(2, '0');
            document.getElementById('pomo-timer-val').textContent = `${{m}}:${{s}}`;
        }}

        // BACKUP E RESTAURAÇÃO
        function exportarBackup() {{
            const backup = {{
                metasConcluidas: progressoMetas,
                topicosPdf: progressoTopicosPdf,
                questoes: dadosQuestoes,
                cadernoErros: dadosCadernoErros,
                checklistRevisao: dadosChecklistRev,
                exportadoEm: new Date().toISOString()
            }};
            const blob = new Blob([JSON.stringify(backup, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `backup_metas_trt4_${{new Date().toISOString().slice(0,10)}}.json`;
            a.click();
            URL.revokeObjectURL(url);
            mostrarToast('Backup exportado com sucesso!');
        }}

        function importarBackup() {{
            document.getElementById('file-import').click();
        }}

        function processarArquivoImportacao(event) {{
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {{
                try {{
                    const backup = JSON.parse(e.target.result);
                    if (backup.metasConcluidas) {{
                        progressoMetas = backup.metasConcluidas;
                        localStorage.setItem('trt4_metas_concluidas', JSON.stringify(progressoMetas));
                    }}
                    if (backup.topicosPdf) {{
                        progressoTopicosPdf = backup.topicosPdf;
                        localStorage.setItem('trt4_topicos_pdf_checked', JSON.stringify(progressoTopicosPdf));
                    }}
                    if (backup.questoes) {{
                        dadosQuestoes = backup.questoes;
                        localStorage.setItem('trt4_questoes_dados', JSON.stringify(dadosQuestoes));
                    }}
                    if (backup.cadernoErros) {{
                        dadosCadernoErros = backup.cadernoErros;
                        localStorage.setItem('trt4_caderno_erros', JSON.stringify(dadosCadernoErros));
                    }}
                    if (backup.checklistRevisao) {{
                        dadosChecklistRev = backup.checklistRevisao;
                        localStorage.setItem('trt4_checklist_revisao', JSON.stringify(dadosChecklistRev));
                    }}
                    atualizarProgressoGlobal();
                    renderizarMatriz();
                    renderizarDisciplinas();
                    if (metaAtivaId) abrirMeta(metaAtivaId);
                    agendarSincronizacaoNuvem();
                    mostrarToast('Backup restaurado com sucesso!');
                }} catch (err) {{
                    alert('Erro ao processar arquivo de backup.');
                }}
            }};
            reader.readAsText(file);
        }}

        function mostrarToast(msg) {{
            const t = document.getElementById('toast-notify');
            t.textContent = msg;
            t.style.display = 'flex';
            setTimeout(() => {{ t.style.display = 'none'; }}, 2500);
        }}

        // ==========================================
        // FIREBASE SYNC & OFFLINE-FIRST ENGINE
        // ==========================================
        const firebaseConfig = {{
            apiKey: "AIzaSyBu__5cQkrf_jFZK5rgnKYC6iL-cHIeZzI",
            authDomain: "card-vendas.firebaseapp.com",
            projectId: "card-vendas",
            storageBucket: "card-vendas.firebasestorage.app",
            messagingSenderId: "686732063995",
            appId: "1:686732063995:web:c17e8cc2c0c15642432c5e"
        }};

        let usuarioFirebase = null;
        let unsubscribeDocNuvem = null;
        let timerSincNuvem = null;

        function atualizarStatusNuvem(estado, textoCompleto, textoCurto) {{
            const btn = document.getElementById('btn-cloud-sync');
            const txt = document.getElementById('cloud-sync-text');
            const ico = document.getElementById('cloud-sync-icon');
            if (!btn || !txt) return;

            btn.classList.remove('synced', 'syncing', 'offline');
            if (estado === 'synced') {{
                btn.classList.add('synced');
                ico.textContent = '🟢';
            }} else if (estado === 'syncing') {{
                btn.classList.add('syncing');
                ico.textContent = '🔄';
            }} else if (estado === 'offline') {{
                btn.classList.add('offline');
                ico.textContent = '🟡';
            }} else {{
                ico.textContent = '☁️';
            }}

            const curto = textoCurto || textoCompleto;
            txt.innerHTML = `<span class="hide-mobile">${{textoCompleto}}</span><span class="show-mobile-only">${{curto}}</span>`;
            btn.title = `${{textoCompleto}} (Sincronização Nuvem Google)`;
        }}

        function inicializarFirebase() {{
            try {{
                if (typeof firebase === 'undefined') {{
                    console.warn('[Firebase] SDK offline ou indisponível.');
                    atualizarStatusNuvem('offline', 'Modo Local');
                    return;
                }}
                if (!firebase.apps.length) {{
                    firebase.initializeApp(firebaseConfig);
                }}

                const db = firebase.firestore();
                db.enablePersistence({{ synchronizeTabs: true }}).catch((err) => {{
                    console.log('[Firebase Persistence]', err.code);
                }});

                firebase.auth().onAuthStateChanged((user) => {{
                    usuarioFirebase = user;
                    if (user) {{
                        const primeiroNome = user.displayName ? user.displayName.split(' ')[0] : 'Conectado';
                        atualizarStatusNuvem('synced', `${{primeiroNome}} • Sincronizado`, `${{primeiroNome}} ✓`);
                        ouvirAlteracoesNuvem(user.uid);
                    }} else {{
                        if (unsubscribeDocNuvem) {{
                            unsubscribeDocNuvem();
                            unsubscribeDocNuvem = null;
                        }}
                        atualizarStatusNuvem('disconnected', 'Conectar Google', 'Conectar Google');
                    }}
                }});

                window.addEventListener('online', () => {{
                    if (usuarioFirebase) {{
                        const primeiroNome = usuarioFirebase.displayName ? usuarioFirebase.displayName.split(' ')[0] : 'Conectado';
                        atualizarStatusNuvem('synced', `${{primeiroNome}} • Sincronizado`, `${{primeiroNome}} ✓`);
                        salvarDadosNuvem();
                    }}
                }});

                window.addEventListener('offline', () => {{
                    if (usuarioFirebase) {{
                        atualizarStatusNuvem('offline', 'Salvo Offline');
                    }}
                }});
            }} catch (err) {{
                console.warn('[Firebase Init Error]', err);
                atualizarStatusNuvem('offline', 'Modo Local');
            }}
        }}

        function ouvirAlteracoesNuvem(uid) {{
            try {{
                const db = firebase.firestore();
                const docRef = db.collection('usuarios').doc(uid).collection('dados').doc('metas_progresso');

                unsubscribeDocNuvem = docRef.onSnapshot((doc) => {{
                    if (doc.exists) {{
                        const dados = doc.data();
                        let houveAtualizacao = false;

                        if (dados.metasConcluidas && typeof dados.metasConcluidas === 'object') {{
                            Object.keys(dados.metasConcluidas).forEach(k => {{
                                if (dados.metasConcluidas[k] && !progressoMetas[k]) {{
                                    progressoMetas[k] = true;
                                    houveAtualizacao = true;
                                }}
                            }});
                            localStorage.setItem('trt4_metas_concluidas', JSON.stringify(progressoMetas));
                        }}

                        if (dados.subtopicos && typeof dados.subtopicos === 'object') {{
                            Object.assign(progressoSubtopicos, dados.subtopicos);
                            localStorage.setItem('trt4_subtopicos_concluidos', JSON.stringify(progressoSubtopicos));
                            houveAtualizacao = true;
                        }}

                        if (dados.topicosPdf && typeof dados.topicosPdf === 'object') {{
                            Object.assign(progressoTopicosPdf, dados.topicosPdf);
                            localStorage.setItem('trt4_topicos_pdf_checked', JSON.stringify(progressoTopicosPdf));
                            houveAtualizacao = true;
                        }}

                        if (dados.questoes && typeof dados.questoes === 'object') {{
                            Object.assign(dadosQuestoes, dados.questoes);
                            localStorage.setItem('trt4_questoes_dados', JSON.stringify(dadosQuestoes));
                            houveAtualizacao = true;
                        }}

                        if (dados.cadernoErros && typeof dados.cadernoErros === 'object') {{
                            Object.assign(dadosCadernoErros, dados.cadernoErros);
                            localStorage.setItem('trt4_caderno_erros', JSON.stringify(dadosCadernoErros));
                            houveAtualizacao = true;
                        }}

                        if (dados.checklistRevisao && typeof dados.checklistRevisao === 'object') {{
                            Object.assign(dadosChecklistRev, dados.checklistRevisao);
                            localStorage.setItem('trt4_checklist_revisao', JSON.stringify(dadosChecklistRev));
                            houveAtualizacao = true;
                        }}

                        if (dados.editalChecks && typeof dados.editalChecks === 'object') {{
                            if (dados.editalChecks.trt4) {{
                                localStorage.setItem('metas_edital_manual_trt4', JSON.stringify(dados.editalChecks.trt4));
                            }}
                            if (dados.editalChecks.trt5) {{
                                localStorage.setItem('metas_edital_manual_trt5', JSON.stringify(dados.editalChecks.trt5));
                            }}
                            houveAtualizacao = true;
                        }}

                        if (dados.editalConfig && typeof dados.editalConfig === 'object') {{
                            if (dados.editalConfig.syncEnabled !== undefined) {{
                                editalSyncMetasAtivo = dados.editalConfig.syncEnabled;
                                localStorage.setItem('metas_sync_cross_enabled', editalSyncMetasAtivo ? 'true' : 'false');
                            }}
                            if (dados.editalConfig.syncBase) {{
                                editalSyncTrtBase = dados.editalConfig.syncBase;
                                localStorage.setItem('metas_sync_base_trt', editalSyncTrtBase);
                            }}
                            houveAtualizacao = true;
                        }}

                        if (houveAtualizacao) {{
                            atualizarProgressoGlobal();
                            renderizarMatriz();
                            renderizarDisciplinas();
                            if (metaAtivaId) abrirMeta(metaAtivaId);
                        }}
                    }} else {{
                        salvarDadosNuvem();
                    }}
                }}, (err) => {{
                    console.warn('[Firestore Listen Error]', err);
                }});
            }} catch (err) {{
                console.warn('[Firestore Listen Setup Error]', err);
            }}
        }}

        function agendarSincronizacaoNuvem() {{
            if (!usuarioFirebase) return;
            atualizarStatusNuvem('syncing', 'Sincronizando...');
            clearTimeout(timerSincNuvem);
            timerSincNuvem = setTimeout(() => {{
                salvarDadosNuvem();
            }}, 700);
        }}

        async function salvarDadosNuvem() {{
            if (!usuarioFirebase) return;
            try {{
                const db = firebase.firestore();
                const docRef = db.collection('usuarios').doc(usuarioFirebase.uid).collection('dados').doc('metas_progresso');
                const checksTrt4 = JSON.parse(localStorage.getItem('metas_edital_manual_trt4') || '{{}}');
                const checksTrt5 = JSON.parse(localStorage.getItem('metas_edital_manual_trt5') || '{{}}');
                const payload = {{
                    metasConcluidas: progressoMetas,
                    subtopicos: progressoSubtopicos,
                    topicosPdf: progressoTopicosPdf,
                    questoes: dadosQuestoes,
                    cadernoErros: dadosCadernoErros,
                    checklistRevisao: dadosChecklistRev,
                    editalChecks: {{
                        trt4: checksTrt4,
                        trt5: checksTrt5
                    }},
                    editalConfig: {{
                        syncEnabled: editalSyncMetasAtivo,
                        syncBase: editalSyncTrtBase,
                        trtAtivo: editalTrtAtivo
                    }},
                    atualizadoEm: firebase.firestore.FieldValue.serverTimestamp()
                }};
                await docRef.set(payload, {{ merge: true }});
                const primeiroNome = usuarioFirebase.displayName ? usuarioFirebase.displayName.split(' ')[0] : 'Conectado';
                atualizarStatusNuvem('synced', `${{primeiroNome}} • Sincronizado`, `${{primeiroNome}} ✓`);
            }} catch (err) {{
                console.warn('[Firestore Save Error]', err);
                if (!navigator.onLine) {{
                    atualizarStatusNuvem('offline', 'Salvo Offline');
                }} else {{
                    atualizarStatusNuvem('syncing', 'Pendente');
                }}
            }}
        }}

        async function tratarCliqueNuvem() {{
            if (!usuarioFirebase) {{
                try {{
                    const provider = new firebase.auth.GoogleAuthProvider();
                    atualizarStatusNuvem('syncing', 'Conectando...');
                    await firebase.auth().signInWithPopup(provider);
                    mostrarToast('Conta Google conectada!');
                }} catch (err) {{
                    if (err.code === 'auth/popup-blocked') {{
                        const provider = new firebase.auth.GoogleAuthProvider();
                        firebase.auth().signInWithRedirect(provider);
                    }} else {{
                        alert('Erro ao conectar com Google: ' + (err.message || 'Verifique as permissões'));
                        atualizarStatusNuvem('disconnected', 'Conectar Google', 'Conectar Google');
                    }}
                }}
            }} else {{
                const info = `Conta conectada: ${{usuarioFirebase.displayName || ''}} (${{usuarioFirebase.email || ''}})\n\nEscolha uma opção:\n• Clique em OK para FORÇAR SINCRONIZAÇÃO NUVEM AGORA\n• Clique em CANCELAR se desejar desconectar da conta.`;
                if (confirm(info)) {{
                    salvarDadosNuvem();
                    mostrarToast('Sincronização na nuvem realizada!');
                }} else {{
                    if (confirm('Deseja realmente sair da sua conta Google nesta plataforma?')) {{
                        firebase.auth().signOut().then(() => {{
                            mostrarToast('Desconectado com sucesso.');
                        }});
                    }}
                }}
            }}
        }}

        // ==========================================
        // PWA E SERVICE WORKER (OFFLINE & INSTALAÇÃO)
        // ==========================================
        let deferredPrompt = null;
        const btnInstalarPwa = document.getElementById('btn-pwa-install');

        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            if (btnInstalarPwa) {{
                btnInstalarPwa.style.display = 'inline-flex';
            }}
        }});

        // SUPORTE A ABRIR META DIRETA VIA HASH (ex: index.html#meta=dc-meta-2)
        function verificarHashMeta() {{
            const hash = window.location.hash;
            if (hash && hash.includes('meta=')) {{
                const metaId = hash.split('meta=')[1]?.split('&')[0];
                if (metaId) {{
                    abrirMeta(metaId);
                }}
            }}
        }}

        function instalarPwa() {{
            if (!deferredPrompt) {{
                mostrarToast('Para instalar, use a opção "Adicionar à tela inicial" no menu do navegador.');
                return;
            }}
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {{
                if (choiceResult.outcome === 'accepted') {{
                    mostrarToast('Aplicativo instalado com sucesso!');
                }}
                deferredPrompt = null;
                if (btnInstalarPwa) btnInstalarPwa.style.display = 'none';
            }});
        }}

        window.addEventListener('appinstalled', () => {{
            mostrarToast('🎉 App instalado com sucesso na tela inicial!');
            if (btnInstalarPwa) btnInstalarPwa.style.display = 'none';
        }});

        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('./sw.js')
                    .then((reg) => {{
                        console.log('[PWA] Service Worker ativo:', reg.scope);
                        reg.onupdatefound = () => {{
                            const installingWorker = reg.installing;
                            installingWorker.onstatechange = () => {{
                                if (installingWorker.state === 'installed') {{
                                    if (navigator.serviceWorker.controller) {{
                                        mostrarToast('Nova versão disponível! Atualizando...');
                                        setTimeout(() => {{ window.location.reload(); }}, 1500);
                                    }}
                                }}
                            }};
                        }};
                    }})
                    .catch((err) => {{
                        console.warn('[PWA] Falha ao registrar Service Worker:', err);
                    }});
            }});
        }}

        // INICIALIZAÇÃO
        const temaSalvo = localStorage.getItem('trt4_tema') || 'dark';
        mudarTema(temaSalvo);
        document.querySelector('.theme-select').value = temaSalvo;

        const layoutSalvo = localStorage.getItem('trt4_layout_modo') || 'auto';
        atualizarBotaoLayout(layoutSalvo);
        if (typeof verificarLayoutMobile === 'function') verificarLayoutMobile();


        // =====================================================================
        // MÓDULO: MEU EDITAL (TJAA vs AJAJ & COMPARATIVO)
        // =====================================================================
        let editalCargoAtivo = localStorage.getItem('trt4_edital_cargo') || 'tjaa';
        let editalFiltroStatus = 'todos';
        let editalBuscaQuery = '';
        let progressoEditalManual = JSON.parse(localStorage.getItem('trt4_edital_manual_checks') || '{{}}');
        if (!progressoEditalManual.tjaa) progressoEditalManual.tjaa = {{}};
        if (!progressoEditalManual.ajaj) progressoEditalManual.ajaj = {{}};

        function abrirVisaoEdital() {{
            document.getElementById('view-quadro').style.display = 'none';
            document.getElementById('view-estudo').style.display = 'none';
            document.getElementById('view-disciplinas').style.display = 'none';
            document.getElementById('view-diagnostico').style.display = 'none';
            document.getElementById('view-meu-edital').style.display = 'flex';
            ativarAbaBotao('tab-btn-edital');
            renderizarDashboardEdital();
        }}

        function setEditalCargo(cargo) {{
            editalCargoAtivo = cargo;
            localStorage.setItem('trt4_edital_cargo', cargo);
            
            const btnTjaa = document.getElementById('btn-cargo-tjaa');
            const btnAjaj = document.getElementById('btn-cargo-ajaj');
            const btnComp = document.getElementById('btn-cargo-comp');
            if (btnTjaa) btnTjaa.className = 'edital-cargo-tab-btn' + (cargo === 'tjaa' ? ' active-tjaa' : '');
            if (btnAjaj) btnAjaj.className = 'edital-cargo-tab-btn' + (cargo === 'ajaj' ? ' active-ajaj' : '');
            if (btnComp) btnComp.className = 'edital-cargo-tab-btn' + (cargo === 'comparativo' ? ' active-comp' : '');

            const controls = document.getElementById('edital-controls-container');
            if (controls) {{
                controls.style.display = (cargo === 'comparativo') ? 'none' : 'flex';
            }}

            renderizarDashboardEdital();
        }}

        function setEditalFiltroStatus(status) {{
            editalFiltroStatus = status;
            ['todos', 'concluidos', 'pendentes'].forEach(s => {{
                const b = document.getElementById(`btn-edital-filtro-${{s}}`);
                if (b) b.classList.toggle('active', s === status);
            }});
            renderizarDashboardEdital();
        }}

        function filtrarTopicosEdital(val) {{
            editalBuscaQuery = val.trim().toLowerCase();
            const clearBtn = document.getElementById('btn-clear-edital-search');
            if (clearBtn) clearBtn.style.display = editalBuscaQuery ? 'block' : 'none';
            renderizarDashboardEdital();
        }}

        function limparBuscaEdital() {{
            editalBuscaQuery = '';
            const inp = document.getElementById('edital-search-input');
            if (inp) inp.value = '';
            const clearBtn = document.getElementById('btn-clear-edital-search');
            if (clearBtn) clearBtn.style.display = 'none';
            renderizarDashboardEdital();
        }}

        function isTopicoConcluido(cargoKey, topico) {{
            const manual = progressoEditalManual[cargoKey]?.[topico.id];
            if (manual !== undefined) return !!manual;
            if (topico.meta_ids && topico.meta_ids.length > 0) {{
                return topico.meta_ids.every(mId => !!progressoMetas[mId]);
            }}
            return false;
        }}

        function toggleEditalTopico(cargoKey, topicoId) {{
            if (!progressoEditalManual[cargoKey]) progressoEditalManual[cargoKey] = {{}};
            const cargo = EDITAIS_DATA[cargoKey];
            let topico = null;
            if (cargo) {{
                for (const d of cargo.disciplinas) {{
                    const found = d.topicos.find(t => t.id === topicoId);
                    if (found) {{ topico = found; break; }}
                }}
            }}
            if (!topico) return;

            const estadoAtual = isTopicoConcluido(cargoKey, topico);
            progressoEditalManual[cargoKey][topicoId] = !estadoAtual;
            localStorage.setItem('trt4_edital_manual_checks', JSON.stringify(progressoEditalManual));
            agendarSincronizacaoNuvem();
            renderizarDashboardEdital();
            mostrarToast(estadoAtual ? 'Tópico marcado como pendente' : '✓ Tópico concluído!');
        }}

        function sincronizarEditalComMetas() {{
            if (editalCargoAtivo === 'tjaa' || editalCargoAtivo === 'ajaj') {{
                progressoEditalManual[editalCargoAtivo] = {{}};
                localStorage.setItem('trt4_edital_manual_checks', JSON.stringify(progressoEditalManual));
                renderizarDashboardEdital();
                mostrarToast('Tópicos sincronizados com as metas concluídas!');
            }}
        }}

        function toggleEditalAccordion(discSigla) {{
            const el = document.getElementById(`edital-card-${{discSigla}}`);
            if (el) el.classList.toggle('collapsed');
        }}

        function toggleTodosAccordionsEdital(expandir) {{
            document.querySelectorAll('.edital-disc-card').forEach(card => {{
                if (expandir) card.classList.remove('collapsed');
                else card.classList.add('collapsed');
            }});
        }}

        function renderizarDashboardEdital() {{
            const kpisEl = document.getElementById('edital-kpis-container');
            const contentEl = document.getElementById('edital-content-area');
            if (!kpisEl || !contentEl || !EDITAIS_DATA) return;

            // VISÃO COMPARATIVA
            if (editalCargoAtivo === 'comparativo') {{
                renderizarVisaoComparativo(kpisEl, contentEl);
                return;
            }}

            // VISÃO TJAA OU AJAJ
            const cargoKey = editalCargoAtivo;
            const cargoData = EDITAIS_DATA[cargoKey];
            if (!cargoData) return;

            const totalTopicos = cargoData.total_topicos || 0;
            let concluidosCount = 0;
            const discStats = {{}};

            cargoData.disciplinas.forEach(d => {{
                let dConcluidos = 0;
                d.topicos.forEach(t => {{
                    if (isTopicoConcluido(cargoKey, t)) {{
                        concluidosCount++;
                        dConcluidos++;
                    }}
                }});
                discStats[d.sigla] = {{
                    total: d.topicos.length,
                    concluidos: dConcluidos,
                    pct: d.topicos.length > 0 ? Math.round((dConcluidos / d.topicos.length) * 100) : 0
                }};
            }});

            const pctGeral = totalTopicos > 0 ? Math.round((concluidosCount / totalTopicos) * 100) : 0;
            const pendentesCount = totalTopicos - concluidosCount;
            const cargoTemaCor = cargoKey === 'tjaa' ? '#3b82f6' : '#8b5cf6';

            // 1. Renderizar KPIs
            kpisEl.innerHTML = `
                <div class="edital-kpi-card" style="border-left: 4px solid ${{cargoTemaCor}};">
                    <div class="edital-kpi-header">
                        <span>Progresso Geral do Edital</span>
                        <span>🎯</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="color:${{cargoTemaCor}};">${{pctGeral}}%</span>
                        <span class="edital-kpi-sub">${{concluidosCount}} de ${{totalTopicos}} tópicos</span>
                    </div>
                    <div class="edital-progress-bar-wrap">
                        <div class="edital-progress-bar-fill" style="width: ${{pctGeral}}%; background: linear-gradient(90deg, ${{cargoTemaCor}}, #10b981);"></div>
                    </div>
                </div>

                <div class="edital-kpi-card">
                    <div class="edital-kpi-header">
                        <span>Tópicos Concluídos</span>
                        <span>✅</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="color:var(--accent-green);">${{concluidosCount}}</span>
                        <span class="edital-kpi-sub">de ${{totalTopicos}} totais</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">Mapeados nas metas e validados</span>
                </div>

                <div class="edital-kpi-card">
                    <div class="edital-kpi-header">
                        <span>Tópicos Pendentes</span>
                        <span>⏳</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="color:var(--accent-gold);">${{pendentesCount}}</span>
                        <span class="edital-kpi-sub">a estudar</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">${{totalTopicos > 0 ? (100 - pctGeral) : 0}}% restante para cobrir o edital</span>
                </div>

                <div class="edital-kpi-card">
                    <div class="edital-kpi-header">
                        <span>Cobertura no Ciclo</span>
                        <span>📚</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value">${{cargoKey === 'tjaa' ? '100%' : '72.2%'}}</span>
                        <span class="edital-kpi-sub">${{cargoKey === 'tjaa' ? '10 matérias ativas' : '9 de 11 matérias'}}</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">${{cargoKey === 'tjaa' ? 'Todas as matérias no ciclo oficial' : 'Exclusivos: Direito Civil e Processo Civil'}}</span>
                </div>
            `;

            // 2. Renderizar Accordions de Disciplinas e Tópicos
            let htmlAccordions = '';

            cargoData.disciplinas.forEach(d => {{
                const s = discStats[d.sigla] || {{ total: d.topicos.length, concluidos: 0, pct: 0 }};
                
                // Filtrar tópicos
                const topicosFiltrados = d.topicos.filter(t => {{
                    const concluido = isTopicoConcluido(cargoKey, t);
                    if (editalFiltroStatus === 'concluidos' && !concluido) return false;
                    if (editalFiltroStatus === 'pendentes' && concluido) return false;

                    if (editalBuscaQuery) {{
                        const noTexto = (t.topico || '').toLowerCase().includes(editalBuscaQuery);
                        const naMeta = (t.metas_texto || '').toLowerCase().includes(editalBuscaQuery);
                        const naSigla = d.sigla.toLowerCase().includes(editalBuscaQuery);
                        const noNome = d.nome.toLowerCase().includes(editalBuscaQuery);
                        if (!noTexto && !naMeta && !naSigla && !noNome) return false;
                    }}
                    return true;
                }});

                if (topicosFiltrados.length === 0 && (editalBuscaQuery || editalFiltroStatus !== 'todos')) {{
                    return; // Esconde matéria vazia se houver filtro ativo
                }}

                const isAnalistaExclusivo = (d.sigla === 'CIV' || d.sigla === 'CPC');

                htmlAccordions += `
                    <div class="edital-disc-card" id="edital-card-${{d.sigla}}">
                        <div class="edital-disc-header" onclick="toggleEditalAccordion('${{d.sigla}}')">
                            <div class="edital-disc-title-wrap">
                                <span class="edital-disc-sigla-badge" style="background:${{isAnalistaExclusivo ? 'rgba(168,85,247,0.2)' : 'rgba(56,189,248,0.2)'}}; color:${{isAnalistaExclusivo ? '#c084fc' : '#38bdf8'}}; border: 1px solid ${{isAnalistaExclusivo ? 'rgba(168,85,247,0.4)' : 'rgba(56,189,248,0.4)'}};">${{d.sigla}}</span>
                                <span class="edital-disc-name">${{d.nome}} ${{isAnalistaExclusivo ? '<span class="edital-exclusive-badge" style="margin-left:6px;">⚖️ Exclusivo Analista</span>' : ''}}</span>
                            </div>
                            <div class="edital-disc-stats">
                                <span class="edital-disc-counter">${{s.concluidos}}/${{s.total}} (${{s.pct}}%)</span>
                                <div class="edital-disc-bar-wrap">
                                    <div style="height:100%; width:${{s.pct}}%; background:${{s.pct === 100 ? '#10b981' : '#3b82f6'}}; border-radius:999px;"></div>
                                </div>
                                <span class="edital-disc-chevron">▼</span>
                            </div>
                        </div>

                        <div class="edital-disc-body">
                            ${{topicosFiltrados.length === 0 ? '<div style="padding:10px; color:var(--text-muted); font-size:0.84rem;">Nenhum tópico correspondente ao filtro.</div>' : ''}}
                            ${{topicosFiltrados.map(t => {{
                                const concluido = isTopicoConcluido(cargoKey, t);
                                return `
                                    <div class="edital-topic-row ${{concluido ? 'is-done' : ''}}" id="topico-row-${{t.id}}">
                                        <div class="edital-topic-left">
                                            <input type="checkbox" class="edital-topic-chk" ${{concluido ? 'checked' : ''}} 
                                                   onchange="toggleEditalTopico('${{cargoKey}}', '${{t.id}}')" 
                                                   title="${{concluido ? 'Marcar como pendente' : 'Marcar como concluído'}}">
                                            <div class="edital-topic-content">
                                                <div class="edital-topic-title">${{t.topico}}</div>
                                                <div class="edital-topic-badges">
                                                    ${{isAnalistaExclusivo ? 
                                                        '<span class="edital-exclusive-badge">📖 Conteúdo Específico de Analista</span>' : 
                                                        (t.meta_ids && t.meta_ids.length > 0 ? 
                                                            t.meta_ids.map(mId => {{
                                                                const mDone = !!progressoMetas[mId];
                                                                const mNum = mId.split('-meta-')[1] || '';
                                                                return `<button class="edital-meta-btn ${{mDone ? 'meta-done' : ''}}" onclick="abrirMeta('${{mId}}')" title="Abrir estudo da Meta ${{mNum}}">🎯 Meta ${{mNum}} ${{mDone ? '✓' : ''}}</button>`;
                                                            }}).join('') : 
                                                            '<span style="font-size:0.72rem; color:var(--text-muted);">Sem meta mapeada</span>')
                                                    }}
                                                </div>
                                            </div>
                                        </div>
                                        <span class="edital-status-tag ${{concluido ? 'done' : 'pending'}}">
                                            ${{concluido ? '✓ Concluído' : '⏳ Pendente'}}
                                        </span>
                                    </div>
                                `;
                            }}).join('')}}
                        </div>
                    </div>
                `;
            }});

            if (htmlAccordions === '') {{
                htmlAccordions = `
                    <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:30px; text-align:center; color:var(--text-muted);">
                        <p style="font-size:1.1rem; margin-bottom:8px;">🔍 Nenhum tópico encontrado para a busca "${{editalBuscaQuery}}".</p>
                        <button class="btn-layout-toggle" onclick="limparBuscaEdital()">Limpar Busca</button>
                    </div>
                `;
            }}

            contentEl.innerHTML = htmlAccordions;
        }}

        function renderizarVisaoComparativo(kpisEl, contentEl) {{
            const tjaa = EDITAIS_DATA['tjaa'];
            const ajaj = EDITAIS_DATA['ajaj'];
            if (!tjaa || !ajaj) return;

            // KPIs Comparativos
            kpisEl.innerHTML = `
                <div class="edital-kpi-card" style="border-left: 4px solid #10b981;">
                    <div class="edital-kpi-header">
                        <span>Sobreposição de Conteúdo</span>
                        <span>🤝</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="color:var(--accent-green);">~72%</span>
                        <span class="edital-kpi-sub">Tronco Comum</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">9 matérias idênticas ou equivalentes em ambos os cargos</span>
                </div>

                <div class="edital-kpi-card" style="border-left: 4px solid #3b82f6;">
                    <div class="edital-kpi-header">
                        <span>TJAA • Técnico</span>
                        <span>🏛️</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="color:#60a5fa;">116</span>
                        <span class="edital-kpi-sub">tópicos no edital</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">100% coberto pelo ciclo oficial (10 matérias)</span>
                </div>

                <div class="edital-kpi-card" style="border-left: 4px solid #8b5cf6;">
                    <div class="edital-kpi-header">
                        <span>AJAJ • Analista</span>
                        <span>⚖️</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="color:#c084fc;">151</span>
                        <span class="edital-kpi-sub">tópicos no edital</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">109 no tronco comum + 42 tópicos exclusivos</span>
                </div>

                <div class="edital-kpi-card" style="border-left: 4px solid #f59e0b;">
                    <div class="edital-kpi-header">
                        <span>Diferença Estratégica</span>
                        <span>⚡</span>
                    </div>
                    <div class="edital-kpi-main">
                        <span class="edital-kpi-value" style="font-size:1.3rem; color:var(--accent-gold);">ADM vs CIV/CPC</span>
                    </div>
                    <span style="font-size:0.75rem; color:var(--text-muted);">Técnico exige ADM; Analista exige Civil e Processo Civil</span>
                </div>
            `;

            // Tabela Detalhada de Comparação
            const disciplinasLinhas = [
                {{ sigla: 'PORT', nome: 'Língua Portuguesa', tjaa: 17, ajaj: 17, dif: 'Idêntico', tipo: 'tronco' }},
                {{ sigla: 'RLM', nome: 'Raciocínio Lógico-Matemático', tjaa: 5, ajaj: 5, dif: 'Idêntico', tipo: 'tronco' }},
                {{ sigla: 'INFO', nome: 'Informática', tjaa: 5, ajaj: 5, dif: 'Idêntico', tipo: 'tronco' }},
                {{ sigla: 'DH', nome: 'Direitos Humanos', tjaa: 14, ajaj: 14, dif: 'Idêntico', tipo: 'tronco' }},
                {{ sigla: 'LEG', nome: 'Legislação Institucional', tjaa: 5, ajaj: 5, dif: 'Idêntico', tipo: 'tronco' }},
                {{ sigla: 'DC', nome: 'Direito Constitucional', tjaa: 19, ajaj: 21, dif: '+2 tópicos em AJAJ (Funções da Justiça)', tipo: 'tronco' }},
                {{ sigla: 'DA', nome: 'Direito Administrativo', tjaa: 6, ajaj: 4, dif: 'TJAA detalha licitações/contratos', tipo: 'tronco' }},
                {{ sigla: 'DT', nome: 'Direito do Trabalho', tjaa: 20, ajaj: 21, dif: '+1 tópico em AJAJ', tipo: 'tronco' }},
                {{ sigla: 'DPT', nome: 'Direito Processual do Trabalho', tjaa: 10, ajaj: 17, dif: '+7 tópicos em AJAJ (Recursos e Execução)', tipo: 'tronco' }},
                {{ sigla: 'ADM', nome: 'Administração e Gestão de Pessoas', tjaa: 15, ajaj: 0, dif: 'Exclusivo do cargo de Técnico (TJAA)', tipo: 'tjaa' }},
                {{ sigla: 'CIV', nome: 'Direito Civil', tjaa: 0, ajaj: 20, dif: 'Exclusivo do cargo de Analista (AJAJ)', tipo: 'ajaj' }},
                {{ sigla: 'CPC', nome: 'Direito Processual Civil', tjaa: 0, ajaj: 22, dif: 'Exclusivo do cargo de Analista (AJAJ)', tipo: 'ajaj' }}
            ];

            contentEl.innerHTML = `
                <div class="comp-box" style="margin-bottom:18px;">
                    <h3 style="font-size:1.1rem; color:var(--text-heading); margin-bottom:8px; display:flex; align-items:center; gap:8px;">
                        <span>📊</span> Comparativo Matéria a Matéria: TJAA vs AJAJ
                    </h3>
                    <p style="font-size:0.84rem; color:var(--text-muted); margin-bottom:14px;">
                        Veja a distribuição exata de tópicos em cada matéria e onde os editais convergem ou exigem esforço específico.
                    </p>

                    <div class="comp-table-wrap">
                        <table class="comp-table">
                            <thead>
                                <tr>
                                    <th>Matéria</th>
                                    <th>TJAA (Técnico)</th>
                                    <th>AJAJ (Analista)</th>
                                    <th>Classificação</th>
                                    <th>Análise Comparativa</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{disciplinasLinhas.map(row => `
                                    <tr>
                                        <td><strong>${{row.sigla}}</strong> • ${{row.nome}}</td>
                                        <td><span style="font-weight:700; color:${{row.tjaa > 0 ? '#60a5fa' : 'var(--text-muted)'}};">${{row.tjaa > 0 ? row.tjaa + ' tópicos' : '—'}}</span></td>
                                        <td><span style="font-weight:700; color:${{row.ajaj > 0 ? '#c084fc' : 'var(--text-muted)'}};">${{row.ajaj > 0 ? row.ajaj + ' tópicos' : '—'}}</span></td>
                                        <td>
                                            ${{row.tipo === 'tronco' ? '<span class="comp-badge-tronco">🤝 Tronco Comum</span>' : 
                                              (row.tipo === 'tjaa' ? '<span class="comp-badge-tjaa">🏛️ Exclusivo TJAA</span>' : '<span class="comp-badge-ajaj">⚖️ Exclusivo AJAJ</span>')}}
                                        </td>
                                        <td style="font-size:0.82rem; color:var(--text-muted);">${{row.dif}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="comp-card-grid">
                    <div class="comp-box" style="border-left:4px solid #3b82f6;">
                        <h4 style="color:#60a5fa; font-size:1rem; margin-bottom:8px;">💡 Estratégia: Foco em Técnico (TJAA)</h4>
                        <ul style="font-size:0.84rem; color:var(--text-body); line-height:1.6; margin-left:18px;">
                            <li><strong>100% no Ciclo:</strong> Todas as 10 matérias estão estruturadas com metas, teoria e questões no nosso sistema.</li>
                            <li><strong>Atenção Especial:</strong> Dedicar tempo à <strong>Administração Geral e Gestão de Pessoas</strong> (15 tópicos), peso relevante para Técnico.</li>
                            <li><strong>Processo do Trabalho:</strong> Edital mais enxuto (10 tópicos focados no rito sumário, ordinário e audiência).</li>
                        </ul>
                    </div>

                    <div class="comp-box" style="border-left:4px solid #8b5cf6;">
                        <h4 style="color:#c084fc; font-size:1rem; margin-bottom:8px;">⚖️ Estratégia: Foco em Analista (AJAJ)</h4>
                        <ul style="font-size:0.84rem; color:var(--text-body); line-height:1.6; margin-left:18px;">
                            <li><strong>Aproveitamento Alto:</strong> 109 dos 151 tópicos são compartilhados com o ciclo da plataforma.</li>
                            <li><strong>Gargalo Específico:</strong> Exige estudo à parte de <strong>Direito Civil (20 tópicos)</strong> e <strong>Processo Civil (22 tópicos)</strong>.</li>
                            <li><strong>Aprofundamento:</strong> Processo do Trabalho ganha mais 7 tópicos (Recursos em espécie e Execução trabalhista).</li>
                        </ul>
                    </div>
                </div>
            `;
        }}



        

        // ROLAGEM HORIZONTAL DA MATRIZ DO QUADRO DE METAS
        function rolarMatrizQuadro(delta) {{
            const el = document.getElementById('matriz-container-el') || document.querySelector('.matriz-container');
            if (el) {{
                el.scrollBy({{ left: delta, behavior: 'smooth' }});
            }}
        }}

        // Habilitar arrasto com mouse (Drag-to-scroll) para simuladores e computadores
        function inicializarArrastoMatriz() {{
            const container = document.getElementById('matriz-container-el') || document.querySelector('.matriz-container');
            if (!container) return;

            let isDown = false;
            let startX = 0;
            let scrollLeft = 0;
            let hasMoved = false;

            container.addEventListener('mousedown', (e) => {{
                if (e.button !== 0) return;
                isDown = true;
                hasMoved = false;
                container.classList.add('is-dragging');
                startX = e.pageX - container.offsetLeft;
                scrollLeft = container.scrollLeft;
            }});

            window.addEventListener('mouseup', () => {{
                if (isDown) {{
                    isDown = false;
                    container.classList.remove('is-dragging');
                    setTimeout(() => {{ hasMoved = false; }}, 60);
                }}
            }});

            container.addEventListener('mousemove', (e) => {{
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const walk = (x - startX) * 1.5;
                if (Math.abs(walk) > 4) {{
                    hasMoved = true;
                }}
                container.scrollLeft = scrollLeft - walk;
            }});

            container.addEventListener('click', (e) => {{
                if (hasMoved) {{
                    e.preventDefault();
                    e.stopPropagation();
                }}
            }}, true);
        }}
    

        // ==========================================================================
        // GERENCIAMENTO DA SIDEBAR DE TRIBUNAIS (TRTs)
        // ==========================================================================
        const TRTS_PREDEFINIDOS = [
            {{
                id: "trt-4",
                numero: "04",
                sigla: "TRT-7",
                uf: "RS",
                regiao: "Ceará",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-04-RS"
            }},
            {{
                id: "trt-5",
                numero: "05",
                sigla: "TRT-5",
                uf: "BA",
                regiao: "Bahia",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-05-BA"
            }},
            {{
                id: "trt-6",
                numero: "06",
                sigla: "TRT-6",
                uf: "PE",
                regiao: "Pernambuco",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-06-PE"
            }},
            {{
                id: "trt-7",
                numero: "07",
                sigla: "TRT-7",
                uf: "CE",
                regiao: "Ceará",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-07-CE"
            }},
            {{
                id: "trt-8",
                numero: "08",
                sigla: "TRT-8",
                uf: "PA/AP",
                regiao: "Pará e Amapá",
                banca: "Cebraspe",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-08-PA"
            }},
            {{
                id: "trt-12",
                numero: "12",
                sigla: "TRT-12",
                uf: "SC",
                regiao: "Santa Catarina",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-12-SC"
            }},
            {{
                id: "trt-15",
                numero: "15",
                sigla: "TRT-15",
                uf: "SP Interior",
                regiao: "Campinas",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-15-SP"
            }}
        ];

        let trtAtivoId = localStorage.getItem('estudos_dl_trt_ativo') || 'trt-4';

        function obterListaTRTs() {{
            try {{
                const salvo = localStorage.getItem('estudos_dl_trts_lista');
                if (salvo) {{
                    const parsed = JSON.parse(salvo);
                    if (Array.isArray(parsed) && parsed.length > 0) return parsed;
                }}
            }} catch (e) {{
                console.error("Erro ao carregar lista de TRTs:", e);
            }}
            return TRTS_PREDEFINIDOS;
        }}

        function salvarListaTRTs(lista) {{
            try {{
                localStorage.setItem('estudos_dl_trts_lista', JSON.stringify(lista));
            }} catch (e) {{
                console.error("Erro ao salvar lista de TRTs:", e);
            }}
        }}

        function selecionarTribunal(id) {{
            const lista = obterListaTRTs();
            const trt = lista.find(t => t.id === id);
            if (!trt) return;

            trtAtivoId = id;
            localStorage.setItem('estudos_dl_trt_ativo', id);

            aplicarTribunalAtivo(trt);
            renderizarListaTRTsSidebar();

            mostrarToast(`🏛️ Tribunal alternado para ${{trt.sigla}} (${{trt.regiao}})!`);
            setTimeout(() => {{
                fecharSidebarTRT();
            }}, 200);
        }}

        function aplicarTribunalAtivo(trt) {{
            if (!trt) {{
                const lista = obterListaTRTs();
                trt = lista.find(t => t.id === trtAtivoId) || lista[0];
            }}
            if (!trt) return;

            // 1. Atualizar pill no topo
            const pillText = document.querySelector('#btn-trt-pill .trt-text');
            if (pillText) pillText.textContent = trt.sigla;

            // 2. Atualizar título da topbar
            const brandTitle = document.querySelector('.topbar-title h1');
            if (brandTitle) {{
                brandTitle.innerHTML = `Estudos DL <span style="font-size: 0.68rem; font-weight: 700; color: #38bdf8; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); padding: 1px 6px; border-radius: 5px; margin-left: 6px; vertical-align: middle;">${{trt.sigla}}</span>`;
            }}

            // 3. Atualizar subtítulo da topbar
            const brandSub = document.querySelector('.topbar-title p');
            if (brandSub) brandSub.textContent = `Metas de Estudos • ${{trt.regiao}} (${{trt.banca}})`;

            // 4. Atualizar banner do Quadro de Metas
            const bannerCiclo = document.querySelector('#view-quadro .quadro-header-info span');
            if (bannerCiclo) bannerCiclo.textContent = `• Ciclo Oficial ${{trt.sigla}} (${{trt.regiao}} - ${{trt.banca}})`;

            // 5. Atualizar aba Meu Edital
            const editalHeader = document.querySelector('#view-meu-edital h2');
            if (editalHeader) editalHeader.innerHTML = `📑 Meu Edital • ${{trt.sigla}} (${{trt.uf}})`;

            // 6. Atualizar Legislação Específica em Disciplinas
            const legCard = document.querySelector('.disciplina-card[data-sigla="LEG"] h3');
            if (legCard) legCard.textContent = `Legislação Específica (${{trt.sigla}} - ${{trt.uf}})`;

            // 7. Atualizar card na Sidebar
            const cardBadge = document.getElementById('sidebar-current-badge');
            const cardNome = document.getElementById('sidebar-current-nome');
            const cardBanca = document.getElementById('sidebar-current-banca');
            if (cardBadge) cardBadge.textContent = `${{trt.sigla}} (${{trt.uf}})`;
            if (cardNome) cardNome.textContent = `Tribunal Regional do Trabalho da ${{trt.numero}}ª Região (${{trt.regiao}})`;
            if (cardBanca) cardBanca.textContent = trt.banca || 'FCC';
        }}

        function toggleSidebarTRT(e) {{
            if (e) {{
                e.stopPropagation();
                e.preventDefault();
            }}
            const el = document.getElementById('sidebar-trt');
            if (el && el.classList.contains('open')) {{
                fecharSidebarTRT();
            }} else {{
                abrirSidebarTRT();
            }}
        }}

        function abrirSidebarTRT() {{
            const sidebar = document.getElementById('sidebar-trt');
            const overlay = document.getElementById('sidebar-trt-overlay');
            if (sidebar && overlay) {{
                sidebar.classList.add('open');
                overlay.classList.add('open');
                renderizarListaTRTsSidebar();
            }}
        }}

        function fecharSidebarTRT() {{
            const sidebar = document.getElementById('sidebar-trt');
            const overlay = document.getElementById('sidebar-trt-overlay');
            if (sidebar && overlay) {{
                sidebar.classList.remove('open');
                overlay.classList.remove('open');
            }}
        }}

        function renderizarListaTRTsSidebar() {{
            const lista = obterListaTRTs();
            const container = document.getElementById('sidebar-trt-list');
            const countEl = document.getElementById('sidebar-trt-count');
            if (!container) return;

            if (countEl) countEl.textContent = `${{lista.length}} disponíveis`;

            const badgesCores = ['badge-trt-blue', 'badge-trt-purple', 'badge-trt-amber', 'badge-trt-emerald'];

            container.innerHTML = lista.map((trt, idx) => {{
                const corBadge = badgesCores[idx % badgesCores.length];
                const isActive = trt.id === trtAtivoId;
                const isCustom = trt.is_custom === true;
                const urlDestino = trt.url || 'https://github.com/daniellucas2025/caderno-do-trt';

                return `
                    <div class="sidebar-trt-item ${{isActive ? 'is-active' : ''}}">
                        <div class="trt-item-left" onclick="selecionarTribunal('${{trt.id}}')" style="cursor: pointer;" title="Clique para alternar para ${{trt.sigla}}">
                            <span class="trt-item-badge ${{corBadge}}">${{trt.sigla || 'TRT'}}</span>
                            <div class="trt-item-info">
                                <div class="trt-item-title">${{trt.regiao}} (${{trt.uf}})</div>
                                <div class="trt-item-sub">Banca ${{trt.banca || 'FCC'}} • ${{trt.status || 'Disponível'}}</div>
                            </div>
                        </div>
                        <div class="trt-item-actions">
                            ${{isActive ? `
                                <span class="btn-trt-action btn-trt-current" title="Tribunal atualmente ativo">✓ Ativo</span>
                            ` : `
                                <button type="button" class="btn-trt-action" onclick="selecionarTribunal('${{trt.id}}')" title="Alternar e estudar para ${{trt.sigla}}">
                                    <span>Alternar</span> ➔
                                </button>
                            `}}
                            <a href="${{urlDestino}}" target="_blank" rel="noopener noreferrer" class="btn-trt-repo-link" title="Abrir pasta/repositório no GitHub ↗">
                                📂
                            </a>
                            ${{isCustom ? `
                                <button class="btn-trt-delete" onclick="removerTRTCustomizado('${{trt.id}}')" title="Remover este TRT">✕</button>
                            ` : ''}}
                        </div>
                    </div>
                `;
            }}).join('');
        }}

        function toggleFormNovoTRT(forcar) {{
            const form = document.getElementById('form-novo-trt');
            const btn = document.getElementById('btn-add-trt-toggle');
            if (!form) return;

            const deveExibir = forcar !== undefined ? forcar : (form.style.display === 'none' || form.style.display === '');
            form.style.display = deveExibir ? 'flex' : 'none';
            if (btn) btn.style.display = deveExibir ? 'none' : 'flex';

            if (deveExibir) {{
                const numInput = document.getElementById('novo-trt-num');
                if (numInput) numInput.focus();
            }}
        }}

        function salvarNovoTRT(e) {{
            e.preventDefault();
            const num = document.getElementById('novo-trt-num').value.trim();
            const uf = document.getElementById('novo-trt-uf').value.trim().toUpperCase();
            const regiao = document.getElementById('novo-trt-regiao').value.trim();
            const banca = document.getElementById('novo-trt-banca').value;
            const status = document.getElementById('novo-trt-status').value;
            const url = document.getElementById('novo-trt-url').value.trim();

            if (!num || !uf || !regiao) {{
                alert("Por favor, preencha todos os campos obrigatórios.");
                return;
            }}

            const numFmt = num.length === 1 ? `0${{num}}` : num;
            const sigla = `TRT-${{num}}`;
            const novoId = `trt-custom-${{num}}-${{uf.toLowerCase()}}`;

            const lista = obterListaTRTs();
            const jaExiste = lista.some(t => t.id === novoId || (t.numero === numFmt && t.uf === uf));
            if (jaExiste) {{
                alert(`O TRT-${{num}} (${{uf}}) já está cadastrado na sua lista.`);
                return;
            }}

            const novoObj = {{
                id: novoId,
                numero: numFmt,
                sigla: sigla,
                uf: uf,
                regiao: regiao,
                banca: banca,
                status: status,
                metas_qtd: 177,
                materias_qtd: 10,
                url: url || `https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-${{numFmt}}-${{uf}}`,
                is_current: false,
                is_custom: true
            }};

            lista.push(novoObj);
            salvarListaTRTs(lista);

            document.getElementById('form-novo-trt').reset();
            toggleFormNovoTRT(false);
            renderizarListaTRTsSidebar();
            selecionarTribunal(novoId);
        }}

        function removerTRTCustomizado(id) {{
            if (!confirm("Deseja remover este tribunal da sua lista?")) return;
            let lista = obterListaTRTs();
            lista = lista.filter(t => t.id !== id);
            salvarListaTRTs(lista);
            if (trtAtivoId === id) {{
                selecionarTribunal('trt-4');
            }} else {{
                renderizarListaTRTsSidebar();
            }}
        }}

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') fecharSidebarTRT();
            if (e.altKey && (e.key === 't' || e.key === 'T')) {{
                e.preventDefault();
                toggleSidebarTRT();
            }}
        }});

        atualizarProgressoGlobal();
        renderizarMatriz();
        inicializarArrastoMatriz();
        abrirVisaoQuadro();
        inicializarFirebase();
        verificarHashMeta();
        renderizarListaTRTsSidebar();
        aplicarTribunalAtivo();
        window.addEventListener('hashchange', verificarHashMeta);
    </script>
</body>
</html>
"""

    # Gera APENAS index.html (evita duplicar arquivos idênticos no GitHub)
    if caminho_saida.name.lower() == "plataforma_metas.html":
        caminho_saida = caminho_saida.parent / "index.html"
    caminho_saida.write_text(template_html, encoding="utf-8")
    print(f"\n[OK] Plataforma Oficial gerada com sucesso!")
    print(f"     Arquivo principal (PWA / GitHub Pages): {caminho_saida}")

def main():
    parser = argparse.ArgumentParser(description="Gerador da Plataforma de Metas - TRT-7")
    parser.add_argument("--dir", "-d", default=".", help="Diretório onde procurar arquivos .html (padrão: pasta METAS)")
    parser.add_argument("--output", "-o", default="index.html", help="Nome do arquivo de saída (padrão: index.html)")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    trt_root = script_dir.parent

    # Suporte para estrutura modular TRT-XX-UF (Cadernos-Completos e Plataforma)
    cadernos_dir = trt_root / "Cadernos-Completos"
    plataforma_dir = trt_root / "Plataforma"

    if cadernos_dir.exists():
        metas_dir = cadernos_dir
    elif (script_dir / "METAS").exists():
        metas_dir = script_dir / "METAS"
    else:
        metas_dir = Path(args.dir).resolve()

    print(f"[*] Varrendo cadernos em: {metas_dir}")
    catalogo_vinculado, ausentes_finais = vincular_conteudo_as_metas(METAS_CATALOGO, metas_dir, DISCIPLINAS_AUSENTES_PDF)

    if plataforma_dir.exists():
        caminho_saida = plataforma_dir / args.output
    else:
        caminho_saida = metas_dir / args.output

    gerar_html_plataforma(catalogo_vinculado, ausentes_finais, caminho_saida)

if __name__ == "__main__":
    main()
