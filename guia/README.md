# 🏦 Análise de Crédito e Inadimplência Bancária
**Projeto de Portfólio — SQL + Power BI**

---

## 📋 Sobre o Projeto

Simulação de uma carteira de crédito bancário com **500 clientes**, **650 contratos** e
mais de **30.000 parcelas**, cobrindo os principais produtos financeiros do mercado brasileiro.

O objetivo é responder perguntas reais que analistas de dados bancários enfrentam no dia a dia:

- Qual é a taxa de inadimplência atual da carteira?
- Quais segmentos e produtos concentram mais risco?
- Qual o valor em risco por faixa de atraso (aging)?
- Como a inadimplência evoluiu ao longo do tempo?

---

## 🗂️ Estrutura do Projeto

```
projeto_credito/
│
├── dados/
│   ├── gerar_dados.py          ← Script Python que cria tudo
│   ├── banco_credito.db        ← Banco SQLite (gerado pelo script)
│   └── exportados/
│       ├── clientes.csv        ← Para Power BI
│       ├── produtos.csv        ← Para Power BI
│       ├── contratos.csv       ← Para Power BI
│       └── parcelas.csv        ← Para Power BI
│
├── sql/
│   └── queries_analise.sql     ← Todas as queries, do básico ao avançado
│
└── guia/
    └── README.md               ← Este arquivo
```

---

## 🗄️ Modelo de Dados

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   CLIENTES   │──────▶│  CONTRATOS   │◀──────│   PRODUTOS   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id_cliente   │       │ id_contrato  │       │ id_produto   │
│ nome         │       │ id_cliente   │       │ nome_produto │
│ segmento     │       │ id_produto   │       │ taxa_juros   │
│ profissao    │       │ valor_financ │       │ prazo_max    │
│ renda_mensal │       │ valor_parcela│       └──────────────┘
│ score_credito│       │ qtd_parcelas │
│ estado       │       │ data_inicio  │
└──────────────┘       │ status       │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   PARCELAS   │
                       ├──────────────┤
                       │ id_parcela   │
                       │ id_contrato  │
                       │ data_vencim. │
                       │ data_pagam.  │
                       │ valor_devido │
                       │ status       │  ← A_VENCER / PAGO_EM_DIA /
                       │ dias_atraso  │     PAGO_COM_ATRASO / INADIMPLENTE
                       │ aging        │
                       └──────────────┘
```

---

## 🚀 Passo a Passo

### ETAPA 1 — Gerar os dados

1. Certifique-se de ter Python instalado (`python --version`)
2. Na pasta `dados/`, execute:
   ```
   python gerar_dados.py
   ```
3. Serão criados: `banco_credito.db` + 4 arquivos CSV na pasta `exportados/`

---

### ETAPA 2 — Explorar com SQL

**Ferramenta recomendada:** DB Browser for SQLite (100% gratuito)
- Download: https://sqlitebrowser.org/dl/

**Passos:**
1. Abra o DB Browser
2. Clique em **"Abrir banco de dados"** → selecione `banco_credito.db`
3. Vá na aba **"Executar SQL"**
4. Abra o arquivo `queries_analise.sql` e execute cada bloco

**Ordem de estudo sugerida:**
| Nível | O que praticar |
|-------|---------------|
| 🟢 Básico (1.1 a 1.5) | SELECT, WHERE, ORDER BY, GROUP BY simples |
| 🟡 Intermediário (2.1 a 2.6) | Agregações, JOINs entre tabelas, HAVING |
| 🔵 Avançado (3.1 a 4.5) | CASE WHEN, CTEs, Subqueries |
| 🏆 Dashboard (PBI-01 a 07) | Queries prontas para o Power BI |

---

### ETAPA 3 — Montar o Dashboard no Power BI

**Pré-requisito:** Power BI Desktop instalado (grátis em microsoft.com/power-bi)

#### Importar os dados:
1. Abra o Power BI Desktop
2. **Página inicial** → **Obter dados** → **Texto/CSV**
3. Importe os 4 arquivos da pasta `exportados/`:
   - `clientes.csv`
   - `produtos.csv`
   - `contratos.csv`
   - `parcelas.csv`
4. Clique em **Carregar** para cada um

#### Criar relacionamentos:
Vá em **Exibição de Modelo** e conecte:
- `contratos[id_cliente]` → `clientes[id_cliente]`
- `contratos[id_produto]` → `produtos[id_produto]`
- `parcelas[id_contrato]` → `contratos[id_contrato]`

#### Visuais sugeridos para o dashboard:

| Visual | Campo(s) | Fonte |
|--------|----------|-------|
| 📊 Cartão — Carteira Total | SUM(contratos[valor_financiado]) | contratos |
| 📊 Cartão — Valor em Risco | SUM parcelas inadimplentes | parcelas |
| 📊 Cartão — Taxa Inadimplência % | Medida DAX (ver abaixo) | — |
| 📈 Linha — Evolução Mensal | data_vencimento x taxa | parcelas |
| 📊 Barras — Por Segmento | segmento x taxa | clientes + parcelas |
| 🥧 Pizza — Aging da Carteira | categoria_aging x valor | parcelas |
| 🗺️ Mapa — Por Estado | estado x valor_risco | clientes + parcelas |
| 📋 Tabela — Clientes em Risco | drill-down completo | todas |

#### Medidas DAX essenciais:
```dax
// Taxa de Inadimplência
Taxa Inadimplência =
DIVIDE(
    COUNTROWS(FILTER(parcelas, parcelas[status_parcela] = "INADIMPLENTE")),
    COUNTROWS(FILTER(parcelas, parcelas[status_parcela] <> "A_VENCER"))
) * 100

// Valor em Risco
Valor em Risco =
CALCULATE(
    SUM(parcelas[valor_devido]),
    parcelas[status_parcela] = "INADIMPLENTE"
)

// Carteira Ativa
Carteira Total =
CALCULATE(
    SUM(contratos[valor_financiado]),
    contratos[status_contrato] = "ATIVO"
)
```

---

## 🎯 O que destacar no portfólio

Quando apresentar este projeto, mencione:

1. **Modelagem de dados:** criou um banco relacional com 4 tabelas e chaves estrangeiras
2. **SQL do básico ao avançado:** queries com JOINs múltiplos, CTEs, subqueries
3. **Domínio do negócio:** entende termos como aging, score de crédito, taxa de inadimplência
4. **Visualização:** transformou dados brutos em um dashboard executivo no Power BI
5. **Escala:** trabalhou com mais de 30.000 registros de forma eficiente

---

## 📖 Glossário Bancário

| Termo | Significado |
|-------|-------------|
| **Inadimplência** | Atraso no pagamento de uma parcela vencida |
| **Aging da Carteira** | Classificação do atraso em faixas (1-30, 31-60, 61-90, 90+) |
| **Score de Crédito** | Pontuação que indica o risco de inadimplência de um cliente |
| **Valor em Risco** | Valor total das parcelas em atraso |
| **Taxa de Inadimplência** | % de parcelas inadimplentes sobre o total de vencidas |
| **Ticket Médio** | Valor médio financiado por contrato |
| **Carteira** | Conjunto de todos os contratos de crédito do banco |
| **CDC** | Crédito Direto ao Consumidor (ex: financiamento de veículo) |
| **Consignado** | Crédito com desconto em folha de pagamento |

---

*Projeto desenvolvido para fins de estudo e demonstração de habilidades em SQL e BI.*
