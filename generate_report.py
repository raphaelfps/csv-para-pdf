import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas as rl_canvas
from datetime import datetime

# ── PALETA DE CORES ───────────────────────────────────────────────────────────
AZUL_ESCURO  = colors.HexColor("#16213e")
AZUL_MEDIO   = colors.HexColor("#0f3460")
AZUL_CLARO   = colors.HexColor("#e8f0fe")
CINZA_LINHA  = colors.HexColor("#f5f5f5")
DESTAQUE     = colors.HexColor("#e94560")
VERDE        = colors.HexColor("#27ae60")
LARANJA      = colors.HexColor("#f39c12")
BRANCO       = colors.white

PALETA_MPL = ["#16213e", "#0f3460", "#1a6b8a", "#2196F3",
              "#64B5F6", "#90CAF9", "#e94560", "#f39c12", "#27ae60", "#8e44ad"]

WIDTH, HEIGHT = A4
MARGEM       = 2 * cm
FULL_W       = WIDTH - 2 * MARGEM

# ── 1. CARREGAR E PROCESSAR DADOS ─────────────────────────────────────────────
df = pd.read_csv("sales_data.csv")
df["data"]  = pd.to_datetime(df["data"])
df["total"] = df["quantidade"] * df["preco_unitario"]
df["mes"]   = df["data"].dt.to_period("M")

# KPIs gerais
total_geral      = df["total"].sum()
total_transacoes = len(df)
ticket_medio     = df["total"].mean()
qtd_total        = df["quantidade"].sum()

# Análise mensal
monthly       = df.groupby("mes")["total"].sum().sort_index()
monthly_qtd   = df.groupby("mes")["quantidade"].sum().sort_index()
monthly_short = [m.strftime("%b/%y") for m in monthly.index]
monthly_growth = monthly.pct_change() * 100
crescimento_anual = (monthly.iloc[-1] / monthly.iloc[0] - 1) * 100

# Análise por categoria
cat_receita = df.groupby("categoria")["total"].sum().sort_values(ascending=False)
cat_qtd     = df.groupby("categoria")["quantidade"].sum()
cat_ticket  = cat_receita / cat_qtd

# Análise por produto
prod_receita = df.groupby("produto")["total"].sum().sort_values(ascending=False)
prod_qtd     = df.groupby("produto")["quantidade"].sum()
top5_prods   = prod_receita.head(5)

# Análise por vendedor
vend_receita    = df.groupby("vendedor")["total"].sum().sort_values(ascending=False)
vend_transacoes = df.groupby("vendedor").size()
vend_ticket     = (
    df.groupby("vendedor")["total"].sum() / df.groupby("vendedor").size()
)

# Análise regional
reg_receita = df.groupby("regiao")["total"].sum().sort_values(ascending=False)
reg_qtd     = df.groupby("regiao")["quantidade"].sum()

# ── 2. GERAÇÃO DE GRÁFICOS (matplotlib → BytesIO) ────────────────────────────
plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
})


def fig_to_image(fig, width_cm, height_cm):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width_cm * cm, height=height_cm * cm)


def chart_tendencia_mensal():
    """Linha de receita mensal com área preenchida."""
    fig, ax = plt.subplots(figsize=(13, 3.8))
    x    = list(range(len(monthly)))
    vals = monthly.values / 1000

    ax.fill_between(x, vals, alpha=0.12, color="#0f3460")
    ax.plot(x, vals, color="#0f3460", linewidth=2.5, marker="o",
            markersize=5, markerfacecolor="#e94560", markeredgewidth=0)

    for i, v in enumerate(vals):
        ax.annotate(f"R${v:.0f}k", (i, v),
                    textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=7.5, color="#333333")

    ax.set_xticks(x)
    ax.set_xticklabels(monthly_short, fontsize=8.5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"R${v:.0f}k"))
    ax.tick_params(axis="y", labelsize=8)
    ax.set_title("Receita Mensal (R$ mil)", fontsize=11,
                 fontweight="bold", color="#16213e", pad=10)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    return fig


def chart_crescimento_mensal():
    """Barras de crescimento mês a mês."""
    fig, ax = plt.subplots(figsize=(13, 2.8))
    g    = monthly_growth.dropna()
    x    = list(range(len(g)))
    lbls = [monthly_short[i + 1] for i in x]
    cors = ["#27ae60" if v >= 0 else "#e94560" for v in g.values]

    bars = ax.bar(x, g.values, color=cors, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(lbls, fontsize=8)
    ax.axhline(0, color="#cccccc", linewidth=0.8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.tick_params(axis="y", labelsize=8)
    ax.set_title("Crescimento Mês a Mês (%)", fontsize=11,
                 fontweight="bold", color="#16213e", pad=10)
    for bar, val in zip(bars, g.values):
        offset = 1.2 if val >= 0 else -4
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + offset,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=7)
    fig.tight_layout()
    return fig


def chart_pizza_categorias():
    """Pizza de participação por categoria."""
    fig, ax = plt.subplots(figsize=(7, 6))
    wedges, _, autotexts = ax.pie(
        cat_receita.values,
        autopct="%1.1f%%",
        colors=PALETA_MPL[:len(cat_receita)],
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        pctdistance=0.72,
    )
    ax.set_aspect("equal")
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")
    ax.legend(wedges, cat_receita.index,
              loc="lower center", bbox_to_anchor=(0.5, -0.08),
              ncol=len(cat_receita), fontsize=9, frameon=False)
    ax.set_title("Participação por Categoria", fontsize=11,
                 fontweight="bold", color="#16213e", pad=10)
    fig.tight_layout()
    return fig


def chart_top_produtos():
    """Barras horizontais — top 5 produtos."""
    fig, ax = plt.subplots(figsize=(11, 3.5))
    prods = top5_prods.index.tolist()[::-1]
    vals  = top5_prods.values[::-1] / 1000
    cors  = PALETA_MPL[:5][::-1]

    bars = ax.barh(prods, vals, color=cors, height=0.55)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.3,
                bar.get_y() + bar.get_height() / 2,
                f"R${val:.1f}k", va="center", fontsize=8.5, color="#333333")

    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"R${v:.0f}k"))
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlim(0, vals.max() * 1.2)
    ax.set_title("Top 5 Produtos por Receita (R$ mil)", fontsize=11,
                 fontweight="bold", color="#16213e", pad=10)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.tight_layout()
    return fig


def chart_vendedores():
    """Barras de receita por vendedor."""
    fig, ax = plt.subplots(figsize=(8, 3.5))
    x    = list(range(len(vend_receita)))
    vals = vend_receita.values / 1000
    bars = ax.bar(x, vals, color=PALETA_MPL[:len(vend_receita)], width=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(vend_receita.index, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"R${v:.0f}k"))
    ax.tick_params(axis="y", labelsize=8)
    ax.set_title("Receita por Vendedor (R$ mil)", fontsize=11,
                 fontweight="bold", color="#16213e", pad=10)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"R${val:.1f}k", ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    return fig


def chart_regioes():
    """Barras de receita por região."""
    fig, ax = plt.subplots(figsize=(8, 3))
    x    = list(range(len(reg_receita)))
    vals = reg_receita.values / 1000
    bars = ax.bar(x, vals, color=PALETA_MPL[2:2 + len(reg_receita)], width=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(reg_receita.index, fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"R${v:.0f}k"))
    ax.tick_params(axis="y", labelsize=8)
    ax.set_title("Receita por Região (R$ mil)", fontsize=11,
                 fontweight="bold", color="#16213e", pad=10)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"R${val:.1f}k", ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    fig.tight_layout()
    return fig


# ── 3. ESTILOS PDF ────────────────────────────────────────────────────────────
_ss = getSampleStyleSheet()


def _s(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=_ss[parent], **kw)


sTitle     = _s("sTitle",    "Title",  fontSize=26, textColor=BRANCO,
                alignment=TA_CENTER, spaceAfter=4, leading=32)
sCoverSub  = _s("sCoverSub",          fontSize=13, textColor=colors.HexColor("#aabbdd"),
                alignment=TA_CENTER, spaceAfter=4)
sCoverDate = _s("sCoverDate",         fontSize=9,  textColor=colors.HexColor("#888888"),
                alignment=TA_CENTER)
sSection   = _s("sSection",           fontSize=13, textColor=AZUL_ESCURO,
                fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
sBody      = _s("sBody",              fontSize=9,  textColor=colors.HexColor("#444444"),
                spaceAfter=4, leading=14)
sKpiLabel  = _s("sKpiLabel",          fontSize=8,  textColor=colors.HexColor("#6688aa"),
                alignment=TA_CENTER)
sKpiValue  = _s("sKpiValue",          fontSize=20, textColor=AZUL_MEDIO,
                alignment=TA_CENTER, fontName="Helvetica-Bold")
sFooter    = _s("sFooter",            fontSize=8,  textColor=colors.HexColor("#999999"),
                alignment=TA_CENTER)


def tabela_estilo(tem_total=False):
    base = [
        ("BACKGROUND",    (0, 0),  (-1, 0),  AZUL_ESCURO),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  BRANCO),
        ("FONTNAME",      (0, 0),  (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0),  (-1, 0),  9),
        ("ALIGN",         (0, 0),  (-1, 0),  "CENTER"),
        ("ROWBACKGROUNDS",(0, 1),  (-1, -1), [colors.white, CINZA_LINHA]),
        ("FONTSIZE",      (0, 1),  (-1, -1), 8.5),
        ("ALIGN",         (1, 1),  (-1, -1), "RIGHT"),
        ("ALIGN",         (0, 1),  (0, -1),  "LEFT"),
        ("GRID",          (0, 0),  (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("TOPPADDING",    (0, 0),  (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 5),
        ("LEFTPADDING",   (0, 0),  (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0),  (-1, -1), 7),
    ]
    if tem_total:
        base += [
            ("BACKGROUND", (0, -1), (-1, -1), AZUL_CLARO),
            ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
            ("LINEABOVE",  (0, -1), (-1, -1), 1, AZUL_MEDIO),
        ]
    return TableStyle(base)


# ── 4. CANVAS COM NUMERAÇÃO DE PÁGINAS ───────────────────────────────────────
class NumeradorPaginas(rl_canvas.Canvas):
    def __init__(self, *args, **kwargs):
        rl_canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_page_states)
        for i, state in enumerate(self._saved_page_states):
            self.__dict__.update(state)
            if i > 0:  # capa sem rodapé
                self._draw_footer(i + 1, total)
            rl_canvas.Canvas.showPage(self)
        rl_canvas.Canvas.save(self)

    def _draw_footer(self, current, total):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#aaaaaa"))
        self.drawString(MARGEM, 1.3 * cm,
                        "Relatório de Vendas 2024  |  Confidencial")
        self.drawRightString(WIDTH - MARGEM, 1.3 * cm,
                             f"Página {current} de {total}")
        self.setStrokeColor(colors.HexColor("#dddddd"))
        self.setLineWidth(0.5)
        self.line(MARGEM, 1.6 * cm, WIDTH - MARGEM, 1.6 * cm)
        self.restoreState()


# ── 5. CONSTRUÇÃO DO STORY ────────────────────────────────────────────────────
story = []

# ── CAPA ──────────────────────────────────────────────────────────────────────
capa_header = Table(
    [[Paragraph("RELATÓRIO DE VENDAS 2024", sTitle)]],
    colWidths=[FULL_W],
    rowHeights=[3.8 * cm],
)
capa_header.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), AZUL_ESCURO),
    ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 18),
]))

story.append(Spacer(1, 1.5 * cm))
story.append(capa_header)
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("Análise Completa de Desempenho Comercial", sCoverSub))
story.append(Spacer(1, 0.15 * cm))
story.append(Paragraph(
    f"Período: Jan/2024 – Dez/2024  ·  Gerado em "
    f"{datetime.now().strftime('%d/%m/%Y às %H:%M')}",
    sCoverDate,
))
story.append(Spacer(1, 0.8 * cm))
story.append(HRFlowable(width="100%", thickness=1.5, color=AZUL_MEDIO))
story.append(Spacer(1, 0.6 * cm))

# Cards de KPIs
cresc_str = f"+{crescimento_anual:.1f}%" if crescimento_anual >= 0 else f"{crescimento_anual:.1f}%"
kpi_table = Table(
    [
        [Paragraph("RECEITA TOTAL",  sKpiLabel),
         Paragraph("TRANSAÇÕES",     sKpiLabel),
         Paragraph("TICKET MÉDIO",   sKpiLabel),
         Paragraph("CRESCIMENTO\nJAN→DEZ", sKpiLabel)],
        [Paragraph(f"R$ {total_geral / 1000:.1f}k", sKpiValue),
         Paragraph(str(total_transacoes),            sKpiValue),
         Paragraph(f"R$ {ticket_medio:,.0f}",        sKpiValue),
         Paragraph(cresc_str,                         sKpiValue)],
    ],
    colWidths=[FULL_W / 4] * 4,
    rowHeights=[0.75 * cm, 1.3 * cm],
)
kpi_table.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, -1), AZUL_CLARO),
    ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING",    (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#c0cfee")),
    ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#c0cfee")),
]))
story.append(kpi_table)
story.append(Spacer(1, 0.8 * cm))

# Destaques do ano na capa
melhor_mes_str = monthly.idxmax().strftime("%B/%Y")
top_vendedor   = vend_receita.idxmax()
melhor_cat     = cat_receita.idxmax()

dest_rows = [
    ["Destaque", "Detalhe", "Receita"],
    ["Melhor Mês",       melhor_mes_str, f"R$ {monthly.max():,.2f}"],
    ["Categoria Líder",  melhor_cat,     f"R$ {cat_receita.max():,.2f}"],
    ["Top Vendedor",     top_vendedor,   f"R$ {vend_receita.max():,.2f}"],
    ["Produto #1",       prod_receita.idxmax(),
                         f"R$ {prod_receita.max():,.2f}"],
]
t_dest = Table(dest_rows, colWidths=[5 * cm, 7 * cm, 5 * cm])
t_dest.setStyle(tabela_estilo())
story.append(Paragraph("Destaques do Ano", sSection))
story.append(t_dest)
story.append(PageBreak())

# ── SEÇÃO 1: EVOLUÇÃO MENSAL ──────────────────────────────────────────────────
story.append(Paragraph("1. Evolução de Receita Mensal", sSection))
story.append(HRFlowable(width="100%", thickness=1, color=AZUL_CLARO))
story.append(Spacer(1, 0.3 * cm))
story.append(fig_to_image(chart_tendencia_mensal(), 17, 5.5))
story.append(Spacer(1, 0.4 * cm))
story.append(fig_to_image(chart_crescimento_mensal(), 17, 4))
story.append(Spacer(1, 0.5 * cm))

story.append(Paragraph("Detalhamento Mensal", sSection))
rows_mensal = [["Mês", "Receita", "Qtd Vendida", "Transações", "Crescimento MoM"]]
for mes, receita in monthly.items():
    label   = mes.strftime("%B/%Y").capitalize()
    qtd_m   = int(df[df["mes"] == mes]["quantidade"].sum())
    trans_m = int((df["mes"] == mes).sum())
    growth  = monthly_growth[mes]
    g_str   = f"{growth:+.1f}%" if pd.notna(growth) else "—"
    rows_mensal.append([label, f"R$ {receita:,.2f}", f"{qtd_m:,}", str(trans_m), g_str])

t_mensal = Table(rows_mensal,
                 colWidths=[4.5 * cm, 4.5 * cm, 3.5 * cm, 2.5 * cm, 3.5 * cm])
t_mensal.setStyle(tabela_estilo())
story.append(t_mensal)
story.append(PageBreak())

# ── SEÇÃO 2: ANÁLISE POR CATEGORIA ───────────────────────────────────────────
story.append(Paragraph("2. Análise por Categoria", sSection))
story.append(HRFlowable(width="100%", thickness=1, color=AZUL_CLARO))
story.append(Spacer(1, 0.3 * cm))

# Pizza centralizada em largura total
pizza_img = fig_to_image(chart_pizza_categorias(), 10, 8)
pizza_centrado = Table(
    [[pizza_img]],
    colWidths=[FULL_W],
)
pizza_centrado.setStyle(TableStyle([
    ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
    ("LEFTPADDING",  (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
]))
story.append(pizza_centrado)
story.append(Spacer(1, 0.4 * cm))

# Tabela em largura total
rows_cat = [["Categoria", "Receita", "% Total", "Qtd Vendida", "Ticket Médio"]]
for cat in cat_receita.index:
    pct = cat_receita[cat] / total_geral * 100
    rows_cat.append([
        cat,
        f"R$ {cat_receita[cat]:,.2f}",
        f"{pct:.1f}%",
        f"{int(cat_qtd[cat]):,}",
        f"R$ {cat_ticket[cat]:,.2f}",
    ])
rows_cat.append([
    "TOTAL",
    f"R$ {total_geral:,.2f}",
    "100%",
    f"{int(qtd_total):,}",
    f"R$ {ticket_medio:,.2f}",
])
t_cat = Table(rows_cat,
              colWidths=[4.5 * cm, 4 * cm, 2.5 * cm, 2.5 * cm, 3.5 * cm])
t_cat.setStyle(tabela_estilo(tem_total=True))
story.append(t_cat)
story.append(PageBreak())

# ── SEÇÃO 3: PERFORMANCE DE PRODUTOS ─────────────────────────────────────────
story.append(Paragraph("3. Performance de Produtos", sSection))
story.append(HRFlowable(width="100%", thickness=1, color=AZUL_CLARO))
story.append(Spacer(1, 0.3 * cm))
story.append(fig_to_image(chart_top_produtos(), 17, 5))
story.append(Spacer(1, 0.5 * cm))

rows_prod = [["Produto", "Categoria", "Receita", "Qtd", "Ticket Médio", "% Total"]]
for prod in prod_receita.index:
    cat_p    = df[df["produto"] == prod]["categoria"].iloc[0]
    qtd_p    = int(prod_qtd[prod])
    ticket_p = prod_receita[prod] / qtd_p
    pct_p    = prod_receita[prod] / total_geral * 100
    rows_prod.append([
        prod, cat_p,
        f"R$ {prod_receita[prod]:,.2f}",
        f"{qtd_p:,}",
        f"R$ {ticket_p:,.2f}",
        f"{pct_p:.1f}%",
    ])
rows_prod.append([
    "TOTAL", "—",
    f"R$ {total_geral:,.2f}",
    f"{int(qtd_total):,}",
    f"R$ {ticket_medio:,.2f}",
    "100%",
])
t_prod = Table(rows_prod,
               colWidths=[4.5 * cm, 2.8 * cm, 3.2 * cm, 2 * cm, 2.8 * cm, 1.7 * cm])
t_prod.setStyle(tabela_estilo(tem_total=True))
story.append(t_prod)
story.append(PageBreak())

# ── SEÇÃO 4: PERFORMANCE DE VENDEDORES ───────────────────────────────────────
story.append(Paragraph("4. Performance de Vendedores", sSection))
story.append(HRFlowable(width="100%", thickness=1, color=AZUL_CLARO))
story.append(Spacer(1, 0.3 * cm))
story.append(fig_to_image(chart_vendedores(), 12, 5))
story.append(Spacer(1, 0.5 * cm))

rows_vend = [["#", "Vendedor", "Receita", "Transações", "Ticket Médio", "% Total"]]
for i, (vend, receita) in enumerate(vend_receita.items(), 1):
    rows_vend.append([
        str(i), vend,
        f"R$ {receita:,.2f}",
        str(int(vend_transacoes[vend])),
        f"R$ {vend_ticket[vend]:,.2f}",
        f"{receita / total_geral * 100:.1f}%",
    ])
rows_vend.append([
    "", "TOTAL",
    f"R$ {total_geral:,.2f}",
    str(total_transacoes),
    f"R$ {ticket_medio:,.2f}",
    "100%",
])
t_vend = Table(rows_vend,
               colWidths=[1 * cm, 4 * cm, 3.8 * cm, 2.5 * cm, 3.5 * cm, 2.2 * cm])
t_vend.setStyle(tabela_estilo(tem_total=True))
story.append(t_vend)

# Pivot vendedor × categoria
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph("Receita por Vendedor × Categoria", sSection))
pivot_vc  = df.pivot_table(
    values="total", index="vendedor",
    columns="categoria", aggfunc="sum", fill_value=0,
)
cats_vc   = list(pivot_vc.columns)
n_vc      = len(cats_vc)
cat_w     = (FULL_W - 4.5 * cm - 2.5 * cm) / n_vc
rows_pv   = [["Vendedor"] + cats_vc + ["Total"]]
for vend in pivot_vc.index:
    linha = [vend]
    for cat in cats_vc:
        linha.append(f"R${pivot_vc.loc[vend, cat] / 1000:.1f}k")
    linha.append(f"R${vend_receita[vend] / 1000:.1f}k")
    rows_pv.append(linha)
tot_pv = ["TOTAL"]
for cat in cats_vc:
    tot_pv.append(f"R${cat_receita[cat] / 1000:.1f}k")
tot_pv.append(f"R${total_geral / 1000:.1f}k")
rows_pv.append(tot_pv)

t_pv = Table(rows_pv,
             colWidths=[4.5 * cm] + [cat_w] * n_vc + [2.5 * cm])
t_pv.setStyle(tabela_estilo(tem_total=True))
story.append(t_pv)
story.append(PageBreak())

# ── SEÇÃO 5: ANÁLISE REGIONAL ─────────────────────────────────────────────────
story.append(Paragraph("5. Análise Regional", sSection))
story.append(HRFlowable(width="100%", thickness=1, color=AZUL_CLARO))
story.append(Spacer(1, 0.3 * cm))
story.append(fig_to_image(chart_regioes(), 12, 4.5))
story.append(Spacer(1, 0.5 * cm))

rows_reg = [["Região", "Receita", "% Total", "Qtd Vendida", "Transações"]]
for reg in reg_receita.index:
    pct_r   = reg_receita[reg] / total_geral * 100
    qtd_r   = int(reg_qtd[reg])
    trans_r = int((df["regiao"] == reg).sum())
    rows_reg.append([
        reg,
        f"R$ {reg_receita[reg]:,.2f}",
        f"{pct_r:.1f}%",
        f"{qtd_r:,}",
        str(trans_r),
    ])
rows_reg.append([
    "TOTAL",
    f"R$ {total_geral:,.2f}",
    "100%",
    f"{int(qtd_total):,}",
    str(total_transacoes),
])
t_reg = Table(rows_reg,
              colWidths=[4.5 * cm, 4.5 * cm, 2.5 * cm, 3 * cm, 2.5 * cm])
t_reg.setStyle(tabela_estilo(tem_total=True))
story.append(t_reg)

# Pivot região × categoria
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph("Receita por Região × Categoria", sSection))
pivot_rc = df.pivot_table(
    values="total", index="regiao",
    columns="categoria", aggfunc="sum", fill_value=0,
)
cats_rc  = list(pivot_rc.columns)
n_rc     = len(cats_rc)
cat_w2   = (FULL_W - 4.5 * cm - 2.5 * cm) / n_rc
rows_prc = [["Região"] + cats_rc + ["Total"]]
for reg in pivot_rc.index:
    linha = [reg]
    for cat in cats_rc:
        linha.append(f"R${pivot_rc.loc[reg, cat] / 1000:.1f}k")
    linha.append(f"R${reg_receita[reg] / 1000:.1f}k")
    rows_prc.append(linha)
tot_rc = ["TOTAL"]
for cat in cats_rc:
    tot_rc.append(f"R${cat_receita[cat] / 1000:.1f}k")
tot_rc.append(f"R${total_geral / 1000:.1f}k")
rows_prc.append(tot_rc)

t_prc = Table(rows_prc,
              colWidths=[4.5 * cm] + [cat_w2] * n_rc + [2.5 * cm])
t_prc.setStyle(tabela_estilo(tem_total=True))
story.append(t_prc)

# Rodapé final
story.append(Spacer(1, 1 * cm))
story.append(HRFlowable(width="100%", thickness=0.5,
                         color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph(
    f"Período: {df['data'].min().strftime('%d/%m/%Y')} a "
    f"{df['data'].max().strftime('%d/%m/%Y')}  |  "
    f"Fonte: sales_data.csv  |  Gerado por generate_report.py",
    sFooter,
))

# ── 6. GERAR PDF ──────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    "sales_report.pdf",
    pagesize=A4,
    rightMargin=MARGEM,
    leftMargin=MARGEM,
    topMargin=MARGEM,
    bottomMargin=2.5 * cm,
)
doc.build(story, canvasmaker=NumeradorPaginas)
print("Relatorio gerado com sucesso: sales_report.pdf")
