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
│   ├── 📄 Documentos-Oficiais/  # Planilhas de controle e Guias de estudo oficiais em PDF
│   └── ⚙️ Scripts-Geradores/    # Automação em Python e .BAT para compilação da plataforma
│
└── 📁 OUTROS-TRTS/               # Modelo e diretrizes para adicionar novos tribunais (TRT-5, TRT-6, TRT-8, etc.)
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

## 🤝 Adicionar Novos Tribunais

Para adicionar um novo tribunal a este repositório, consulte o guia na pasta [`OUTROS-TRTS/README.md`](OUTROS-TRTS/README.md).
