# 🏛️ Guia de Implementação e Arquitetura para Outros TRTs

Este diretório contém os modelos, ferramentas e diretrizes arquiteturais para adicionar qualquer novo Tribunal Regional do Trabalho ao ecossistema do repositório **CADERNO DO TRT**.

---

## 🎯 Arquitetura: O "Núcleo Comum" dos TRTs

Concursos de Tribunais Regionais do Trabalho (TRTs) compartilham uma base programática de aproximadamente **85% a 90% idêntica**:
- **Direito do Trabalho**: CLT, Súmulas e OJs do TST, Legislação Trabalhista Extravagante.
- **Direito Processual do Trabalho**: Procedimentos, Prazos, Execução, Recursos, PJe.
- **Direito Constitucional**: Direitos e Deveres Individuais, Organização do Estado e do Judiciário.
- **Direito Administrativo**: Regime Jurídico Único (Lei 8.112), Atos Administrativos, Licitações.
- **Língua Portuguesa**: Gramática, Redação Oficial e Interpretação de Texto.
- **Raciocínio Lógico-Matemático (RLM)**: Lógica proposicional, frações, porcentagem, análise combinatória.
- **Noções de Informática / Direitos Humanos / Administração**: Aplicados conforme o cargo (TJAA / AJAJ).

### 🔍 O Que Muda de um TRT para Outro?
1. **Legislação Específica**: Regimento Interno do Tribunal, Código de Ética e Plano Estratégico.
2. **Peculiaridades de Banca**: Estilo FCC (literalidade e súmulas) vs Cebraspe (certo/errado e jurisprudência) vs FGV (casos práticos).
3. **Distribuição de Questões e Pesos** específicos do edital regional.

---

## ⚡ Como Criar um Novo TRT em Segundos

Você não precisa copiar pastas nem renomear dezenas de arquivos manualmente. O repositório conta com automação completa:

### Método 1: Assistente Interativo (Recomendado no Windows)
1. Dê um duplo-clique no arquivo `NOVO_TRT.bat` localizado na raiz do repositório.
2. Responda às perguntas simples do assistente:
   - Número da Região (ex: `05` para TRT-5, `06` para TRT-6, `08` para TRT-8, etc.)
   - UF do Estado (ex: `BA`, `PE`, `PA`, `SC`, etc.)
   - Nome por Extenso (ex: `Bahia`, `Pernambuco`, `Pará e Amapá`)
   - Banca Organizadora (ex: `FCC`, `Cebraspe`, `FGV`)
3. Pronto! O script criará a pasta `TRT-XX-UF`, herdará as matérias-base, configurará o PWA offline, personalizará os manifests e compilará a plataforma automaticamente!

### Método 2: Linha de Comando (CLI)
Você também pode rodar direto pelo terminal:
```bash
python gerar_novo_trt.py --numero 05 --uf BA --regiao "Bahia" --banca FCC
```

---

## 📂 Estrutura Padronizada de Cada Tribunal

Cada tribunal criado possui sua independência total:

```
caderno-do-trt/
├── TRT-04-RS/
├── TRT-05-BA/
│   ├── 📱 Plataforma/            # index.html e assets PWA (100% offline)
│   ├── 📚 Cadernos-Completos/    # HTMLs com teoria e questões das matérias
│   ├── 📑 Mapeamento-Edital/     # editais_mapped.json com os tópicos de TJAA/AJAJ
│   ├── 🔒 Documentos-Oficiais/   # Local de anotações (sem PDFs/CPFs - LGPD)
│   └── ⚙️ Scripts-Geradores/     # Scripts de compilação daquele tribunal
```

---

## 📑 Como Mapear um Novo Edital

Nesta pasta `OUTROS-TRTS/`, você encontra duas ferramentas de suporte:

1. **`template_edital.json`**:
   - Arquivo modelo que mostra a estrutura de correlação entre os tópicos do edital e as metas de estudo.

2. **`importar_edital_txt.py`**:
   - Permite colar os tópicos brutos do edital em um arquivo `.txt` e convertê-los automaticamente para JSON:
   ```bash
   python OUTROS-TRTS/importar_edital_txt.py --cargo TJAA --arquivo edital_bruto.txt --saida TRT-XX-UF/Mapeamento-Edital/editais_mapped.json
   ```

---

## 🔒 Diretriz de Segurança e Proteção de Dados (LGPD)

> **ATENÇÃO:** Nunca coloque arquivos `.pdf` neste repositório.
> Arquivos baixados de plataformas terceiras geralmente contêm marcas d'água com seu **CPF e dados pessoais**.
> - O arquivo `.gitignore` bloqueia permanentemente `*.pdf` e `*.PDF`.
> - Utilize HTMLs na pasta `Cadernos-Completos/` ou JSONs para alimentar o sistema sem expor sua privacidade.
