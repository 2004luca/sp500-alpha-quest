# S&P 500 Alpha-Quest: Dynamic Allocation 🚀

A systematic multi-factor portfolio strategy built on the S&P 500 universe, combining **Momentum**, **Low Volatility**, and **Mean Reversion** signals to outperform the market on a risk-adjusted basis.

---

## 📊 Results Summary

| Metric | Multi-Factor Strategy | SPY (S&P 500) |
|---|---|---|
| Total Return | **146.13%** | 111.20% |
| Annual Return | **19.79%** | 16.17% |
| Sharpe Ratio | **0.92** | 0.77 |
| Volatility | 21.62% | 20.98% |
| Max Drawdown | -37.70% | -33.72% |

> Backtest period: January 2019 — January 2024

---

## 🧠 Strategy Overview

The strategy selects the **top 50 stocks** from the S&P 500 each day based on a combined score of 3 factors:

### Factor 1 — Momentum (40%)
Stocks that performed well over the last 12 months tend to continue performing well. We exclude the last month (21 days) to avoid short-term reversal effects.

### Factor 2 — Low Volatility (30%)
More stable stocks tend to deliver better risk-adjusted returns. We use the inverse of volatility so that stable stocks receive a higher score.

### Factor 3 — Mean Reversion (30%)
Stocks that have fallen below their historical average tend to recover. We measure how far each stock is below its 3-month rolling mean.

### Portfolio Construction
Each factor is ranked and normalized between 0 and 1 before combining. The top 50 stocks receive an equal weight of 2% each.

---

## 📁 Project Structure
```
sp500-alpha-quest/
├── data/                   # Historical price data (S&P 500 constituents)
├── notebooks/
│   ├── sp500_strategy.ipynb  # Main notebook with full analysis
│   └── dashboard.py          # Interactive Plotly dashboard
├── src/
│   ├── data_loader.py        # Downloads S&P 500 price data
│   ├── strategy.py           # Multi-factor scoring logic
│   └── backtest.py           # Backtest engine and metrics
├── results/                  # Charts and dashboard output
└── requirements.txt
```

---

## 🔗 Links

- 📓 [Full Notebook](https://nbviewer.org/github/2004luca/sp500-alpha-quest/blob/main/notebooks/sp500_strategy.ipynb)
- 📊 [Interactive Dashboard](https://2004luca.github.io/sp500-alpha-quest/results/dashboard.html)

---

## ⚙️ How to Run

1. Clone the repository:
```bash
git clone https://github.com/2004luca/sp500-alpha-quest.git
cd sp500-alpha-quest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download data:
```bash
python src/data_loader.py
```

4. Run the notebook:
```bash
jupyter notebook notebooks/sp500_strategy.ipynb
```

5. Generate the dashboard:
```bash
cd notebooks
python dashboard.py
```

---

## 🛠️ Technologies

- **Python 3.14**
- **pandas** — data manipulation
- **yfinance** — market data
- **numpy** — numerical computing
- **matplotlib** — static charts
- **plotly** — interactive dashboard
- **scipy** — optimization

---

## 👤 Author

Luca Santucci