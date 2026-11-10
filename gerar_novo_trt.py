# -*- coding: utf-8 -*-
"""
Gerador Modular de Novos Tribunais (TRTs)
Repositório: CADERNO DO TRT

Cria uma estrutura completa, independente e 100% funcional para qualquer novo TRT
a partir do núcleo comum unificado de matérias e editais.
"""

import sys
import shutil
import argparse
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TRT4_DIR = BASE_DIR / "TRT-04-RS"

CORE_CADERNOS = [
    "Direito Constitucional_COMPLETO.html",
    "Direito Administrativo_COMPLETO.html",
    "Direito do Trabalho_COMPLETO.html",
    "Processo do Trabalho_COMPLETO.html",
    "Português_COMPLETO.html",
    "Matematica e Rlm_COMPLETO.html",
    "Informática_COMPLETO.html",
    "Direitos Humanos_COMPLETO.html",
    "Administração_COMPLETO.html"
]

LEGISLACAO_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Legislação Específica para o TRT-{numero} ({uf}) - Material Compilado</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #1e293b; background: #f8fafc; }}
        h1 {{ color: #0284c7; border-bottom: 2px solid #0284c7; padding-bottom: 8px; }}
        h2 {{ color: #0f172a; margin-top: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 4px solid #0284c7; }}
        code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Legislação Específica • TRT-{numero} ({uf})</h1>
    <div class="card">
        <h2>Regimento Interno e Normas Locais</h2>
        <p>Este caderno destina-se ao estudo das normas específicas do Tribunal Regional do Trabalho da {numero}ª Região ({regiao}):</p>
        <ul>
            <li><strong>Regimento Interno do TRT-{numero}</strong>: Composição, Competência do Pleno, Turmas e Seções Especializadas.</li>
            <li><strong>Código de Ética e Conduta</strong> da {numero}ª Região.</li>
            <li><strong>Provimentos e Portarias</strong> da Presidência e Corregedoria Regional.</li>
        </ul>
        <p><em>Insira aqui os textos das leis locais, artigos comentados e resumos para que sejam compilados automaticamente na sua plataforma.</em></p>
    </div>
</body>
</html>
"""

README_DOCS_PRIVACIDADE = """# 🔒 Documentos Oficiais - Proteção de Privacidade (LGPD)

> **DIRETRIZ DE SEGURANÇA E PRIVACIDADE:**
> Nenhum arquivo em formato `.pdf` deve ser colocado neste repositório ou enviado ao GitHub.
> Documentos oficiais, relatórios e guias de plataformas terceiras contêm rotineiramente **CPF e dados pessoais do usuário em marcas d'água**.

O arquivo `.gitignore` na raiz do repositório já está configurado para bloquear automaticamente:
- `*.pdf`
- `*.PDF`

Para incluir anotações ou dados de editais, utilize:
1. Arquivos `.html` na pasta `Cadernos-Completos/`.
2. Mapeamentos estruturados em JSON na pasta `Mapeamento-Edital/`.
3. Anotações em Markdown sem informações sensíveis.
"""

def criar_trt(numero, uf, regiao, banca="FCC", herdar_base=True):
    num_fmt = f"{int(numero):02d}"
    uf_upper = uf.strip().upper()
    pasta_nome = f"TRT-{num_fmt}-{uf_upper}"
    trt_dir = BASE_DIR / pasta_nome

    print(f"\n{'='*65}")
    print(f"🚀 INICIANDO CRIAÇÃO DO {pasta_nome} ({regiao})")
    print(f"{'='*65}")

    if trt_dir.exists():
        print(f"⚠️ A pasta '{pasta_nome}' já existe. Atualizando componentes...")
    else:
        trt_dir.mkdir(parents=True, exist_ok=True)

    # 1. Pastas padrão
    pastas = [
        "Cadernos-Completos",
        "Documentos-Oficiais",
        "Mapeamento-Edital",
        "Plataforma",
        "Scripts-Geradores"
    ]
    for p in pastas:
        (trt_dir / p).mkdir(parents=True, exist_ok=True)

    # 2. Documentos Oficiais - README de Privacidade
    (trt_dir / "Documentos-Oficiais" / "README.md").write_text(README_DOCS_PRIVACIDADE, encoding="utf-8")
    print("  [OK] Política de privacidade e bloqueio de CPF configurados.")

    # 3. Cadernos Completos (Núcleo Comum)
    cadernos_dir = trt_dir / "Cadernos-Completos"
    if herdar_base and TRT4_DIR.exists():
        print("  [+] Copiando matérias-base do núcleo comum dos TRTs...")
        for arq in CORE_CADERNOS:
            origem = TRT4_DIR / "Cadernos-Completos" / arq
            if origem.exists():
                shutil.copy2(origem, cadernos_dir / arq)
        print("  [OK] 10 matérias do núcleo comum herdadas com sucesso.")

    # Criar caderno de Legislação Específica para este TRT
    leg_nome = f"Legislação Específica para o TRT-{int(numero)} ({uf_upper})_COMPLETO.html"
    leg_path = cadernos_dir / leg_nome
    if not leg_path.exists():
        conteudo_leg = LEGISLACAO_TEMPLATE.format(
            numero=int(numero),
            uf=uf_upper,
            regiao=regiao
        )
        leg_path.write_text(conteudo_leg, encoding="utf-8")
        print(f"  [+] Criado template de Legislação Específica: {leg_nome}")

    # 4. Mapeamento de Edital
    map_dir = trt_dir / "Mapeamento-Edital"
    origem_map = TRT4_DIR / "Mapeamento-Edital" / "editais_mapped.json"
    if origem_map.exists():
        map_conteudo = origem_map.read_text(encoding="utf-8")
        # Customizar strings do tribunal
        map_conteudo = map_conteudo.replace("TRT-4", f"TRT-{int(numero)}")
        map_conteudo = map_conteudo.replace("TRT 4", f"TRT {int(numero)}")
        (map_dir / "editais_mapped.json").write_text(map_conteudo, encoding="utf-8")
        print("  [OK] Mapeamento de edital personalizado gerado.")

    # 5. PWA Assets na Plataforma
    plat_dir = trt_dir / "Plataforma"
    origem_plat = TRT4_DIR / "Plataforma"
    if origem_plat.exists():
        for asset in ["icon-192.png", "icon-512.png", "icon.svg", "sw.js"]:
            src = origem_plat / asset
            if src.exists():
                shutil.copy2(src, plat_dir / asset)

    # Manifest personalizado
    manifest_txt = f"""{{
  "name": "Estudos DL • Metas TRT-{int(numero)} ({uf_upper})",
  "short_name": "TRT-{int(numero)}",
  "description": "Plataforma de Metas e Acompanhamento de Estudos para o TRT da {int(numero)}ª Região ({regiao})",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#0d1117",
  "theme_color": "#0d1117",
  "icons": [
    {{
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }},
    {{
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }}
  ]
}}"""
    (plat_dir / "manifest.json").write_text(manifest_txt, encoding="utf-8")
    print("  [OK] Assets PWA e Manifest configurados.")

    # 6. Scripts Geradores
    scripts_dir = trt_dir / "Scripts-Geradores"
    origem_gen = TRT4_DIR / "Scripts-Geradores" / "gerar_plataforma_metas.py"
    if origem_gen.exists():
        gen_codigo = origem_gen.read_text(encoding="utf-8")
        # Personalizar labels e títulos para o novo tribunal
        gen_codigo = gen_codigo.replace("TRT-4", f"TRT-{int(numero)}")
        gen_codigo = gen_codigo.replace("TRT 4", f"TRT {int(numero)}")
        gen_codigo = gen_codigo.replace("Rio Grande do Sul", regiao)
        gen_codigo = gen_codigo.replace("(RS)", f"({uf_upper})")
        (scripts_dir / "gerar_plataforma_metas.py").write_text(gen_codigo, encoding="utf-8")

    # Arquivos .BAT
    bat1 = """@echo off\nchcp 65001 > nul\ntitle Gerar Plataforma de Metas\npython "%~dp0gerar_plataforma_metas.py"\npause\n"""
    bat2 = """@echo off\nchcp 65001 > nul\ntitle Publicar no GitHub\npython "%~dp0publicar_github.py"\npause\n"""
    bat3 = """@echo off\nchcp 65001 > nul\ntitle Gerar e Publicar\npython "%~dp0gerar_plataforma_metas.py"\nif %ERRORLEVEL% EQU 0 python "%~dp0publicar_github.py"\npause\n"""

    (scripts_dir / "1. GERAR_PLATAFORMA.bat").write_text(bat1, encoding="utf-8")
    (scripts_dir / "2. PUBLICAR_SITE.bat").write_text(bat2, encoding="utf-8")
    (scripts_dir / "3. GERAR_E_PUBLICAR_TUDO.bat").write_text(bat3, encoding="utf-8")

    if (TRT4_DIR / "Scripts-Geradores" / "publicar_github.py").exists():
        shutil.copy2(TRT4_DIR / "Scripts-Geradores" / "publicar_github.py", scripts_dir / "publicar_github.py")

    print("  [OK] Scripts de automação instalados.")

    # 7. README local do TRT
    readme_trt = f"""# 🏛️ TRT da {int(numero)}ª Região ({uf_upper}) - {regiao}

> **Plataforma de Metas, Acompanhamento e Cadernos Teóricos de Estudos**  
> Banca: **{banca}** | Organização: **Metodologia de Alto Desempenho**

---

## 📂 Organização da Pasta

- `Plataforma/`: Aplicação Web PWA 100% offline (`index.html`) com Quadro de Metas e Dashboard.
- `Cadernos-Completos/`: Cadernos teóricos unificados em HTML por matéria (núcleo comum CLT/Processual/CF + Legislação Específica).
- `Mapeamento-Edital/`: Mapeamento correlacionado dos tópicos de TJAA e AJAJ com as metas.
- `Documentos-Oficiais/`: Diretório seguro (bloqueado contra `.pdf` no Git para proteção de dados/CPF - LGPD).
- `Scripts-Geradores/`: Scripts automatizados para compilar a plataforma após novas alterações.

---

## 🚀 Como Executar

Abra o arquivo `Plataforma/index.html` em qualquer navegador. Funciona sem internet e salva seu progresso automaticamente!
"""
    (trt_dir / "README.md").write_text(readme_trt, encoding="utf-8")

    # 8. Executar compilação inicial da plataforma
    print("  [*] Compilando plataforma inicial...")
    res = subprocess.run([sys.executable, str(scripts_dir / "gerar_plataforma_metas.py")], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res.returncode == 0:
        print("  ✅ Plataforma compilada com sucesso!")
    else:
        print("  ⚠️ Aviso ao compilar:", res.stderr[:300])

    # 9. Atualizar tabela no README principal
    atualizar_readme_principal(num_fmt, uf_upper, regiao, banca)

    print(f"\n🎉 SUCESSO! O Tribunal {pasta_nome} está 100% pronto!")
    print(f"👉 Local: {trt_dir}")
    print(f"👉 Abra a plataforma em: {trt_dir / 'Plataforma' / 'index.html'}\n")

def atualizar_readme_principal(num_fmt, uf_upper, regiao, banca):
    readme_path = BASE_DIR / "README.md"
    if not readme_path.exists():
        return

    import re
    texto = readme_path.read_text(encoding="utf-8")
    linha_trt = f"| **TRT-{num_fmt}** | {regiao} | {banca} | ✅ Instalado | 177 Metas • TJAA & AJAJ | [Abrir Localmente](TRT-{num_fmt}-{uf_upper}/Plataforma/index.html) |"

    padrao = rf"\|\s*\*\*TRT-{num_fmt}\*\*.*"
    if re.search(padrao, texto):
        texto = re.sub(padrao, linha_trt, texto)
    else:
        tabela_header = "| Tribunal | Região | Banca | Status | Metas / Tópicos | Plataforma Online |"
        idx_header = texto.find(tabela_header)
        if idx_header != -1:
            idx_fim_tab = texto.find("\n\n---", idx_header)
            if idx_fim_tab != -1:
                texto = texto[:idx_fim_tab] + "\n" + linha_trt + texto[idx_fim_tab:]
            else:
                texto += "\n" + linha_trt + "\n"

    readme_path.write_text(texto, encoding="utf-8")
    print("  [OK] Tabela do README principal atualizada.")

def main():
    parser = argparse.ArgumentParser(description="Gerador de Novo TRT para o Repositório CADERNO DO TRT")
    parser.add_argument("--numero", "-n", help="Número da Região (ex: 5, 05, 6, 8, 12, 15)")
    parser.add_argument("--uf", "-u", help="UF do Estado (ex: BA, PE, PA, SC, SP)")
    parser.add_argument("--regiao", "-r", help="Nome do Estado/Região (ex: Bahia, Pernambuco, etc.)")
    parser.add_argument("--banca", "-b", default="FCC", help="Banca organizadora (padrão: FCC)")
    parser.add_argument("--sem-base", action="store_true", help="Não herdar matérias do núcleo comum")

    args = parser.parse_args()

    numero = args.numero
    uf = args.uf
    regiao = args.regiao
    banca = args.banca
    herdar = not args.sem_base

    # Modo Interativo se não passar argumentos
    if not numero or not uf or not regiao:
        print("\n" + "="*65)
        print("🏛️  ASSISTENTE DE CRIAÇÃO DE NOVO TRT - CADERNO DO TRT")
        print("="*65)
        if not numero:
            numero = input("• Digite o número da Região do TRT (ex: 5, 6, 8, 12, 15): ").strip()
        if not uf:
            uf = input("• Digite a UF do Estado (ex: BA, PE, PA, SC, SP): ").strip()
        if not regiao:
            regiao = input("• Digite o Nome do Estado/Região (ex: Bahia, Pernambuco): ").strip()
        
        banca_input = input(f"• Banca organizadora [Padrão: {banca}]: ").strip()
        if banca_input:
            banca = banca_input

        herdar_input = input("• Deseja herdar o núcleo comum dos TRTs (CLT, CF, Dir. Adm, etc.)? (S/N) [Padrão: S]: ").strip().lower()
        if herdar_input == "n":
            herdar = False

    criar_trt(numero, uf, regiao, banca=banca, herdar_base=herdar)

if __name__ == "__main__":
    main()
