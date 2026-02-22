# CSV to PDF Report Generator

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-2.x-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![matplotlib](https://img.shields.io/badge/matplotlib-3.x-11557C?style=flat)](https://matplotlib.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.x-E74C3C?style=flat)](https://www.reportlab.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat)](LICENSE)

Automated report generation pipeline: reads raw sales data from a CSV file and produces a multi-page, print-ready PDF report — with embedded charts, KPI cards, cross-dimensional pivot tables, and per-page footer navigation.

Built for businesses that need to turn spreadsheet exports into professional reports **without manual formatting work**.

---

## Report Structure

The generated PDF contains a cover page and five analytical sections:

| Section | Content |
|---------|---------|
| **Cover** | KPI cards (total revenue, transactions, avg ticket, YoY growth) + highlights table |
| **1. Monthly Trend** | Revenue line chart with area fill + MoM growth bar chart + monthly breakdown table |
| **2. Category Analysis** | Pie chart (revenue share) + category table with ticket médio |
| **3. Product Performance** | Horizontal bar chart (top 5) + full product ranking table |
| **4. Salesperson Performance** | Revenue bar chart + ranking table + salesperson × category pivot |
| **5. Regional Analysis** | Regional bar chart + table + region × category pivot |

All charts are generated with matplotlib and embedded directly in the PDF as high-resolution images — no temporary files.

---

## Sample Output

The script takes a raw CSV like this:

| data | produto | categoria | quantidade | preco_unitario | vendedor | regiao |
|------|---------|-----------|------------|----------------|----------|--------|
| 2024-01-05 | Notebook Dell | Eletrônicos | 3 | 3500.00 | Ana Silva | Sudeste |
| 2024-03-10 | Cadeira Gamer | Móveis | 3 | 1800.00 | Carlos Mendes | Nordeste |
| 2024-11-15 | Mouse Logitech | Eletrônicos | 50 | 120.00 | Bruno Costa | Sul |

And generates a structured, multi-page PDF — ready to print or share with stakeholders.

> A pre-generated sample (`sales_report.pdf`) is included in the repository.

---

## Use Cases

- **Sales reporting** — automate weekly/monthly reports from ERP or e-commerce exports
- **Salesperson performance reviews** — rank reps by revenue, transactions, and avg ticket
- **Regional dashboards** — break down performance across territories
- **Inventory summaries** — turn stock data into management-ready documents
- **Client deliverables** — produce branded, professional reports programmatically

---

## Tech Stack

| Tool | Role |
|------|------|
| **Python 3.8+** | Core language |
| **pandas** | Data loading, aggregation, pivot tables, and time-series analysis |
| **matplotlib** | Chart generation (line, bar, pie) embedded as PNG via `BytesIO` |
| **ReportLab** | PDF layout engine — multi-page documents, tables, styles, custom canvas |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/raphaelfps/csv-para-pdf.git
cd csv-para-pdf
```

**2. Install dependencies**

```bash
pip install pandas matplotlib reportlab
```

> Recommended: use a virtual environment
> ```bash
> python -m venv venv && source venv/bin/activate  # Linux/macOS
> python -m venv venv && venv\Scripts\activate     # Windows
> pip install pandas matplotlib reportlab
> ```

---

## Usage

**1. Prepare your data**

Place your CSV file in the project folder, or use the included `sales_data.csv` sample (120 transactions across 12 months).

Your CSV must have these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `data` | string | Sale date | `2024-01-05` |
| `produto` | string | Product name | `Notebook Dell` |
| `categoria` | string | Category | `Eletrônicos` |
| `quantidade` | integer | Units sold | `3` |
| `preco_unitario` | float | Unit price | `3500.00` |
| `vendedor` | string | Salesperson name | `Ana Silva` |
| `regiao` | string | Sales region | `Sudeste` |

**2. Run the script**

```bash
python generate_report.py
```

**3. Collect the output**

```
Relatorio gerado com sucesso: sales_report.pdf
```

Open `sales_report.pdf` — ready to print or share.

---

## Project Structure

```
csv-para-pdf/
├── generate_report.py   # Main script — data processing, chart generation, PDF build
├── sales_data.csv       # Sample dataset (120 transactions, 12 months)
├── sales_report.pdf     # Pre-generated output sample
└── README.md
```

---

## Customization

The script is organized in six clearly separated stages:

- **Stage 1 — Data ingestion**: swap `sales_data.csv` for any CSV source, add filters or date ranges
- **Stage 2 — Analytics**: extend aggregations — add new dimensions, custom KPIs, or forecasting
- **Stage 3 — Chart generation**: each chart is an isolated function returning a `matplotlib` figure — easy to swap styles or add new chart types
- **Stage 4 — PDF styles**: centralized color palette and style definitions — change the entire look in one place
- **Stage 5 — Content assembly**: add, remove, or reorder sections in the `story` list
- **Stage 6 — PDF build**: extend to batch generation (one PDF per region/month), email delivery, or cloud storage upload

Common extensions available on request:
- Custom logo and company branding
- Date range filtering via CLI arguments
- Batch processing (generate one PDF per month/region/salesperson)
- Email delivery via SMTP or SendGrid

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

*Built by a Python automation specialist. Open to freelance projects involving data pipelines, report automation, and document generation.*
