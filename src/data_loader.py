import yfinance as yf
import pandas as pd

def get_sp500_tickers():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
    df = pd.read_csv(url)
    tickers = df["Symbol"].tolist()
    tickers = [t.replace(".", "-") for t in tickers]
    return tickers

def download_prices(tickers, start, end):
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    data = data.dropna(axis=1, thresh=int(0.8 * len(data)))
    return data

if __name__ == "__main__":
    tickers = get_sp500_tickers()
    print(f"Total tickers: {len(tickers)}")
    prices = download_prices(tickers, "2020-01-01", "2024-01-01")
    print(prices.shape)
    prices.to_csv("data/prices.csv")
    print("Guardado em data/prices.csv")