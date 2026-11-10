# 🏛️ CADERNO DO TRT

> Repositório Central de Estudos, Metas, Editais e Cadernos Teóricos para os Tribunais Regionais do Trabalho (TRTs).
> Baseado na metodologia de alto desempenho do **Caderno do Aprovado**.

---

## 📂 Estrutura do Repositório Organizada por Tribunal

Este repositório foi projetado com uma arquitetura modular por Tribunal. Cada concurso de TRT possui sua própria pasta independente com seus materiais, plataforma interativa e mapeamento de edital:

```
caderno-do-trt/
│
├── 📁 TRT-04-RS/                 # Tribunal Regional do Trabalho da 4ª Região (Rio Grande do Sul)
│   ├── 📱 Plataforma/           # Aplicação Web PWA 100% offline com Quadro de Metas e Dashboard
│   ├── 📚 Cadernos-Completos/   # 10 Cadernos teóricos unificados em HTML por matéria
│   ├── 📑 Mapeamento-Edital/    # Mapeamento 100% correlacionado dos tópicos de TJAA e AJAJ com as metas
│   ├── 🔒 Documentos-Oficiais/  # Diretório seguro (protegido contra PDFs com CPF por LGPD)
│   └── ⚙️ Scripts-Geradores/    # Automação em Python e .BAT para compilação da plataforma
│
├── 📁 OUTROS-TRTS/               # Modelos, conversores de edital e diretrizes para novos tribunais
├── ⚡ NOVO_TRT.bat               # Assistente 1-clique para criar qualquer novo TRT
└── 🐍 gerar_novo_trt.py          # Gerador modular automatizado via CLI
```

---

## 🏛️ Tribunais Disponíveis

| Tribunal | Região | Banca | Status | Metas / Tópicos | Plataforma Online |
|:---|:---:|:---:|:---:|:---:|:---:|
| **TRT-04** | Rio Grande do Sul | FCC | ✅ Concluído (100%) | 177 Metas (10 Matérias) • TJAA & AJAJ | [Acessar Plataforma](https://daniellucas2025.github.io/metas-trt4/) |
| **TRT-05** | Bahia | FCC | ⏳ Em Planejamento | — | — |
| **TRT-06** | Pernambuco | FCC | ⏳ Em Planejamento | — | — |
| **TRT-08** | Pará / Amapá | Cebraspe | ⏳ Em Planejamento | — | — |

---

## 🚀 Como Executar a Plataforma de Qualquer TRT

1. Acesse a pasta do tribunal desejado (ex: `TRT-04-RS/Plataforma`).
2. Abra o arquivo `index.html` em qualquer navegador (Chrome, Edge, Firefox, Safari).
3. **Funciona 100% offline**, sem necessidade de instalar servidores, Node.js ou dependências.
4. Possui sincronização em nuvem opcional com o Google Drive para manter o progresso compartilhado entre celular e computador.

---

## ⚡ Como Criar Qualquer Novo TRT em 1 Minuto

Adicionar um novo TRT é automatizado:

1. Dê um duplo-clique em `NOVO_TRT.bat` (ou execute `python gerar_novo_trt.py`).
2. Digite a região, o estado e a banca (ex: `05`, `BA`, `Bahia`, `FCC`).
3. O gerador cria a pasta completa `TRT-XX-UF`, herda o núcleo comum das matérias (CLT, CF, Dir. Adm, etc.), gera os cadernos, assets PWA e compila a plataforma imediatamente!

Para detalhes avançados e mapeamento de editais em texto, consulte o guia na pasta [`OUTROS-TRTS/README.md`](OUTROS-TRTS/README.md).

---

## 🔒 Proteção de Dados e Privacidade (LGPD)

> **AVISO IMPORTANTE:** Arquivos `.pdf` de plataformas terceiras não são incluídos no repositório por conterem marcas d'água com CPF e dados pessoais.
> O arquivo `.gitignore` bloqueia permanentemente `*.pdf` para proteger a sua privacidade.
