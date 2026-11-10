# -*- coding: utf-8 -*-
"""
Gerador do Portal Master Hub - CADERNO DO TRT
Gera a página raiz index.html para o GitHub Pages (https://daniellucas2025.github.io/caderno-do-trt/)
com a aba '🏛️ Hub de TRTs' como tela inicial interativa e acesso a todos os tribunais regionais.
"""

import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TRT4_INDEX = BASE_DIR / "TRT-04-RS" / "Plataforma" / "index.html"
OUTPUT_INDEX = BASE_DIR / "index.html"

HUB_CSS = """
        /* ==========================================================================
           ESTILOS DO MASTER HUB DE TRTS (TELA INICIAL)
           ========================================================================== */
        #view-hub {
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px 20px 60px;
        }

        .hub-hero {
            background: linear-gradient(135deg, rgba(17, 24, 39, 0.95), rgba(15, 23, 42, 0.98));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 36px 32px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 45px -15px rgba(0, 0, 0, 0.7);
        }

        .hub-hero::before {
            content: '';
            position: absolute;
            top: -120px;
            right: -100px;
            width: 380px;
            height: 380px;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.15), transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .hub-hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 5px 14px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #38bdf8;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 16px;
        }

        .hub-hero h1 {
            font-size: 2.1rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.25;
            margin-bottom: 12px;
            letter-spacing: -0.02em;
        }

        .hub-hero p {
            color: #94a3b8;
            font-size: 1.02rem;
            line-height: 1.6;
            max-width: 880px;
            margin-bottom: 28px;
        }

        .hub-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
        }

        .hub-stat-card {
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            backdrop-filter: blur(10px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .hub-stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.3);
        }

        .hub-stat-icon {
            font-size: 2rem;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .hub-stat-number {
            font-size: 1.55rem;
            font-weight: 800;
            color: #f1f5f9;
            line-height: 1.1;
        }

        .hub-stat-label {
            font-size: 0.78rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }

        .hub-filter-bar {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 24px;
            padding: 16px 20px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
        }

        .hub-filter-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .hub-pill-btn {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #94a3b8;
            font-size: 0.84rem;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 999px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .hub-pill-btn:hover {
            background: rgba(51, 65, 85, 0.8);
            color: #f8fafc;
            border-color: rgba(255, 255, 255, 0.15);
        }

        .hub-pill-btn.active {
            background: #2563eb;
            color: #ffffff;
            border-color: #3b82f6;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        }

        .hub-search-box {
            position: relative;
            min-width: 280px;
            flex: 1;
            max-width: 380px;
        }

        .hub-search-input {
            width: 100%;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #f1f5f9;
            padding: 9px 14px 9px 38px;
            border-radius: 10px;
            font-size: 0.88rem;
            outline: none;
            transition: border-color 0.2s;
        }

        .hub-search-input:focus {
            border-color: #38bdf8;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
        }

        .hub-search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #64748b;
            font-size: 0.95rem;
            pointer-events: none;
        }

        .hub-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 22px;
            margin-bottom: 36px;
        }

        .hub-card {
            background: linear-gradient(135deg, rgba(20, 26, 43, 0.95), rgba(15, 20, 32, 0.95));
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        }

        .hub-card:hover {
            transform: translateY(-4px);
            border-color: rgba(56, 189, 248, 0.35);
            box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
        }

        .hub-card.is-active-trt {
            border-color: #38bdf8;
            background: linear-gradient(135deg, rgba(23, 37, 84, 0.85), rgba(15, 23, 42, 0.95));
            box-shadow: 0 10px 30px -5px rgba(56, 189, 248, 0.25);
        }

        .hub-card-active-tag {
            position: absolute;
            top: 14px;
            right: 16px;
            background: #0284c7;
            color: #ffffff;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .hub-card-header {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            margin-bottom: 16px;
        }

        .hub-card-badge {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.05rem;
            color: #ffffff;
            flex-shrink: 0;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .hub-badge-sul { background: linear-gradient(135deg, #0284c7, #0369a1); }
        .hub-badge-nordeste { background: linear-gradient(135deg, #d97706, #b45309); }
        .hub-badge-sudeste { background: linear-gradient(135deg, #7c3aed, #6d28d9); }
        .hub-badge-norte { background: linear-gradient(135deg, #059669, #047857); }
        .hub-badge-centro { background: linear-gradient(135deg, #e11d48, #be123c); }

        .hub-card-title-group {
            flex: 1;
            padding-right: 85px;
        }

        .hub-card-title-group h3 {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 4px;
            line-height: 1.25;
        }

        .hub-card-jurisdicao {
            font-size: 0.82rem;
            color: #94a3b8;
            line-height: 1.4;
        }

        .hub-card-meta-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 18px;
        }

        .hub-meta-tag {
            font-size: 0.72rem;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.06);
            color: #cbd5e1;
        }

        .hub-meta-tag.banca {
            color: #38bdf8;
            border-color: rgba(56, 189, 248, 0.25);
            background: rgba(56, 189, 248, 0.08);
        }

        .hub-progress-section {
            margin-bottom: 20px;
        }

        .hub-progress-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.78rem;
            color: #94a3b8;
            margin-bottom: 6px;
        }

        .hub-progress-track {
            height: 6px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 999px;
            overflow: hidden;
        }

        .hub-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #2563eb);
            border-radius: 999px;
            transition: width 0.4s ease;
        }

        .hub-card-actions {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: auto;
        }

        .hub-btn-estudar {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff;
            border: none;
            padding: 10px 16px;
            border-radius: 10px;
            font-size: 0.88rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: transform 0.15s ease, filter 0.15s ease;
        }

        .hub-btn-estudar:hover {
            filter: brightness(1.12);
            transform: translateY(-1px);
        }

        .hub-btn-secondary-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .hub-btn-sub {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #cbd5e1;
            padding: 7px 10px;
            border-radius: 8px;
            font-size: 0.76rem;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            transition: background 0.15s, border-color 0.15s;
        }

        .hub-btn-sub:hover {
            background: rgba(51, 65, 85, 0.8);
            border-color: rgba(255, 255, 255, 0.18);
            color: #ffffff;
        }

        @media (max-width: 768px) {
            #view-hub { padding: 14px 12px 40px; }
            .hub-hero { padding: 22px 18px; margin-bottom: 18px; }
            .hub-hero h1 { font-size: 1.55rem; }
            .hub-hero p { font-size: 0.88rem; margin-bottom: 20px; }
            .hub-grid { grid-template-columns: 1fr; gap: 14px; }
            .hub-filter-bar { flex-direction: column; align-items: stretch; }
            .hub-search-box { max-width: 100%; min-width: auto; }
        }
"""

HUB_HTML_VIEW = """
        <!-- ==========================================================================
             VISÃO 0: MASTER HUB DE TRTS (CATÁLOGO CENTRAL)
             ========================================================================== -->
        <div id="view-hub" class="view-content" style="display: block;">
            <div class="hub-hero">
                <div class="hub-hero-badge">🏛️ Portal Central de Estudos • Tribunais Regionais do Trabalho</div>
                <h1>CADERNO DO TRT — Hub Nacional de Estudos</h1>
                <p>
                    Plataforma unificada de alto desempenho com 177 metas por ciclo, cadernos teóricos completos (núcleo comum CLT, Processo e Constitucional + Legislação Específica) e editais verticalizados para os cargos de TJAA e AJAJ de todos os TRTs do Brasil.
                </p>

                <div class="hub-stats-grid">
                    <div class="hub-stat-card">
                        <div class="hub-stat-icon">🏛️</div>
                        <div>
                            <div class="hub-stat-number" id="hub-stat-total-trts">8</div>
                            <div class="hub-stat-label">Tribunais Mapeados</div>
                        </div>
                    </div>
                    <div class="hub-stat-card">
                        <div class="hub-stat-icon">📊</div>
                        <div>
                            <div class="hub-stat-number" id="hub-stat-metas-total">177</div>
                            <div class="hub-stat-label">Metas por Ciclo</div>
                        </div>
                    </div>
                    <div class="hub-stat-card">
                        <div class="hub-stat-icon">📚</div>
                        <div>
                            <div class="hub-stat-number">10</div>
                            <div class="hub-stat-label">Cadernos Teóricos</div>
                        </div>
                    </div>
                    <div class="hub-stat-card">
                        <div class="hub-stat-icon">⚡</div>
                        <div>
                            <div class="hub-stat-number">100%</div>
                            <div class="hub-stat-label">PWA / Offline & GitHub</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- BARRA DE FILTROS E BUSCA -->
            <div class="hub-filter-bar">
                <div class="hub-filter-pills">
                    <button class="hub-pill-btn active" onclick="filtrarHubTRTs('todos', this)">🌐 Todos os TRTs</button>
                    <button class="hub-pill-btn" onclick="filtrarHubTRTs('sul', this)">🏔️ Sul (RS, SC)</button>
                    <button class="hub-pill-btn" onclick="filtrarHubTRTs('nordeste', this)">☀️ Nordeste (BA, PE, CE)</button>
                    <button class="hub-pill-btn" onclick="filtrarHubTRTs('sudeste', this)">🏙️ Sudeste (SP)</button>
                    <button class="hub-pill-btn" onclick="filtrarHubTRTs('norte', this)">🌳 Norte (PA/AP)</button>
                </div>

                <div class="hub-search-box">
                    <span class="hub-search-icon">🔍</span>
                    <input type="text" id="hub-search-input" class="hub-search-input" placeholder="Buscar por número, estado, UF ou banca..." oninput="filtrarHubBusca(this.value)">
                </div>
            </div>

            <!-- GRID DOS CARDS DE TRTS -->
            <div class="hub-grid" id="hub-trts-grid">
                <!-- Preenchido dinamicamente via renderizarHubTRTs() -->
            </div>
        </div>
"""

HUB_JS = """
        // ==========================================================================
        // SCRIPT DO MASTER HUB DE TRTS
        // ==========================================================================
        var filtroRegiaoAtual = 'todos';
        var termoBuscaHub = '';

        function abrirVisaoHub() {
            const hubEl = document.getElementById('view-hub');
            if (hubEl) hubEl.style.display = 'block';
            const quadroEl = document.getElementById('view-quadro');
            if (quadroEl) quadroEl.style.display = 'none';
            const estudoEl = document.getElementById('view-estudo');
            if (estudoEl) estudoEl.style.display = 'none';
            const discEl = document.getElementById('view-disciplinas');
            if (discEl) discEl.style.display = 'none';
            const diagEl = document.getElementById('view-diagnostico');
            if (diagEl) diagEl.style.display = 'none';
            const editalEl = document.getElementById('view-meu-edital');
            if (editalEl) editalEl.style.display = 'none';
            ativarAbaBotao('tab-btn-hub');
            renderizarHubTRTs();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function estudarTRT(trtId) {
            selecionarTribunal(trtId);
            abrirVisaoQuadro();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function filtrarHubTRTs(regiao, btn) {
            filtroRegiaoAtual = regiao;
            document.querySelectorAll('.hub-pill-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderizarHubTRTs();
        }

        function filtrarHubBusca(valor) {
            termoBuscaHub = (valor || '').toLowerCase().trim();
            renderizarHubTRTs();
        }

        function renderizarHubTRTs() {
            const grid = document.getElementById('hub-trts-grid');
            if (!grid) return;

            const lista = obterListaTRTs();
            const totalTRTsEl = document.getElementById('hub-stat-total-trts');
            if (totalTRTsEl) totalTRTsEl.textContent = lista.length;

            const trtsFiltrados = lista.filter(trt => {
                // Filtro macro região
                if (filtroRegiaoAtual !== 'todos') {
                    if ((trt.regiao_macro || '').toLowerCase() !== filtroRegiaoAtual) return false;
                }
                // Filtro busca
                if (termoBuscaHub) {
                    const texto = `${trt.sigla} ${trt.regiao} ${trt.uf} ${trt.banca || ''} ${trt.numero || ''}`.toLowerCase();
                    if (!texto.includes(termoBuscaHub)) return false;
                }
                return true;
            });

            if (trtsFiltrados.length === 0) {
                grid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; background: rgba(15, 23, 42, 0.4); border-radius: 16px; border: 1px dashed rgba(255,255,255,0.1);">
                        <div style="font-size: 2.2rem; margin-bottom: 12px;">🔍</div>
                        <h4 style="font-size: 1.1rem; color: #f1f5f9; margin-bottom: 6px;">Nenhum Tribunal encontrado</h4>
                        <p style="color: #94a3b8; font-size: 0.88rem;">Tente ajustar o termo de busca ou selecione outro filtro regional.</p>
                    </div>
                `;
                return;
            }

            const badgesRegiao = {
                'sul': 'hub-badge-sul',
                'nordeste': 'hub-badge-nordeste',
                'sudeste': 'hub-badge-sudeste',
                'norte': 'hub-badge-norte',
                'centro': 'hub-badge-centro'
            };

            grid.innerHTML = trtsFiltrados.map(trt => {
                const isActive = trt.id === trtAtivoId;
                const regClass = badgesRegiao[trt.regiao_macro || 'sul'] || 'hub-badge-sul';
                const totalMetas = trt.metas_qtd || 177;

                // Obter progresso salvo
                let concluidas = 0;
                try {
                    const storageKey = isActive ? 'estudos_dl_metas_concluidas' : `estudos_dl_metas_concluidas_${trt.id}`;
                    const raw = localStorage.getItem(storageKey);
                    if (raw) {
                        const parsed = JSON.parse(raw);
                        concluidas = Array.isArray(parsed) ? parsed.length : 0;
                    } else if (isActive && typeof metasConcluidas !== 'undefined') {
                        concluidas = metasConcluidas.size;
                    }
                } catch(e) {}

                const pct = Math.min(100, Math.round((concluidas / totalMetas) * 100));
                const localUrl = trt.local_url || `./${trt.sigla}-${trt.uf.split(' ')[0]}/Plataforma/index.html`;
                const githubUrl = trt.url || `https://github.com/daniellucas2025/caderno-do-trt/tree/main/${trt.sigla}-${trt.uf.split(' ')[0]}`;

                return `
                    <div class="hub-card ${isActive ? 'is-active-trt' : ''}">
                        ${isActive ? '<div class="hub-card-active-tag">✓ Ativo Agora</div>' : ''}
                        
                        <div>
                            <div class="hub-card-header">
                                <div class="hub-card-badge ${regClass}">
                                    ${trt.sigla.replace('TRT-', '')}
                                </div>
                                <div class="hub-card-title-group">
                                    <h3>${trt.sigla} • ${trt.regiao}</h3>
                                    <div class="hub-card-jurisdicao">Região: ${trt.uf} • Abrangência Regional</div>
                                </div>
                            </div>

                            <div class="hub-card-meta-tags">
                                <span class="hub-meta-tag banca">Banca: ${trt.banca || 'FCC'}</span>
                                <span class="hub-meta-tag">Cargos: TJAA & AJAJ</span>
                                <span class="hub-meta-tag">177 Metas Mapeadas</span>
                                <span class="hub-meta-tag">10 Cadernos</span>
                            </div>

                            <div class="hub-progress-section">
                                <div class="hub-progress-labels">
                                    <span>Progresso do Ciclo</span>
                                    <span><strong>${concluidas}</strong> de ${totalMetas} (${pct}%)</span>
                                </div>
                                <div class="hub-progress-track">
                                    <div class="hub-progress-bar" style="width: ${pct}%;"></div>
                                </div>
                            </div>
                        </div>

                        <div class="hub-card-actions">
                            <button type="button" class="hub-btn-estudar" onclick="estudarTRT('${trt.id}')">
                                🎯 Estudar este TRT ➔
                            </button>
                            <div class="hub-btn-secondary-row">
                                <a href="${localUrl}" class="hub-btn-sub" title="Abrir plataforma isolada deste tribunal">
                                    📱 Plataforma
                                </a>
                                <a href="${githubUrl}" target="_blank" rel="noopener noreferrer" class="hub-btn-sub" title="Ver arquivos e cadernos no GitHub">
                                    📂 GitHub ↗
                                </a>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
"""

def gerar_master_portal():
    print(f"[*] Lendo template de base em: {TRT4_INDEX}")
    if not TRT4_INDEX.exists():
        raise FileNotFoundError(f"Arquivo {TRT4_INDEX} não encontrado.")

    html = TRT4_INDEX.read_text(encoding="utf-8")

    # 1. Ajustar Título e Meta Tags
    html = re.sub(
        r"<title>.*?</title>",
        "<title>CADERNO DO TRT • Portal Hub & Plataforma de Estudos Unificada</title>",
        html
    )

    # 2. Inserir Estilos do Master Hub antes do fechamento de </style>
    if "/* ESTILOS DO MASTER HUB" not in html:
        html = html.replace("</style>", f"{HUB_CSS}\n</style>")

    # 3. Adicionar botão da aba Hub de TRTs no topbar-tabs
    antigo_tab_btn = '<button class="topbar-tab-btn active" id="tab-btn-quadro"'
    if antigo_tab_btn in html:
        novo_tab_btn = '<button class="topbar-tab-btn active" id="tab-btn-hub" onclick="abrirVisaoHub()">🏛️ Hub <span class="hide-mobile">de TRTs</span></button>\n                <button class="topbar-tab-btn" id="tab-btn-quadro"'
        html = html.replace(antigo_tab_btn, novo_tab_btn)

    # 4. Inserir container view-hub antes do view-quadro
    if '<div id="view-hub"' not in html:
        alvo = '<section class="quadro-section" id="view-quadro">'
        if alvo in html:
            html = html.replace(
                alvo,
                f"{HUB_HTML_VIEW}\n        <section class=\"quadro-section\" id=\"view-quadro\" style=\"display: none;\">"
            )
        else:
            html = re.sub(
                r'(<section[^>]*id=["\']view-quadro["\'][^>]*>)',
                f"{HUB_HTML_VIEW}\n        \\1",
                html
            )

    # 5. Expandir TRTS_PREDEFINIDOS com todos os 8 tribunais e metadados de região e URLs
    antiga_lista_trts = re.search(r"const TRTS_PREDEFINIDOS = \[.*?\];", html, re.DOTALL)
    if antiga_lista_trts:
        nova_lista_trts = """const TRTS_PREDEFINIDOS = [
            {
                id: "trt-4",
                numero: "04",
                sigla: "TRT-4",
                uf: "RS",
                regiao: "Rio Grande do Sul",
                regiao_macro: "sul",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-04-RS/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-04-RS"
            },
            {
                id: "trt-5",
                numero: "05",
                sigla: "TRT-5",
                uf: "BA",
                regiao: "Bahia",
                regiao_macro: "nordeste",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-05-BA/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-05-BA"
            },
            {
                id: "trt-6",
                numero: "06",
                sigla: "TRT-6",
                uf: "PE",
                regiao: "Pernambuco",
                regiao_macro: "nordeste",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-06-PE/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-06-PE"
            },
            {
                id: "trt-7",
                numero: "07",
                sigla: "TRT-7",
                uf: "CE",
                regiao: "Ceará",
                regiao_macro: "nordeste",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-07-CE/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-07-CE"
            },
            {
                id: "trt-8",
                numero: "08",
                sigla: "TRT-8",
                uf: "PA/AP",
                regiao: "Pará e Amapá",
                regiao_macro: "norte",
                banca: "Cebraspe",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-08-PA/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-08-PA"
            },
            {
                id: "trt-12",
                numero: "12",
                sigla: "TRT-12",
                uf: "SC",
                regiao: "Santa Catarina",
                regiao_macro: "sul",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-12-SC/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-12-SC"
            },
            {
                id: "trt-15",
                numero: "15",
                sigla: "TRT-15",
                uf: "SP Interior",
                regiao: "Campinas",
                regiao_macro: "sudeste",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-15-SP/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-15-SP"
            },
            {
                id: "trt-2",
                numero: "02",
                sigla: "TRT-2",
                uf: "SP Capital",
                regiao: "São Paulo e Litoral",
                regiao_macro: "sudeste",
                banca: "FCC",
                status: "Disponível",
                metas_qtd: 177,
                materias_qtd: 10,
                local_url: "./TRT-02-SP/Plataforma/index.html",
                url: "https://github.com/daniellucas2025/caderno-do-trt/tree/main/TRT-02-SP"
            }
        ];"""
        html = html.replace(antiga_lista_trts.group(0), nova_lista_trts)

    # 6. Atualizar as funções abrirVisao... para esconder view-hub
    visoes_alvo = [
        "abrirVisaoQuadro() {",
        "abrirVisaoEstudo() {",
        "abrirVisaoDisciplinas() {",
        "abrirVisaoDiagnostico() {",
        "abrirVisaoEdital() {"
    ]
    for visao in visoes_alvo:
        html = html.replace(
            visao,
            f"{visao}\n            const hubEl = document.getElementById('view-hub'); if (hubEl) hubEl.style.display = 'none';"
        )

    # 7. Inserir scripts do Hub ANTES da inicialização e configurar inicialização
    if "function renderizarHubTRTs" not in html:
        init_orig = "inicializarFirebase();\n        verificarHashMeta();"
        if init_orig in html:
            html = html.replace(
                init_orig,
                f"{HUB_JS}\n\n        {init_orig}"
            )
        else:
            html = html.replace(
                "</script>\n</body>",
                f"{HUB_JS}\n    </script>\n</body>"
            )

        html = html.replace(
            "renderizarListaTRTsSidebar();",
            "renderizarListaTRTsSidebar();\n        renderizarHubTRTs();"
        )
        html = html.replace(
            "aplicarTribunalAtivo();",
            "aplicarTribunalAtivo();\n        if (!window.location.hash.includes('meta=')) { abrirVisaoHub(); }"
        )

    # 8. Escrever arquivo final index.html na raiz
    OUTPUT_INDEX.write_text(html, encoding="utf-8")
    print(f"✅ Master Portal Hub index.html gerado com sucesso!")
    print(f"   Destino: {OUTPUT_INDEX} ({OUTPUT_INDEX.stat().st_size:,} bytes)")

if __name__ == "__main__":
    gerar_master_portal()
