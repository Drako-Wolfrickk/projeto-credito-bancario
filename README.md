# 🏦 Dashboard de Análise de Crédito e Inadimplência Bancária

> Projeto de portfólio — SQL · Power BI · Python · SQLite

[![SQL](https://img.shields.io/badge/SQL-SQLite-blue)](https://sqlitebrowser.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)](https://powerbi.microsoft.com/)
[![Python](https://img.shields.io/badge/Python-3.x-green)](https://www.python.org/)
[![Portfolio](https://img.shields.io/badge/Portf%C3%B3lio-Online-orange)](https://data-journey-gustavo.lovable.app)

---

## 📋 Sobre o Projeto

Simulação completa de uma carteira de crédito bancário com **500 clientes**, **650 contratos** e mais de **30.000 parcelas**, cobrindo os principais produtos financeiros do mercado brasileiro.

O projeto foi construído do zero — da modelagem do banco de dados até o dashboard executivo — respondendo perguntas reais que analistas de dados bancários enfrentam no dia a dia.

### 🎯 Perguntas respondidas

- Qual é a taxa de inadimplência atual da carteira?
- Quais segmentos e produtos concentram mais risco?
- Qual o valor em risco por faixa de atraso (aging)?
- Como a inadimplência evoluiu ao longo do tempo?

---

## 📊 Resultados do Dashboard

| KPI | Valor |
|-----|-------|
| 💰 Carteira Total | R$ 74,6 milhões |
| ⚠️ Valor em Risco | R$ 1,42 milhões |
| 📉 Taxa de Inadimplência | 3,58% |
| 👥 Total de Clientes | 500 |
| 📄 Total de Contratos | 650 |
| 🧾 Total de Parcelas | 30.468 |

### 💡 Principais Insights

- Clientes do segmento **Básico** têm taxa de inadimplência **60% maior** que clientes Premium (4,2% vs 2,6%)
- **87,76% do valor em risco** está concentrado em atraso acima de 90 dias — alta probabilidade de perda definitiva
- A inadimplência cresceu de 2023 a 2025 e sinalizou queda em 2026, indicando melhora de safra
- Cartão de Crédito e Crédito Pessoal lideram o número de parcelas inadimplentes

---

## 🗂️ Estrutura do Projeto

```
projeto_credito/
│
├── dados/
│   ├── gerar_dados.py          ← Script Python que gera os dados
│   ├── banco_credito.db        ← Banco SQLite com 30.468 registros
│   └── exportados/
│       ├── clientes_br.csv
│       ├── contratos_br.csv
│       ├── parcelas_br.csv
│       └── produtos_br.csv
│
├── sql/
│   └── queries_analise.sql     ← 9 queries do básico ao avançado
│
├── guia/
│   └── README.md               ← Guia passo a passo do projeto
│
└── Dashboard_Credito_Bancario.pbix  ← Dashboard Power BI
```

---

## 🗄️ Modelo de Dados

```
clientes ──1──▶──*── contratos ──1──▶──*── parcelas
                         ▲
                    *────┘────1
                      produtos
```

### Tabelas

| Tabela | Registros | Descrição |
|--------|-----------|-----------|
| `clientes` | 500 | Dados cadastrais, segmento, score e renda |
| `produtos` | 5 | Crédito Pessoal, Consignado, CDC Veículo, Cartão, Imobiliário |
| `contratos` | 650 | Contratos com valor, prazo, taxa e status |
| `parcelas` | 30.468 | Histórico completo de pagamentos com aging |

---

## 🚀 Tecnologias Utilizadas

- **Python** — geração dos dados sintéticos realistas
- **SQLite** — banco de dados relacional com 4 tabelas e chaves estrangeiras
- **SQL** — 9 queries cobrindo SELECT, WHERE, GROUP BY, JOIN, CASE WHEN, CTEs e subqueries
- **Power BI** — dashboard executivo com 5 visuais e medidas DAX
- **DB Browser for SQLite** — exploração e execução das queries

---

## 📈 Queries SQL — Do Básico ao Avançado

| Nível | Conceitos |
|-------|-----------|
| 🟢 Básico | SELECT, WHERE, ORDER BY, LIMIT, GROUP BY |
| 🟡 Intermediário | COUNT, SUM, AVG, ROUND, HAVING, JOINs |
| 🔵 Avançado | CASE WHEN, múltiplos JOINs, LEFT JOIN |
| 🏆 Expert | CTEs, subqueries, análise de aging, série temporal |

---

## 📉 Visuais do Dashboard Power BI

- **3 Cartões KPI** — Carteira Total, Valor em Risco, Taxa de Inadimplência
- **Gráfico de barras** — Inadimplência por segmento de cliente
- **Gráfico de barras** — Inadimplência por produto bancário
- **Gráfico de pizza** — Aging da carteira (faixas de atraso)
- **Gráfico de linha** — Evolução mensal da inadimplência (2023–2026)

---

## ▶️ Como Reproduzir

### 1. Gerar os dados
```bash
cd dados/
python gerar_dados.py
python corrigir_csv.py
```

### 2. Explorar com SQL
- Instale o [DB Browser for SQLite](https://sqlitebrowser.org/dl/)
- Abra o arquivo `dados/banco_credito.db`
- Execute as queries em `sql/queries_analise.sql`

### 3. Abrir o Dashboard
- Instale o [Power BI Desktop](https://powerbi.microsoft.com/pt-br/downloads/)
- Abra `Dashboard_Credito_Bancario.pbix`

---

## 🔗 Links

- 🌐 [Portfólio Online](https://data-journey-gustavo.lovable.app)
- 💼 [LinkedIn](https://www.linkedin.com/in/gustavo-duarte-cloud)

---

## 👤 Autor

**Gustavo Duarte de Lima Ribeiro**
Analista de Dados JR | Cloud & BI

*Projeto desenvolvido para fins de estudo e demonstração de habilidades em SQL, Power BI e Python.*
