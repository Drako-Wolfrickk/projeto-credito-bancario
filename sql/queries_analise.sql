-- ================================================================
--  PROJETO: Análise de Crédito e Inadimplência Bancária
--  Arquivo : queries_analise.sql
--  Banco   : banco_credito.db  (SQLite)
--  Autor   : Gustavo Ribeiro (portfolio)
-- ================================================================
--  COMO USAR:
--  1. Abra o DB Browser for SQLite (grátis: sqlitebrowser.org)
--  2. Clique em "Abrir banco de dados" → selecione banco_credito.db
--  3. Vá na aba "Executar SQL"
--  4. Cole e execute cada bloco separadamente
-- ================================================================


-- ╔══════════════════════════════════════════════════════╗
-- ║         NÍVEL 1 — CONSULTAS BÁSICAS                 ║
-- ║  SELECT · WHERE · ORDER BY · LIMIT                  ║
-- ╚══════════════════════════════════════════════════════╝

-- ── 1.1  Todos os clientes do banco ──────────────────────────────
SELECT *
FROM clientes
LIMIT 10;

-- ── 1.2  Clientes do estado de SP com renda acima de R$ 5.000 ───
SELECT
    id_cliente,
    nome,
    segmento,
    renda_mensal,
    score_credito
FROM clientes
WHERE estado = 'SP'
  AND renda_mensal > 5000
ORDER BY renda_mensal DESC;

-- ── 1.3  Contratos ativos ordenados por valor ────────────────────
SELECT
    id_contrato,
    id_cliente,
    id_produto,
    valor_financiado,
    qtd_parcelas,
    data_inicio
FROM contratos
WHERE status_contrato = 'ATIVO'
ORDER BY valor_financiado DESC
LIMIT 20;

-- ── 1.4  Parcelas inadimplentes com mais de 30 dias de atraso ───
SELECT
    id_parcela,
    id_contrato,
    data_vencimento,
    valor_devido,
    dias_atraso,
    categoria_aging
FROM parcelas
WHERE status_parcela = 'INADIMPLENTE'
  AND dias_atraso > 30
ORDER BY dias_atraso DESC;

-- ── 1.5  Quantos clientes existem por segmento? ─────────────────
SELECT
    segmento,
    COUNT(*) AS total_clientes
FROM clientes
GROUP BY segmento
ORDER BY total_clientes DESC;


-- ╔══════════════════════════════════════════════════════╗
-- ║         NÍVEL 2 — AGREGAÇÕES E FILTROS              ║
-- ║  GROUP BY · HAVING · COUNT · SUM · AVG              ║
-- ╚══════════════════════════════════════════════════════╝

-- ── 2.1  Total de contratos e valor médio por produto ────────────
SELECT
    p.nome_produto,
    COUNT(c.id_contrato)          AS total_contratos,
    ROUND(AVG(c.valor_financiado),2) AS ticket_medio,
    ROUND(SUM(c.valor_financiado),2) AS carteira_total
FROM contratos c
JOIN produtos p ON c.id_produto = p.id_produto
GROUP BY p.nome_produto
ORDER BY carteira_total DESC;

-- ── 2.2  Taxa de inadimplência por segmento de cliente ──────────
--   (apenas parcelas vencidas — exclui A_VENCER)
SELECT
    cl.segmento,
    COUNT(*)                                                AS total_parcelas_vencidas,
    SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN 1 ELSE 0 END)
                                                            AS inadimplentes,
    ROUND(
        100.0 * SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN 1 ELSE 0 END)
              / COUNT(*), 2
    )                                                       AS taxa_inadimplencia_pct
FROM parcelas pa
JOIN contratos co ON pa.id_contrato = co.id_contrato
JOIN clientes  cl ON co.id_cliente  = cl.id_cliente
WHERE pa.status_parcela != 'A_VENCER'
GROUP BY cl.segmento
ORDER BY taxa_inadimplencia_pct DESC;

-- ── 2.3  Aging da carteira inadimplente (valor em risco) ────────
SELECT
    categoria_aging,
    COUNT(*)                            AS qtd_parcelas,
    ROUND(SUM(valor_devido), 2)         AS valor_em_risco,
    ROUND(AVG(dias_atraso), 1)          AS media_dias_atraso
FROM parcelas
WHERE status_parcela = 'INADIMPLENTE'
GROUP BY categoria_aging
ORDER BY
    CASE categoria_aging
        WHEN '1-30 dias'  THEN 1
        WHEN '31-60 dias' THEN 2
        WHEN '61-90 dias' THEN 3
        WHEN '90+ dias'   THEN 4
    END;

-- ── 2.4  Produtos com maior valor em risco ──────────────────────
SELECT
    p.nome_produto,
    COUNT(pa.id_parcela)            AS parcelas_inadimplentes,
    ROUND(SUM(pa.valor_devido), 2)  AS valor_em_risco
FROM parcelas pa
JOIN contratos co ON pa.id_contrato = co.id_contrato
JOIN produtos  p  ON co.id_produto  = p.id_produto
WHERE pa.status_parcela = 'INADIMPLENTE'
GROUP BY p.nome_produto
ORDER BY valor_em_risco DESC;

-- ── 2.5  Score médio dos clientes inadimplentes vs adimplentes ──
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1 FROM contratos co
            JOIN parcelas pa ON co.id_contrato = pa.id_contrato
            WHERE co.id_cliente = cl.id_cliente
              AND pa.status_parcela = 'INADIMPLENTE'
        ) THEN 'Inadimplente'
        ELSE 'Adimplente'
    END AS perfil,
    COUNT(*)                           AS qtd_clientes,
    ROUND(AVG(score_credito), 0)       AS score_medio,
    ROUND(AVG(renda_mensal), 2)        AS renda_media
FROM clientes cl
GROUP BY perfil;

-- ── 2.6  Estados com maior concentração de inadimplência ────────
SELECT
    cl.estado,
    COUNT(pa.id_parcela)                     AS parcelas_inadimp,
    ROUND(SUM(pa.valor_devido), 2)           AS valor_em_risco,
    ROUND(AVG(cl.score_credito), 0)          AS score_medio_estado
FROM parcelas pa
JOIN contratos co ON pa.id_contrato = co.id_contrato
JOIN clientes  cl ON co.id_cliente  = cl.id_cliente
WHERE pa.status_parcela = 'INADIMPLENTE'
GROUP BY cl.estado
HAVING parcelas_inadimp >= 3
ORDER BY valor_em_risco DESC;


-- ╔══════════════════════════════════════════════════════╗
-- ║         NÍVEL 3 — JOINs E CASE WHEN                 ║
-- ║  INNER JOIN · LEFT JOIN · CASE · COALESCE           ║
-- ╚══════════════════════════════════════════════════════╝

-- ── 3.1  Visão completa: cliente + contrato + produto ───────────
SELECT
    cl.nome,
    cl.segmento,
    cl.score_credito,
    cl.renda_mensal,
    co.id_contrato,
    p.nome_produto,
    co.valor_financiado,
    co.qtd_parcelas,
    co.status_contrato
FROM clientes  cl
JOIN contratos co ON cl.id_cliente  = co.id_cliente
JOIN produtos  p  ON co.id_produto  = p.id_produto
ORDER BY cl.nome
LIMIT 20;

-- ── 3.2  Classificação de risco por score de crédito ────────────
SELECT
    nome,
    score_credito,
    renda_mensal,
    CASE
        WHEN score_credito >= 800 THEN 'Muito Baixo'
        WHEN score_credito >= 650 THEN 'Baixo'
        WHEN score_credito >= 500 THEN 'Médio'
        WHEN score_credito >= 350 THEN 'Alto'
        ELSE 'Muito Alto'
    END AS risco_credito,
    CASE
        WHEN renda_mensal >= 10000 THEN 'A'
        WHEN renda_mensal >=  5000 THEN 'B'
        WHEN renda_mensal >=  3000 THEN 'C'
        ELSE 'D'
    END AS faixa_renda
FROM clientes
ORDER BY score_credito DESC;

-- ── 3.3  Clientes sem nenhum contrato (LEFT JOIN) ───────────────
SELECT
    cl.id_cliente,
    cl.nome,
    cl.segmento,
    cl.data_cadastro
FROM clientes cl
LEFT JOIN contratos co ON cl.id_cliente = co.id_cliente
WHERE co.id_contrato IS NULL;

-- ── 3.4  Situação atual de cada contrato ────────────────────────
--   (resumo de parcelas: pagas, a vencer, inadimplentes)
SELECT
    co.id_contrato,
    cl.nome,
    p.nome_produto,
    co.valor_financiado,
    co.qtd_parcelas,
    SUM(CASE WHEN pa.status_parcela IN ('PAGO_EM_DIA','PAGO_COM_ATRASO') THEN 1 ELSE 0 END) AS pagas,
    SUM(CASE WHEN pa.status_parcela = 'A_VENCER'    THEN 1 ELSE 0 END) AS a_vencer,
    SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN 1 ELSE 0 END) AS inadimplentes,
    ROUND(SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN pa.valor_devido ELSE 0 END),2)
        AS valor_inadimp
FROM contratos co
JOIN clientes  cl ON co.id_cliente  = cl.id_cliente
JOIN produtos  p  ON co.id_produto  = p.id_produto
JOIN parcelas  pa ON co.id_contrato = pa.id_contrato
GROUP BY co.id_contrato, cl.nome, p.nome_produto, co.valor_financiado, co.qtd_parcelas
HAVING inadimplentes > 0
ORDER BY valor_inadimp DESC
LIMIT 20;


-- ╔══════════════════════════════════════════════════════╗
-- ║         NÍVEL 4 — QUERIES AVANÇADAS                 ║
-- ║  CTEs · Subqueries · Window Functions               ║
-- ╚══════════════════════════════════════════════════════╝

-- ── 4.1  CTE: KPIs gerais da carteira ───────────────────────────
WITH
carteira AS (
    SELECT
        SUM(valor_financiado)   AS total_carteira,
        COUNT(id_contrato)      AS total_contratos,
        COUNT(DISTINCT id_cliente) AS total_clientes
    FROM contratos
),
inadimplencia AS (
    SELECT
        COUNT(*)             AS parcelas_inadimp,
        SUM(valor_devido)    AS valor_risco
    FROM parcelas
    WHERE status_parcela = 'INADIMPLENTE'
),
vencidas AS (
    SELECT COUNT(*) AS total_vencidas
    FROM parcelas
    WHERE status_parcela != 'A_VENCER'
)
SELECT
    ca.total_clientes,
    ca.total_contratos,
    ROUND(ca.total_carteira, 2)                                AS carteira_total_R$,
    in_.parcelas_inadimp,
    ROUND(in_.valor_risco, 2)                                  AS valor_em_risco_R$,
    ROUND(100.0 * in_.parcelas_inadimp / ve.total_vencidas, 2) AS taxa_inadimplencia_pct
FROM carteira ca, inadimplencia in_, vencidas ve;

-- ── 4.2  CTE: Evolução mensal de inadimplência (2024-2026) ──────
WITH meses AS (
    SELECT DISTINCT
        SUBSTR(data_vencimento, 1, 7) AS ano_mes
    FROM parcelas
    WHERE data_vencimento BETWEEN '2024-01-01' AND '2026-06-30'
)
SELECT
    m.ano_mes,
    COUNT(pa.id_parcela)                   AS total_vencidas,
    SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN 1 ELSE 0 END)
                                           AS inadimplentes,
    ROUND(
        100.0 * SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN 1 ELSE 0 END)
              / NULLIF(COUNT(pa.id_parcela),0), 2
    )                                      AS taxa_inadimp_pct
FROM meses m
LEFT JOIN parcelas pa
       ON SUBSTR(pa.data_vencimento,1,7) = m.ano_mes
      AND pa.status_parcela != 'A_VENCER'
GROUP BY m.ano_mes
ORDER BY m.ano_mes;

-- ── 4.3  CTE: Top 20 clientes com maior exposição a risco ───────
WITH risco_cliente AS (
    SELECT
        co.id_cliente,
        SUM(pa.valor_devido)                AS valor_risco,
        COUNT(pa.id_parcela)                AS parcelas_inadimp,
        MAX(pa.dias_atraso)                 AS max_dias_atraso
    FROM parcelas pa
    JOIN contratos co ON pa.id_contrato = co.id_contrato
    WHERE pa.status_parcela = 'INADIMPLENTE'
    GROUP BY co.id_cliente
)
SELECT
    cl.nome,
    cl.segmento,
    cl.score_credito,
    cl.estado,
    rc.parcelas_inadimp,
    ROUND(rc.valor_risco, 2)   AS valor_em_risco,
    rc.max_dias_atraso,
    CASE
        WHEN rc.max_dias_atraso > 90 THEN '🔴 Crítico'
        WHEN rc.max_dias_atraso > 60 THEN '🟠 Alto'
        WHEN rc.max_dias_atraso > 30 THEN '🟡 Médio'
        ELSE                              '🟢 Baixo'
    END AS nivel_risco
FROM risco_cliente rc
JOIN clientes cl ON rc.id_cliente = cl.id_cliente
ORDER BY rc.valor_risco DESC
LIMIT 20;

-- ── 4.4  CTE: Matriz de risco — Segmento x Produto ──────────────
WITH base AS (
    SELECT
        cl.segmento,
        p.nome_produto,
        COUNT(pa.id_parcela)                                               AS total_parc,
        SUM(CASE WHEN pa.status_parcela = 'INADIMPLENTE' THEN 1 ELSE 0 END) AS inadimp
    FROM parcelas pa
    JOIN contratos co ON pa.id_contrato = co.id_contrato
    JOIN clientes  cl ON co.id_cliente  = cl.id_cliente
    JOIN produtos  p  ON co.id_produto  = p.id_produto
    WHERE pa.status_parcela != 'A_VENCER'
    GROUP BY cl.segmento, p.nome_produto
)
SELECT
    segmento,
    nome_produto,
    total_parc,
    inadimp,
    ROUND(100.0 * inadimp / NULLIF(total_parc,0), 2) AS taxa_pct
FROM base
ORDER BY segmento, taxa_pct DESC;

-- ── 4.5  Subquery: clientes com múltiplos contratos inadimplentes
SELECT
    cl.nome,
    cl.segmento,
    cl.score_credito,
    sub.qtd_contratos_inadimp,
    ROUND(sub.total_valor_risco, 2) AS total_valor_risco
FROM clientes cl
JOIN (
    SELECT
        co.id_cliente,
        COUNT(DISTINCT co.id_contrato)   AS qtd_contratos_inadimp,
        SUM(pa.valor_devido)             AS total_valor_risco
    FROM contratos co
    JOIN parcelas pa ON co.id_contrato = pa.id_contrato
    WHERE pa.status_parcela = 'INADIMPLENTE'
    GROUP BY co.id_cliente
    HAVING COUNT(DISTINCT co.id_contrato) > 1
) sub ON cl.id_cliente = sub.id_cliente
ORDER BY sub.total_valor_risco DESC;


-- ╔══════════════════════════════════════════════════════╗
-- ║       QUERIES PARA O DASHBOARD POWER BI             ║
-- ║  (Resultados finais — exporte como CSV)             ║
-- ╚══════════════════════════════════════════════════════╝

-- ─── PBI-01  KPIs Principais ─────────────────────────────────────
--  USE: Cartões no topo do dashboard
WITH
total AS (SELECT SUM(valor_financiado) AS carteira FROM contratos),
inadi AS (SELECT SUM(valor_devido) AS em_risco, COUNT(*) AS qtd FROM parcelas WHERE status_parcela='INADIMPLENTE'),
venc  AS (SELECT COUNT(*) AS total FROM parcelas WHERE status_parcela != 'A_VENCER')
SELECT
    ROUND(total.carteira,     2) AS carteira_total,
    ROUND(inadi.em_risco,     2) AS valor_em_risco,
    inadi.qtd                    AS parcelas_inadimplentes,
    ROUND(100.0*inadi.qtd/venc.total, 2) AS taxa_inadimplencia_pct
FROM total, inadi, venc;

-- ─── PBI-02  Inadimplência por Segmento ──────────────────────────
--  USE: Gráfico de barras — Segmento x Taxa %
SELECT
    cl.segmento,
    COUNT(*)                                                         AS total_vencidas,
    SUM(CASE WHEN pa.status_parcela='INADIMPLENTE' THEN 1 ELSE 0 END) AS inadimplentes,
    ROUND(100.0*SUM(CASE WHEN pa.status_parcela='INADIMPLENTE' THEN 1 ELSE 0 END)/COUNT(*),2)
                                                                     AS taxa_pct
FROM parcelas pa
JOIN contratos co ON pa.id_contrato=co.id_contrato
JOIN clientes  cl ON co.id_cliente=cl.id_cliente
WHERE pa.status_parcela != 'A_VENCER'
GROUP BY cl.segmento ORDER BY taxa_pct DESC;

-- ─── PBI-03  Aging da Carteira ────────────────────────────────────
--  USE: Gráfico de pizza ou barras — faixas de atraso
SELECT
    categoria_aging,
    COUNT(*)                      AS qtd_parcelas,
    ROUND(SUM(valor_devido),2)    AS valor_em_risco
FROM parcelas
WHERE status_parcela = 'INADIMPLENTE'
GROUP BY categoria_aging;

-- ─── PBI-04  Evolução Mensal (Série Temporal) ────────────────────
--  USE: Gráfico de linha — meses x taxa de inadimplência
SELECT
    SUBSTR(data_vencimento,1,7)                                       AS ano_mes,
    COUNT(*)                                                          AS total_vencidas,
    SUM(CASE WHEN status_parcela='INADIMPLENTE' THEN 1 ELSE 0 END)   AS inadimplentes,
    ROUND(100.0*SUM(CASE WHEN status_parcela='INADIMPLENTE' THEN 1 ELSE 0 END)/COUNT(*),2)
                                                                      AS taxa_pct,
    ROUND(SUM(CASE WHEN status_parcela='INADIMPLENTE' THEN valor_devido ELSE 0 END),2)
                                                                      AS valor_em_risco
FROM parcelas
WHERE status_parcela != 'A_VENCER'
  AND data_vencimento >= '2024-01-01'
GROUP BY ano_mes
ORDER BY ano_mes;

-- ─── PBI-05  Inadimplência por Produto ───────────────────────────
--  USE: Gráfico de barras horizontais
SELECT
    p.nome_produto,
    COUNT(pa.id_parcela)                      AS inadimplentes,
    ROUND(SUM(pa.valor_devido),2)             AS valor_em_risco,
    ROUND(AVG(pa.dias_atraso),1)              AS media_dias_atraso
FROM parcelas pa
JOIN contratos co ON pa.id_contrato=co.id_contrato
JOIN produtos   p ON co.id_produto=p.id_produto
WHERE pa.status_parcela = 'INADIMPLENTE'
GROUP BY p.nome_produto ORDER BY valor_em_risco DESC;

-- ─── PBI-06  Inadimplência por Estado (mapa) ─────────────────────
--  USE: Mapa de calor por UF
SELECT
    cl.estado,
    COUNT(pa.id_parcela)              AS qtd_inadimplentes,
    ROUND(SUM(pa.valor_devido),2)     AS valor_em_risco
FROM parcelas pa
JOIN contratos co ON pa.id_contrato=co.id_contrato
JOIN clientes  cl ON co.id_cliente=cl.id_cliente
WHERE pa.status_parcela = 'INADIMPLENTE'
GROUP BY cl.estado ORDER BY valor_em_risco DESC;

-- ─── PBI-07  Tabela Detalhe — Clientes em Risco ──────────────────
--  USE: Tabela detalhada com drill-down
SELECT
    cl.nome,
    cl.segmento,
    cl.estado,
    cl.score_credito,
    p.nome_produto,
    co.id_contrato,
    co.valor_financiado,
    pa.numero_parcela,
    pa.data_vencimento,
    pa.valor_devido,
    pa.dias_atraso,
    pa.categoria_aging,
    CASE
        WHEN pa.dias_atraso > 90 THEN 'Crítico'
        WHEN pa.dias_atraso > 60 THEN 'Alto'
        WHEN pa.dias_atraso > 30 THEN 'Médio'
        ELSE 'Baixo'
    END AS nivel_risco
FROM parcelas pa
JOIN contratos co ON pa.id_contrato=co.id_contrato
JOIN clientes  cl ON co.id_cliente=cl.id_cliente
JOIN produtos   p ON co.id_produto=p.id_produto
WHERE pa.status_parcela = 'INADIMPLENTE'
ORDER BY pa.dias_atraso DESC;
