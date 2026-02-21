import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime

# ── 1. LER E PROCESSAR O CSV ─────────────────────────────────────────────────

df = pd.read_csv("sales_data.csv")
df["total"] = df["quantidade"] * df["preco_unitario"]

total_geral = df["total"].sum()
total_por_categoria = df.groupby("categoria")["total"].sum().sort_values(ascending=False)
top5_produtos = (
    df.groupby("produto")["total"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)

# ── 2. CONFIGURAR DOCUMENTO ───────────────────────────────────────────────────

doc = SimpleDocTemplate(
    "sales_report.pdf",
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm,
)

styles = getSampleStyleSheet()
WIDTH, HEIGHT = A4

# Estilos customizados
style_title = ParagraphStyle(
    "titulo",
    parent=styles["Title"],
    fontSize=22,
    textColor=colors.HexColor("#1a1a2e"),
    spaceAfter=4,
    alignment=TA_CENTER,
)
style_subtitle = ParagraphStyle(
    "subtitulo",
    parent=styles["Normal"],
    fontSize=10,
    textColor=colors.HexColor("#555555"),
    spaceAfter=2,
    alignment=TA_CENTER,
)
style_section = ParagraphStyle(
    "secao",
    parent=styles["Heading2"],
    fontSize=13,
    textColor=colors.HexColor("#16213e"),
    spaceBefore=16,
    spaceAfter=6,
    borderPad=4,
)
style_total = ParagraphStyle(
    "total",
    parent=styles["Normal"],
    fontSize=13,
    textColor=colors.HexColor("#0f3460"),
    alignment=TA_RIGHT,
    spaceBefore=8,
)

AZUL_ESCURO  = colors.HexColor("#16213e")
AZUL_MEDIO   = colors.HexColor("#0f3460")
AZUL_CLARO   = colors.HexColor("#e8f0fe")
CINZA_LINHA  = colors.HexColor("#f0f0f0")

def estilo_tabela(tem_total=False):
    base = [
        ("BACKGROUND",  (0, 0), (-1, 0),  AZUL_ESCURO),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  10),
        ("ALIGN",       (0, 0), (-1, 0),  "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA_LINHA]),
        ("FONTSIZE",    (0, 1), (-1, -1), 9),
        ("ALIGN",       (1, 1), (-1, -1), "RIGHT"),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
    ]
    if tem_total:
        base += [
            ("BACKGROUND", (0, -1), (-1, -1), AZUL_CLARO),
            ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
            ("LINEABOVE",  (0, -1), (-1, -1), 1, AZUL_MEDIO),
        ]
    return TableStyle(base)

# ── 3. MONTAR CONTEÚDO ────────────────────────────────────────────────────────

story = []

# Cabeçalho
story.append(Paragraph("Relatório de Vendas", style_title))
story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", style_subtitle))
story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=2, color=AZUL_MEDIO))
story.append(Spacer(1, 12))

# Card total geral
story.append(Paragraph("Resumo Geral", style_section))
dados_total = [
    ["Métrica", "Valor"],
    ["Total de transações", f"{len(df):,}"],
    ["Quantidade total vendida", f"{df['quantidade'].sum():,} unidades"],
    ["Receita total", f"R$ {total_geral:,.2f}"],
]
t = Table(dados_total, colWidths=[10*cm, 7*cm])
t.setStyle(estilo_tabela())
story.append(t)

# Vendas por categoria
story.append(Paragraph("Vendas por Categoria", style_section))
dados_cat = [["Categoria", "Receita", "% do Total"]]
for cat, valor in total_por_categoria.items():
    pct = valor / total_geral * 100
    dados_cat.append([cat, f"R$ {valor:,.2f}", f"{pct:.1f}%"])
dados_cat.append(["TOTAL", f"R$ {total_geral:,.2f}", "100%"])

t2 = Table(dados_cat, colWidths=[7*cm, 6*cm, 4*cm])
t2.setStyle(estilo_tabela(tem_total=True))
story.append(t2)

# Top 5 produtos
story.append(Paragraph("Top 5 Produtos por Receita", style_section))
dados_top = [["#", "Produto", "Receita"]]
for i, (prod, valor) in enumerate(top5_produtos.items(), 1):
    dados_top.append([str(i), prod, f"R$ {valor:,.2f}"])

t3 = Table(dados_top, colWidths=[1.5*cm, 11*cm, 5*cm])
t3.setStyle(estilo_tabela())
story.append(t3)

story.append(Spacer(1, 20))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 6))
story.append(Paragraph(
    f"Período analisado: {df['data'].min()} a {df['data'].max()}  |  Fonte: vendas.csv",
    ParagraphStyle("rodape", parent=styles["Normal"], fontSize=8,
                   textColor=colors.HexColor("#999999"), alignment=TA_CENTER)
))

# ── 4. GERAR PDF ──────────────────────────────────────────────────────────────

doc.build(story)
print("✅ Report generated successfully: sales_report.pdf")
