# 📊 CSV to PDF Sales Report Generator

A Python script that reads a CSV file with sales data and automatically generates a clean, professional PDF report.

## What it does

- Reads raw sales data from a CSV file
- Calculates total revenue, revenue by category, and top 5 products
- Generates a formatted PDF report with tables and summary

## Example Output

The generated report includes:
- **General summary** — total transactions, units sold, and total revenue
- **Sales by category** — revenue breakdown with percentage per category
- **Top 5 products** — ranked by total revenue

## Requirements

- Python 3.8+
- pandas
- reportlab

Install dependencies:

```bash
pip install pandas reportlab
```

## How to use

1. Place your CSV file in the project folder (or use the included `sales_data.csv` sample)
2. Run the script:

```bash
python generate_report.py
```

3. Open `sales_report.pdf` in the project folder

## CSV format

Your CSV file must have these columns:

| Column | Description | Example |
|---|---|---|
| `data` | Sale date | 2024-01-05 |
| `produto` | Product name | Notebook Dell |
| `categoria` | Category | Electronics |
| `quantidade` | Units sold | 3 |
| `preco_unitario` | Unit price | 3500.00 |
