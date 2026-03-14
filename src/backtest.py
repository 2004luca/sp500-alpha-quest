import pandas as pd
import numpy as np

def run_backtest(prices, weights):
    """
    Simula a estratégia ao longo do tempo.
    A cada dia calcula o retorno do portfolio com base nos pesos do dia anterior.
    Usamos pesos do dia anterior para evitar look-ahead bias
    (não podemos usar informação do futuro).
    """
    # Retornos diários de cada ação
    daily_returns = prices.pct_change()

    # Retorno do portfolio = soma dos retornos de cada ação * peso
    # Usamos shift(1) para usar os pesos do dia anterior
    portfolio_returns = (daily_returns * weights.shift(1)).sum(axis=1)

    # Retorno acumulado (valor de 1€ investido no início)
    cumulative_returns = (1 + portfolio_returns).cumprod()

    return portfolio_returns, cumulative_returns

def run_benchmark(prices):
    """
    Benchmark: S&P 500 equal-weight (todas as ações com peso igual).
    Serve para comparar com a nossa estratégia.
    """
    daily_returns = prices.pct_change()
    benchmark_returns = daily_returns.mean(axis=1)
    benchmark_cumulative = (1 + benchmark_returns).cumprod()
    return benchmark_returns, benchmark_cumulative

def calculate_metrics(returns, label="Portfolio"):
    """
    Calcula as métricas principais de performance:
    - Retorno total
    - Retorno anualizado
    - Volatilidade anualizada
    - Sharpe Ratio (retorno ajustado ao risco)
    - Maximum Drawdown (maior queda do pico ao vale)
    """
    # Retorno total
    total_return = (1 + returns).cumprod().iloc[-1] - 1

    # Retorno anualizado (assumindo 252 dias de trading por ano)
    n_years = len(returns) / 252
    annual_return = (1 + total_return) ** (1 / n_years) - 1

    # Volatilidade anualizada
    annual_vol = returns.std() * np.sqrt(252)

    # Sharpe Ratio (assumindo taxa livre de risco = 0)
    sharpe = annual_return / annual_vol

    # Maximum Drawdown
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    print(f"\n--- {label} ---")
    print(f"Retorno Total:       {total_return:.2%}")
    print(f"Retorno Anualizado:  {annual_return:.2%}")
    print(f"Volatilidade:        {annual_vol:.2%}")
    print(f"Sharpe Ratio:        {sharpe:.2f}")
    print(f"Maximum Drawdown:    {max_drawdown:.2%}")

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_vol": annual_vol,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown
    }

if __name__ == "__main__":
    import sys
    sys.path.append("src")
    from strategy import calculate_combined_score, select_portfolio

    # Carregar dados
    prices = pd.read_csv("data/prices.csv", index_col=0, parse_dates=True)
    print("Dados carregados:", prices.shape)

    # Calcular scores e pesos
    print("A calcular scores... (pode demorar um momento)")
    scores = calculate_combined_score(prices)
    weights = select_portfolio(scores)

    # Correr backtest
    port_returns, port_cumulative = run_backtest(prices, weights)
    bench_returns, bench_cumulative = run_benchmark(prices)

    # Métricas
    port_metrics  = calculate_metrics(port_returns,  "Estratégia Multifator")
    bench_metrics = calculate_metrics(bench_returns, "Benchmark Equal-Weight")

    # Guardar resultados
    results = pd.DataFrame({
        "Portfolio": port_cumulative,
        "Benchmark": bench_cumulative
    })
    results.to_csv("results/backtest_results.csv")
    print("\nResultados guardados em results/backtest_results.csv")