# 📁 Modelo de Organização para Novos Tribunais (TRTs)

Este diretório serve como referência e guia para adicionar novos tribunais ao repositório **CADERNO DO TRT**.

---

## 📋 Padrão de Nomenclatura das Pastas

Cada novo tribunal deve ser criado na raiz do repositório seguindo o padrão:
```
TRT-[NUMERO]-[UF]/
```

Exemplos:
- `TRT-05-BA/` (Bahia)
- `TRT-06-PE/` (Pernambuco)
- `TRT-08-PA/` (Pará e Amapá)
- `TRT-12-SC/` (Santa Catarina)
- `TRT-15-SP/` (Campinas)

---

## 📂 Subpastas Obrigatórias

Dentro de cada pasta de tribunal, mantenha a mesma estrutura padronizada:

```
TRT-XX-UF/
├── Plataforma/            # index.html, sw.js, manifest.json
├── Cadernos-Completos/    # HTMLs com teoria e questões das matérias
├── Mapeamento-Edital/     # editais_mapped.json com os tópicos de TJAA/AJAJ
├── Documentos-Oficiais/   # PDFs de planilhas e guias oficiais
└── Scripts-Geradores/     # Scripts de compilação daquele tribunal
```

---

## 💡 Dica

Você pode duplicar a pasta `TRT-04-RS` como ponto de partida e apenas substituir os cadernos e PDFs específicos da nova região!
