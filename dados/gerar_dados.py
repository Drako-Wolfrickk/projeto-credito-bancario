"""
=============================================================
  PROJETO: Análise de Crédito e Inadimplência Bancária
  Script : Gerador de Dados Sintéticos
  Autor  : Gustavo Ribeiro (portfolio)
  Gerado : via Python + SQLite
=============================================================
Execute com:  python gerar_dados.py
Resultado  :  banco_credito.db  +  CSVs na pasta /exportados
=============================================================
"""

import sqlite3
import random
import math
import os
import csv
from datetime import date, timedelta

# ── Reprodutibilidade ─────────────────────────────────────
random.seed(42)
TODAY = date(2026, 6, 20)

# ── Pastas de saída ───────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH   = os.path.join(BASE_DIR, "banco_credito.db")
CSV_DIR   = os.path.join(BASE_DIR, "exportados")
os.makedirs(CSV_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────
# DADOS DE REFERÊNCIA
# ─────────────────────────────────────────────────────────
ESTADOS = [
    ('SP',0.22),('RJ',0.12),('MG',0.11),('RS',0.07),('PR',0.06),
    ('SC',0.05),('BA',0.04),('GO',0.03),('DF',0.03),('CE',0.03),
    ('PE',0.03),('ES',0.02),('MS',0.02),('MT',0.02),('AM',0.02),
    ('PA',0.02),('AL',0.02),('PB',0.02),('MA',0.02),('RO',0.02),
]
ESTADO_NOMES, ESTADO_PESOS = zip(*ESTADOS)

PRODUTOS = [
    # (codigo, nome, taxa_mensal, prazo_max, val_min, val_max)
    ("CP", "Crédito Pessoal",           0.035, 60,  1_000,    50_000),
    ("FI", "Financiamento Imobiliário", 0.008, 360, 100_000, 1_000_000),
    ("CV", "CDC Veículo",               0.015, 60,  20_000,  200_000),
    ("CC", "Cartão de Crédito",         0.045, 12,  500,      15_000),
    ("CS", "Crédito Consignado",        0.018, 96,  2_000,   100_000),
]
PRODUTO_MAP = {p[0]: p for p in PRODUTOS}

SEGMENTOS   = ["Premium", "Middle", "Básico", "PJ"]
SEG_PESOS   = [0.15, 0.40, 0.35, 0.10]

PROFISSOES  = ["Servidor Público","CLT - Privado","Autônomo",
               "Aposentado","Empresário","Profissional Liberal"]

# Renda por segmento (min, max) em R$
RENDA_SEG = {
    "Premium": (8_000,  40_000),
    "Middle":  (3_000,   8_000),
    "Básico":  (1_000,   3_000),
    "PJ":      (10_000, 80_000),
}

# Score de crédito por segmento (min, max) — escala 300-900
SCORE_SEG = {
    "Premium": (700, 900),
    "Middle":  (550, 750),
    "Básico":  (300, 580),
    "PJ":      (600, 850),
}

# Taxa base de inadimplência por segmento x produto
INADIMP = {
    ("Premium","CP"):0.03, ("Premium","FI"):0.01, ("Premium","CV"):0.02,
    ("Premium","CC"):0.05, ("Premium","CS"):0.01,
    ("Middle", "CP"):0.10, ("Middle", "FI"):0.03, ("Middle", "CV"):0.07,
    ("Middle", "CC"):0.14, ("Middle", "CS"):0.04,
    ("Básico", "CP"):0.20, ("Básico", "FI"):0.07, ("Básico", "CV"):0.12,
    ("Básico", "CC"):0.25, ("Básico", "CS"):0.06,
    ("PJ",     "CP"):0.08, ("PJ",     "FI"):0.04, ("PJ",     "CV"):0.06,
    ("PJ",     "CC"):0.12, ("PJ",     "CS"):0.03,
}

NOMES = [
    "Carlos Silva","Maria Santos","José Oliveira","Ana Souza","Pedro Lima",
    "Fernanda Pereira","Paulo Costa","Juliana Ferreira","Roberto Rodrigues",
    "Camila Almeida","Marcos Nascimento","Patricia Carvalho","Ricardo Martins",
    "Bruna Araújo","Rafael Gomes","Luciana Barbosa","Fernando Ribeiro",
    "Mariana Rocha","Alexandre Cardoso","Cristina Mendes","Lucas Teixeira",
    "Larissa Moreira","Rodrigo Nunes","Vanessa Correia","Eduardo Freitas",
    "Priscila Azevedo","Thiago Miranda","Renata Castro","Daniel Cavalcanti",
    "Tatiana Pinto","Leandro Monteiro","Michelle Cunha","Anderson Dias",
    "Carla Melo","Marcelo Moraes","Claudia Lopes","Diego Ramos","Aline Vieira",
    "Bruno Machado","Roberta Andrade","Henrique Peixoto","Natalia Campos",
    "Gustavo Duarte","Leticia Farias","Rodrigo Batista","Sabrina Tavares",
    "Vinicius Siqueira","Beatriz Paiva","Caio Rezende","Isabela Neves",
]

# ─────────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────
def rand_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def wchoice(population, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    cum = 0
    for item, w in zip(population, weights):
        cum += w
        if r <= cum:
            return item
    return population[-1]

def calcular_parcela(valor: float, taxa: float, n: int) -> float:
    """Price/SAC — tabela Price simplificada."""
    if taxa == 0:
        return valor / n
    return valor * (taxa * (1 + taxa)**n) / ((1 + taxa)**n - 1)

def add_months(d: date, months: int) -> date:
    m = d.month - 1 + months
    year  = d.year + m // 12
    month = m % 12 + 1
    day   = min(d.day, [31,28,31,30,31,30,31,31,30,31,30,31][month-1])
    return date(year, month, day)

def dias_atraso(data_venc: date, data_pag: date | None) -> int:
    if data_pag is None:
        return max(0, (TODAY - data_venc).days)
    return max(0, (data_pag - data_venc).days)

def categoria_aging(dias: int) -> str:
    if dias == 0:            return "EM_DIA"
    if dias <= 30:           return "1-30 dias"
    if dias <= 60:           return "31-60 dias"
    if dias <= 90:           return "61-90 dias"
    return                          "90+ dias"

# ─────────────────────────────────────────────────────────
# GERAÇÃO DOS DADOS
# ─────────────────────────────────────────────────────────
def gerar_clientes(n=500):
    clientes = []
    nomes_usados = set()
    for i in range(1, n + 1):
        nome = random.choice(NOMES)
        # Evita duplicata exata de nome
        sufixo = 1
        base   = nome
        while nome in nomes_usados:
            nome = f"{base} {sufixo}"
            sufixo += 1
        nomes_usados.add(nome)

        segmento = wchoice(SEGMENTOS, SEG_PESOS)
        rmin, rmax = RENDA_SEG[segmento]
        smin, smax = SCORE_SEG[segmento]

        clientes.append({
            "id_cliente":     i,
            "nome":           nome,
            "segmento":       segmento,
            "profissao":      random.choice(PROFISSOES),
            "renda_mensal":   round(random.uniform(rmin, rmax), 2),
            "score_credito":  random.randint(smin, smax),
            "estado":         wchoice(ESTADO_NOMES, ESTADO_PESOS),
            "data_nascimento":rand_date(date(1960,1,1), date(2000,12,31)).isoformat(),
            "data_cadastro":  rand_date(date(2020,1,1), date(2024,12,31)).isoformat(),
        })
    return clientes

def gerar_contratos(clientes, n=750):
    contratos = []
    parcelas  = []
    id_parcela = 1
    id_contrato = 1

    # Vários clientes terão 1 contrato, alguns terão 2
    cliente_ids = [c["id_cliente"] for c in clientes]
    # Sorteia clientes, permitindo repetição para ~30% terem 2 contratos
    pool = cliente_ids + random.sample(cliente_ids, k=int(len(cliente_ids)*0.30))
    random.shuffle(pool)
    pool = pool[:n]

    segmento_map = {c["id_cliente"]: c["segmento"] for c in clientes}

    for cod_contrato, id_cliente in enumerate(pool, start=1):
        prod_code = wchoice(
            [p[0] for p in PRODUTOS],
            [0.30, 0.15, 0.20, 0.20, 0.15]  # distribuição de produtos
        )
        prod = PRODUTO_MAP[prod_code]
        _, _, taxa_base, prazo_max, val_min, val_max = prod

        # Prazo (em meses)
        prazo = random.choice([6,12,18,24,36,48,60,72,96,120,180,240,360])
        prazo = min(prazo, prazo_max)

        valor = round(random.uniform(val_min, val_max), 2)
        taxa  = taxa_base * random.uniform(0.85, 1.25)
        taxa  = round(taxa, 5)
        parcela = round(calcular_parcela(valor, taxa, prazo), 2)

        # Data de início (entre jan/2023 e dez/2025)
        data_inicio = rand_date(date(2023,1,1), date(2025,12,31))
        data_fim    = add_months(data_inicio, prazo)
        status_contrato = "QUITADO" if data_fim < TODAY else "ATIVO"

        contrato_id = f"CTR{cod_contrato:05d}"
        segmento    = segmento_map[id_cliente]
        taxa_inadimp = INADIMP.get((segmento, prod_code), 0.10)
        # O cliente tem comportamento definido
        eh_inadimplente = random.random() < taxa_inadimp

        contratos.append({
            "id_contrato":      contrato_id,
            "id_cliente":       id_cliente,
            "id_produto":       prod_code,
            "valor_financiado": valor,
            "valor_parcela":    parcela,
            "taxa_juros_mensal":round(taxa * 100, 4),
            "qtd_parcelas":     prazo,
            "data_inicio":      data_inicio.isoformat(),
            "data_fim":         data_fim.isoformat(),
            "status_contrato":  status_contrato,
        })

        # ── Gera as parcelas ──────────────────────────────
        for num in range(1, prazo + 1):
            data_venc = add_months(data_inicio, num)

            # Parcelas futuras
            if data_venc > TODAY:
                parcelas.append({
                    "id_parcela":     id_parcela,
                    "id_contrato":    contrato_id,
                    "numero_parcela": num,
                    "data_vencimento":data_venc.isoformat(),
                    "data_pagamento": None,
                    "valor_devido":   parcela,
                    "valor_pago":     None,
                    "status_parcela": "A_VENCER",
                    "dias_atraso":    0,
                    "categoria_aging":"A_VENCER",
                })
                id_parcela += 1
                continue

            # Parcelas passadas
            if eh_inadimplente:
                # Determina a partir de que parcela começa a atrasar
                parcela_quebra = random.randint(max(1, prazo//3), prazo)
                if num < parcela_quebra:
                    # Pagou em dia antes de quebrar
                    atraso = 0
                    dpag   = data_venc + timedelta(days=random.randint(0, 2))
                    status = "PAGO_EM_DIA"
                else:
                    # Inadimplente
                    atraso_dias = (TODAY - data_venc).days
                    # Pode ter pago com muito atraso ou ainda não ter pago
                    if random.random() < 0.3 and atraso_dias > 5:
                        # Pagou atrasado
                        atraso = random.randint(5, min(90, atraso_dias))
                        dpag   = data_venc + timedelta(days=atraso)
                        status = "PAGO_COM_ATRASO"
                    else:
                        # Ainda não pagou
                        dpag   = None
                        atraso = atraso_dias
                        status = "INADIMPLENTE"
            else:
                # Cliente bom: paga em dia, raramente atrasa
                r = random.random()
                if r < 0.85:
                    atraso = 0
                    dpag   = data_venc - timedelta(days=random.randint(0, 3))
                    status = "PAGO_EM_DIA"
                elif r < 0.97:
                    atraso = random.randint(1, 15)
                    dpag   = data_venc + timedelta(days=atraso)
                    status = "PAGO_COM_ATRASO"
                else:
                    dpag   = None
                    atraso = (TODAY - data_venc).days
                    status = "INADIMPLENTE"

            parcelas.append({
                "id_parcela":     id_parcela,
                "id_contrato":    contrato_id,
                "numero_parcela": num,
                "data_vencimento":data_venc.isoformat(),
                "data_pagamento": dpag.isoformat() if dpag else None,
                "valor_devido":   parcela,
                "valor_pago":     round(parcela * random.uniform(0.98,1.0), 2) if dpag else None,
                "status_parcela": status,
                "dias_atraso":    atraso,
                "categoria_aging":categoria_aging(atraso) if status == "INADIMPLENTE" else "EM_DIA" if atraso==0 else f"1-{atraso} dias",
            })
            id_parcela += 1

    return contratos, parcelas

# ─────────────────────────────────────────────────────────
# BANCO DE DADOS
# ─────────────────────────────────────────────────────────
DDL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS parcelas;
DROP TABLE IF EXISTS contratos;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS clientes;

CREATE TABLE clientes (
    id_cliente      INTEGER PRIMARY KEY,
    nome            TEXT    NOT NULL,
    segmento        TEXT    NOT NULL,
    profissao       TEXT,
    renda_mensal    REAL    NOT NULL,
    score_credito   INTEGER NOT NULL,
    estado          TEXT    NOT NULL,
    data_nascimento TEXT,
    data_cadastro   TEXT
);

CREATE TABLE produtos (
    id_produto          TEXT PRIMARY KEY,
    nome_produto        TEXT    NOT NULL,
    taxa_juros_mensal   REAL    NOT NULL,
    prazo_maximo_meses  INTEGER NOT NULL,
    valor_minimo        REAL,
    valor_maximo        REAL
);

CREATE TABLE contratos (
    id_contrato         TEXT PRIMARY KEY,
    id_cliente          INTEGER NOT NULL,
    id_produto          TEXT    NOT NULL,
    valor_financiado    REAL    NOT NULL,
    valor_parcela       REAL    NOT NULL,
    taxa_juros_mensal   REAL    NOT NULL,
    qtd_parcelas        INTEGER NOT NULL,
    data_inicio         TEXT    NOT NULL,
    data_fim            TEXT    NOT NULL,
    status_contrato     TEXT    NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_produto) REFERENCES produtos(id_produto)
);

CREATE TABLE parcelas (
    id_parcela          INTEGER PRIMARY KEY,
    id_contrato         TEXT    NOT NULL,
    numero_parcela      INTEGER NOT NULL,
    data_vencimento     TEXT    NOT NULL,
    data_pagamento      TEXT,
    valor_devido        REAL    NOT NULL,
    valor_pago          REAL,
    status_parcela      TEXT    NOT NULL,
    dias_atraso         INTEGER NOT NULL DEFAULT 0,
    categoria_aging     TEXT,
    FOREIGN KEY (id_contrato) REFERENCES contratos(id_contrato)
);
"""

def criar_banco(clientes, produtos, contratos, parcelas):
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.executescript(DDL)

    # Clientes
    cur.executemany("""
        INSERT INTO clientes VALUES
        (:id_cliente,:nome,:segmento,:profissao,:renda_mensal,
         :score_credito,:estado,:data_nascimento,:data_cadastro)
    """, clientes)

    # Produtos
    for p in produtos:
        cur.execute("""
            INSERT INTO produtos VALUES (?,?,?,?,?,?)
        """, p)

    # Contratos
    cur.executemany("""
        INSERT INTO contratos VALUES
        (:id_contrato,:id_cliente,:id_produto,:valor_financiado,
         :valor_parcela,:taxa_juros_mensal,:qtd_parcelas,
         :data_inicio,:data_fim,:status_contrato)
    """, contratos)

    # Parcelas
    cur.executemany("""
        INSERT INTO parcelas VALUES
        (:id_parcela,:id_contrato,:numero_parcela,:data_vencimento,
         :data_pagamento,:valor_devido,:valor_pago,
         :status_parcela,:dias_atraso,:categoria_aging)
    """, parcelas)

    conn.commit()
    conn.close()
    print(f"  ✔ banco_credito.db criado com sucesso")

def exportar_csv(nome_arquivo, linhas):
    if not linhas:
        return
    path = os.path.join(CSV_DIR, nome_arquivo)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=linhas[0].keys())
        writer.writeheader()
        writer.writerows(linhas)
    print(f"  ✔ {nome_arquivo}  ({len(linhas):,} linhas)")

# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🏦  Gerando dados do projeto Crédito Bancário...\n")

    # 1. Clientes
    clientes = gerar_clientes(500)

    # 2. Produtos (tabela de referência)
    produtos = [(p[0],p[1],p[2],p[3],p[4],p[5]) for p in PRODUTOS]

    # 3. Contratos e parcelas
    contratos, parcelas = gerar_contratos(clientes, 750)

    # 4. Banco SQLite
    print("📦 Criando banco de dados SQLite...")
    criar_banco(clientes, produtos, contratos, parcelas)

    # 5. Exportar CSVs (para uso no Power BI)
    print("\n📄 Exportando CSVs para Power BI...")

    # Produtos como lista de dicts para o CSV
    produtos_dicts = [
        {"id_produto":p[0],"nome_produto":p[1],"taxa_juros_mensal":p[2],
         "prazo_maximo_meses":p[3],"valor_minimo":p[4],"valor_maximo":p[5]}
        for p in PRODUTOS
    ]

    exportar_csv("clientes.csv",  clientes)
    exportar_csv("produtos.csv",  produtos_dicts)
    exportar_csv("contratos.csv", contratos)
    exportar_csv("parcelas.csv",  parcelas)

    # Resumo
    inadimp = [p for p in parcelas if p["status_parcela"] == "INADIMPLENTE"]
    pagas   = [p for p in parcelas if p["status_parcela"] in ("PAGO_EM_DIA","PAGO_COM_ATRASO")]
    a_vencer= [p for p in parcelas if p["status_parcela"] == "A_VENCER"]

    total_carteira = sum(c["valor_financiado"] for c in contratos)
    val_em_risco   = sum(p["valor_devido"] for p in inadimp)

    print(f"""
📊 Resumo do Dataset Gerado
{'─'*40}
  Clientes     : {len(clientes):>6,}
  Contratos    : {len(contratos):>6,}
  Parcelas     : {len(parcelas):>6,}
    → A Vencer : {len(a_vencer):>6,}
    → Pagas    : {len(pagas):>6,}
    → Inadimp. : {len(inadimp):>6,}
{'─'*40}
  Carteira Total: R$ {total_carteira:>14,.2f}
  Valor em Risco: R$ {val_em_risco:>14,.2f}
  Taxa Inadimp. : {len(inadimp)/len([p for p in parcelas if p['status_parcela'] != 'A_VENCER'])*100:.1f}%
{'─'*40}
✅ Pronto! Próximo passo: abra o arquivo queries_analise.sql
""")
