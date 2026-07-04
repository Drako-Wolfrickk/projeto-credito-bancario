"""
Converte os CSVs para o formato brasileiro (ponto e vírgula como separador,
vírgula como decimal) para importação correta no Power BI em PT-BR.
Execute: python corrigir_csv.py
"""

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR  = os.path.join(BASE_DIR, "exportados")

# Colunas numéricas (com decimal) por arquivo
COLUNAS_DECIMAL = {
    "clientes.csv":  ["renda_mensal"],
    "contratos.csv": ["valor_financiado", "valor_parcela", "taxa_juros_mensal"],
    "parcelas.csv":  ["valor_devido", "valor_pago"],
    "produtos.csv":  ["taxa_juros_mensal", "valor_minimo", "valor_maximo"],
}

def formatar_valor(valor, eh_decimal):
    """Troca ponto por vírgula nos campos numéricos."""
    if not eh_decimal or valor == "" or valor is None:
        return valor
    return valor.replace(".", ",")

for arquivo, colunas_dec in COLUNAS_DECIMAL.items():
    caminho = os.path.join(CSV_DIR, arquivo)
    saida   = os.path.join(CSV_DIR, arquivo.replace(".csv", "_br.csv"))

    with open(caminho, "r", encoding="utf-8") as fin, \
         open(saida,   "w", encoding="utf-8-sig", newline="") as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames, delimiter=";")
        writer.writeheader()

        for row in reader:
            nova_row = {}
            for col, val in row.items():
                nova_row[col] = formatar_valor(val, col in colunas_dec)
            writer.writerow(nova_row)

    print(f"  ✔ {arquivo.replace('.csv', '_br.csv')} gerado")

print("\n✅ Pronto! Importe os arquivos _br.csv no Power BI.")
print("   Use 'Ponto e vírgula' como delimitador na importação.")
