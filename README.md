# CSV to PDF Report Generator

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-2.x-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.x-E74C3C?style=flat)](https://www.reportlab.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat)](LICENSE)

Automated report generation pipeline: reads raw sales data from a CSV file and produces a formatted, print-ready PDF report — with summary KPIs, revenue breakdown by category, and top products ranked by revenue.

Built for businesses that need to turn spreadsheet exports into professional reports **without manual formatting work**.

---

## Sample Output

The script takes a raw CSV like this:

| date | product | category | quantity | unit_price |
|------|---------|----------|----------|------------|
| 2024-01-05 | Notebook Dell | Electronics | 3 | 3500.00 |
| 2024-01-07 | Logitech Mouse | Electronics | 15 | 120.00 |
| 2024-02-10 | Pilot Pen (box) | Stationery | 30 | 25.00 |

And generates a structured PDF report with three sections:

**General Summary**
| Metric | Value |
|--------|-------|
| Total transactions | 30 |
| Total units sold | 311 units |
| Total revenue | R$ 128,435.00 |

**Revenue by Category** — with percentage share of each category and a total row.

**Top 5 Products by Revenue** — ranked list, ready to share with stakeholders.

> To see the actual output, run the script and open `sales_report.pdf`. A pre-generated sample is included in the repository.

---

## Use Cases

- **Sales reporting** — automate weekly/monthly reports from ERP or e-commerce exports
- **Inventory summaries** — turn stock data into management-ready documents
- **Financial snapshots** — generate recurring PDF summaries from accounting CSV exports
- **Client deliverables** — produce branded, professional reports programmatically

---

## Tech Stack

| Tool | Role |
|------|------|
| **Python 3.8+** | Core language |
| **pandas** | Data loading, aggregation, and transformation |
| **ReportLab** | PDF layout engine — tables, styles, typography |

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/csv-to-pdf-report.git
cd csv-to-pdf-report
```

**2. Install dependencies**

```bash
pip install pandas reportlab
```

> No virtual environment setup required, but recommended for clean installs:
> ```bash
> python -m venv venv && source venv/bin/activate  # Linux/macOS
> python -m venv venv && venv\Scripts\activate     # Windows
> pip install pandas reportlab
> ```

---

## Usage

**1. Prepare your data**

Place your CSV file in the project folder, or use the included `sales_data.csv` sample.

Your CSV must have these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `data` | string | Sale date | `2024-01-05` |
| `produto` | string | Product name | `Notebook Dell` |
| `categoria` | string | Category | `Electronics` |
| `quantidade` | integer | Units sold | `3` |
| `preco_unitario` | float | Unit price | `3500.00` |

**2. Run the script**

```bash
python generate_report.py
```

**3. Collect the output**

```
✅ Report generated successfully: sales_report.pdf
```

Open `sales_report.pdf` — ready to print or share.

---

## Project Structure

```
csv-to-pdf-report/
├── generate_report.py   # Main script — data processing + PDF generation
├── sales_data.csv       # Sample dataset (30 transactions, 3 months)
├── sales_report.pdf     # Pre-generated output sample
└── README.md
```

---

## Customization

The script is structured in four clearly separated stages, making it easy to adapt:

- **Stage 1 — Data ingestion**: swap `sales_data.csv` for any CSV source, add filters or date ranges
- **Stage 2 — Document config**: change page size, margins, or fonts to match your brand
- **Stage 3 — Content assembly**: add new sections (charts, conditional highlights, multi-sheet data)
- **Stage 4 — PDF build**: extend to batch generation, email delivery, or cloud storage upload

Common extensions I can implement on request:
- Custom logo and company branding
- Date range filtering via CLI arguments
- Batch processing (generate one PDF per month/region)
- Chart integration (bar/pie charts with matplotlib or ReportLab graphics)
- Email delivery via SMTP or SendGrid

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.

---

*Built by a Python automation specialist. Open to freelance projects involving data pipelines, report automation, and document generation.*
