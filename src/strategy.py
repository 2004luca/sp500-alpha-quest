import pandas as pd
import numpy as np

def calculate_momentum(prices, window=252):
    """
    Momentum: retorno dos últimos 12 meses (252 dias de trading).
    Ações que subiram muito têm score alto.
    Excluímos o último mês (21 dias) para evitar efeito de reversão de curto prazo.
    """
    momentum = prices.shift(21).pct_change(window - 21)
    return momentum

def calculate_volatility(prices, window=63):
    """
    Volatilidade: desvio padrão dos retornos diários nos últimos 3 meses (63 dias).
    Usamos o INVERSO — ações mais estáveis têm score mais alto.
    """
    daily_returns = prices.pct_change()
    volatility = daily_returns.rolling(window).std()
    inverse_volatility = 1 / volatility
    return inverse_volatility

def calculate_mean_reversion(prices, window=63):
    """
    Mean Reversion: distância do preço atual à sua média dos últimos 3 meses.
    Se o preço está ABAIXO da média, o score é positivo (esperamos que suba).
    Se o preço está ACIMA da média, o score é negativo (esperamos que desça).
    """
    rolling_mean = prices.rolling(window).mean()
    deviation = (rolling_mean - prices) / rolling_mean
    return deviation

def calculate_combined_score(prices, w_mom=0.4, w_vol=0.3, w_rev=0.3):
    """
    Score final: combinação dos 3 fatores com pesos.
    - Momentum tem peso 40% (fator mais importante)
    - Volatilidade tem peso 30%
    - Mean Reversion tem peso 30%
    Cada fator é normalizado (rank) antes de combinar
    para garantir que estão todos na mesma escala.
    """
    mom  = calculate_momentum(prices)
    vol  = calculate_volatility(prices)
    rev  = calculate_mean_reversion(prices)

    # Normalizar cada fator: converter em rankings entre 0 e 1
    mom_rank = mom.rank(axis=1, pct=True)
    vol_rank = vol.rank(axis=1, pct=True)
    rev_rank = rev.rank(axis=1, pct=True)

    # Score combinado com pesos
    combined = w_mom * mom_rank + w_vol * vol_rank + w_rev * rev_rank
    return combined

def select_portfolio(scores, top_n=50):
    """
    Seleciona as top 50 ações com maior score combinado.
    Aloca peso igual a cada ação selecionada (1/50 = 2% por ação).
    Devolve um DataFrame com os pesos ao longo do tempo.
    """
    # Para cada dia, seleciona as top_n ações
    weights = pd.DataFrame(0.0, index=scores.index, columns=scores.columns)

    for date in scores.index:
        row = scores.loc[date].dropna()
        if len(row) < top_n:
            continue
        top_stocks = row.nlargest(top_n).index
        weights.loc[date, top_stocks] = 1.0 / top_n

    return weights

if __name__ == "__main__":
    # Teste rápido
    prices = pd.read_csv("data/prices.csv", index_col=0, parse_dates=True)
    print("Dados carregados:", prices.shape)

    scores = calculate_combined_score(prices)
    print("Scores calculados:", scores.shape)

    weights = select_portfolio(scores)
    print("Exemplo de pesos (último dia):")
    last = weights.iloc[-1]
    print(last[last > 0])