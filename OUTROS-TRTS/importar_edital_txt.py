# -*- coding: utf-8 -*-
"""
Conversor Inteligente de Edital em Texto para JSON Mapeado (editais_mapped.json)
Uso:
    python importar_edital_txt.py --cargo TJAA --arquivo edital_tjaa.txt --saida editais_mapped.json
"""

import re
import json
import argparse
from pathlib import Path

SIGLAS_DISCIPLINAS = {
    "PORTUGUÊS": "PORT",
    "PORTUGUES": "PORT",
    "LÍNGUA PORTUGUESA": "PORT",
    "LINGUA PORTUGUESA": "PORT",
    "MATEMÁTICA E RACIOCÍNIO LÓGICO": "RLM",
    "RACIOCÍNIO LÓGICO-MATEMÁTICO": "RLM",
    "RACIOCÍNIO LÓGICO E MATEMÁTICO": "RLM",
    "RLM": "RLM",
    "DIREITO CONSTITUCIONAL": "DC",
    "NOÇÕES DE DIREITO CONSTITUCIONAL": "DC",
    "DIREITO ADMINISTRATIVO": "DA",
    "NOÇÕES DE DIREITO ADMINISTRATIVO": "DA",
    "DIREITO DO TRABALHO": "DT",
    "NOÇÕES DE DIREITO DO TRABALHO": "DT",
    "DIREITO PROCESSUAL DO TRABALHO": "DPT",
    "NOÇÕES DE DIREITO PROCESSUAL DO TRABALHO": "DPT",
    "INFORMÁTICA": "INFO",
    "NOÇÕES DE INFORMÁTICA": "INFO",
    "DIREITOS HUMANOS": "DH",
    "ADMINISTRAÇÃO PÚBLICA": "ADM",
    "NOÇÕES DE ADMINISTRAÇÃO PÚBLICA": "ADM",
    "GESTÃO PÚBLICA": "ADM",
    "LEGISLAÇÃO ESPECÍFICA": "LEG",
    "REGIMENTO INTERNO": "LEG"
}

def identificar_disciplina(linha):
    limpo = re.sub(r'^[#*\-•\d\.\s]+', '', linha).strip().upper()
    for nome, sigla in SIGLAS_DISCIPLINAS.items():
        if limpo == nome or limpo.startswith(nome + ":") or limpo.startswith(nome + " -"):
            return sigla, nome
    return None, None

def processar_texto_edital(conteudo_txt, cargo_tipo="TJAA"):
    linhas = conteudo_txt.splitlines()
    disciplinas = []
    disc_atual = None

    for raw_linha in linhas:
        linha = raw_linha.strip()
        if not linha:
            continue

        sigla_detectada, nome_detectado = identificar_disciplina(linha)
        if sigla_detectada:
            disc_atual = {
                "sigla": sigla_detectada,
                "nome": nome_detectado,
                "topicos": []
            }
            disciplinas.append(disc_atual)
            continue

        if disc_atual is None:
            disc_atual = {
                "sigla": "GERAL",
                "nome": "CONHECIMENTOS GERAIS",
                "topicos": []
            }
            disciplinas.append(disc_atual)

        # Limpar prefixo numerado como "1.", "1 -", "1.1."
        topico_limpo = re.sub(r'^\d+(\.\d+)*[\.\-\)]\s*', '', linha).strip()
        if not topico_limpo:
            continue

        idx = len(disc_atual["topicos"]) + 1
        sigla_lower = disc_atual["sigla"].lower()
        cargo_lower = cargo_tipo.lower()

        topico_obj = {
            "id": f"{sigla_lower}-{cargo_lower}-topico-{idx}",
            "topico": topico_limpo,
            "metas_texto": str(idx),
            "metas_numeros": [idx],
            "meta_ids": [f"{sigla_lower}-meta-{idx}"]
        }
        disc_atual["topicos"].append(topico_obj)

    # Filtrar disciplinas vazias
    disciplinas = [d for d in disciplinas if len(d["topicos"]) > 0]
    total_topicos = sum(len(d["topicos"]) for d in disciplinas)

    cargo_nome = "Técnico Judiciário - Área Administrativa (TJAA)" if cargo_tipo.upper() == "TJAA" else "Analista Judiciário - Área Judiciária (AJAJ)"

    return {
        "cargo": cargo_nome,
        "sigla_cargo": cargo_tipo.upper(),
        "disciplinas": disciplinas,
        "total_topicos": total_topicos
    }

def main():
    parser = argparse.ArgumentParser(description="Importador de Edital TXT para JSON de Metas")
    parser.add_argument("--arquivo", "-a", required=True, help="Caminho do arquivo .txt com os tópicos do edital")
    parser.add_argument("--cargo", "-c", default="TJAA", choices=["TJAA", "AJAJ"], help="Cargo correspondente (TJAA ou AJAJ)")
    parser.add_argument("--saida", "-s", default="editais_mapped.json", help="Arquivo JSON de saída")

    args = parser.parse_args()
    caminho_txt = Path(args.arquivo)

    if not caminho_txt.exists():
        print(f"❌ Erro: Arquivo {caminho_txt} não encontrado!")
        return

    texto = caminho_txt.read_text(encoding="utf-8", errors="ignore")
    dados_cargo = processar_texto_edital(texto, args.cargo)

    saida_path = Path(args.saida)
    dados_completos = {}
    if saida_path.exists():
        try:
            with open(saida_path, "r", encoding="utf-8") as f:
                dados_completos = json.load(f)
        except Exception:
            dados_completos = {}

    chave = args.cargo.lower()
    dados_completos[chave] = dados_cargo

    with open(saida_path, "w", encoding="utf-8") as f:
        json.dump(dados_completos, f, ensure_ascii=False, indent=2)

    print(f"✅ Edital para {args.cargo} importado com sucesso!")
    print(f"   Disciplinas processadas: {len(dados_cargo['disciplinas'])}")
    print(f"   Total de tópicos mapeados: {dados_cargo['total_topicos']}")
    print(f"   Salvo em: {saida_path.resolve()}")

if __name__ == "__main__":
    main()

