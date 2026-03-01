📈 1. ANÁLISE TÉCNICA AVANÇADA
core/indicators.py
python
import pandas as pd
import numpy as np
from typing import Dict, List
import talib  # Biblioteca de indicadores técnicos

class AnaliseTecnica:
    """Indicadores técnicos para melhorar as decisões"""
    
    @staticmethod
    def calcular_rsi(precos: List[float], periodo: int = 14) -> float:
        """RSI - Relative Strength Index (sobrecomprado/sobrevendido)"""
        if len(precos) < periodo + 1:
            return 50
        
        # Converte para pandas Series
        series = pd.Series(precos)
        delta = series.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    @staticmethod
    def calcular_macd(precos: List[float]) -> Dict:
        """MACD - Moving Average Convergence Divergence"""
        if len(precos) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        exp1 = pd.Series(precos).ewm(span=12, adjust=False).mean()
        exp2 = pd.Series(precos).ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return {
            'macd': macd.iloc[-1],
            'signal': signal.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    @staticmethod
    def calcular_bandas_bollinger(precos: List[float], periodo: int = 20) -> Dict:
        """Bandas de Bollinger"""
        if len(precos) < periodo:
            return {'superior': precos[-1], 'media': precos[-1], 'inferior': precos[-1]}
        
        series = pd.Series(precos)
        media = series.rolling(window=periodo).mean()
        desvio = series.rolling(window=periodo).std()
        
        banda_superior = media + (desvio * 2)
        banda_inferior = media - (desvio * 2)
        
        return {
            'superior': banda_superior.iloc[-1],
            'media': media.iloc[-1],
            'inferior': banda_inferior.iloc[-1]
        }
    
    @staticmethod
    def calcular_volume_profile(volumes: List[float], precos: List[float], bins: int = 10) -> Dict:
        """Perfil de Volume - áreas de suporte/resistência"""
        if len(precos) < 10:
            return {}
        
        # Cria faixas de preço
        price_range = np.linspace(min(precos), max(precos), bins)
        volume_by_price = {f"{price:.0f}": 0 for price in price_range}
        
        # Distribui volume nas faixas
        for i, price in enumerate(precos):
            idx = np.digitize(price, price_range) - 1
            if 0 <= idx < len(price_range):
                key = f"{price_range[idx]:.0f}"
                volume_by_price[key] += volumes[i] if i < len(volumes) else 0
        
        # Encontra níveis de maior volume (suporte/resistência)
        max_volume_price = max(volume_by_price, key=volume_by_price.get)
        
        return {
            'volume_profile': volume_by_price,
            'ponto_controle': float(max_volume_price)
        }
🎯 2. ESTRATÉGIA DE ENTRADA MELHORADA
core/strategy_avancada.py
python
from core.indicators import AnaliseTecnica
from utils.logger import logger
import numpy as np

class EstrategiaAvancada:
    """Versão melhorada com múltiplos indicadores"""
    
    def __init__(self):
        self.indicators = AnaliseTecnica()
        self.price_history = []
        self.volume_history = []
        self.position = None
        
        # Pesos para cada indicador
        self.pesos = {
            'rsi': 0.20,
            'macd': 0.25,
            'bollinger': 0.25,
            'volume': 0.15,
            'suporte_resistencia': 0.15
        }
        
    def analisar_momento_compra(self, preco_atual: float) -> Dict:
        """Análise multifatorial para decisão de compra"""
        
        if len(self.price_history) < 30:
            return {'decisao': False, 'confianca': 0, 'motivo': 'histórico insuficiente'}
        
        score = 0
        motivos = []
        
        # 1. Análise RSI
        rsi = self.indicators.calcular_rsi(self.price_history)
        if rsi < 30:  # Sobre Vendido
            score += self.pesos['rsi']
            motivos.append(f"RSI oversold: {rsi:.1f}")
        elif rsi < 40:
            score += self.pesos['rsi'] * 0.5
            motivos.append(f"RSI próximo de oversold: {rsi:.1f}")
        
        # 2. Análise MACD
        macd_data = self.indicators.calcular_macd(self.price_history)
        if macd_data['histogram'] > 0 and macd_data['macd'] > macd_data['signal']:
            score += self.pesos['macd']
            motivos.append("MACD com cruzamento positivo")
        
        # 3. Bandas de Bollinger
        bb = self.indicators.calcular_bandas_bollinger(self.price_history)
        if preco_atual <= bb['inferior'] * 1.01:  # Próximo da banda inferior
            score += self.pesos['bollinger']
            motivos.append("Preço na banda inferior de Bollinger")
        elif preco_atual <= bb['media']:
            score += self.pesos['bollinger'] * 0.5
            motivos.append("Preço abaixo da média de Bollinger")
        
        # 4. Análise de Volume
        if len(self.volume_history) > 5:
            volume_medio = np.mean(self.volume_history[-5:])
            volume_atual = self.volume_history[-1] if self.volume_history else 0
            
            if volume_atual > volume_medio * 1.5:  # Volume 50% acima da média
                score += self.pesos['volume']
                motivos.append("Volume acima da média")
        
        # 5. Suporte/Resistência
        if len(self.price_history) > 20:
            suporte = np.percentile(self.price_history[-20:], 20)
            if preco_atual <= suporte * 1.02:  # Próximo do suporte
                score += self.pesos['suporte_resistencia']
                motivos.append("Próximo do nível de suporte")
        
        # Decisão final
        confianca = min(score * 100, 100)  # Converte para porcentagem
        
        return {
            'decisao': score >= 0.6,  # 60% de confiança necessário
            'confianca': confianca,
            'score': score,
            'motivos': motivos,
            'rsi': rsi
        }
    
    def analisar_momento_venda(self, preco_atual: float, preco_compra: float) -> Dict:
        """Análise para decisão de venda"""
        
        if len(self.price_history) < 20:
            return {'decisao': False, 'confianca': 0}
        
        score = 0
        motivos = []
        
        lucro_atual = (preco_atual - preco_compra) / preco_compra * 100
        
        # 1. RSI sobrecomprado
        rsi = self.indicators.calcular_rsi(self.price_history)
        if rsi > 70:  # Sobrecomprado
            score += self.pesos['rsi']
            motivos.append(f"RSI sobrecomprado: {rsi:.1f}")
        
        # 2. Bandas de Bollinger
        bb = self.indicators.calcular_bandas_bollinger(self.price_history)
        if preco_atual >= bb['superior'] * 0.99:  # Próximo da banda superior
            score += self.pesos['bollinger']
            motivos.append("Preço na banda superior")
        
        # 3. Resistência
        if len(self.price_history) > 20:
            resistencia = np.percentile(self.price_history[-20:], 80)
            if preco_atual >= resistencia * 0.98:
                score += self.pesos['suporte_resistencia']
                motivos.append("Próximo da resistência")
        
        # 4. Lucro mínimo garantido
        if lucro_atual >= 3:  # Meta original de 3%
            score += 0.3
            motivos.append(f"Lucro de {lucro_atual:.1f}% atingido")
        
        return {
            'decisao': score >= 0.5 or lucro_atual >= 3,
            'confianca': min(score * 100, 100),
            'score': score,
            'motivos': motivos,
            'lucro': lucro_atual
        }
📊 3. BACKTESTING AUTOMATIZADO
backtest/backtest_engine.py
python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
from typing import List, Dict
import json

class BacktestEngine:
    """Motor de backtesting para testar estratégias"""
    
    def __init__(self, capital_inicial=1000, taxa=0.001):
        self.capital_inicial = capital_inicial
        self.capital = capital_inicial
        self.taxa = taxa
        self.trades = []
        self.metrics = {}
        
    def fetch_historical_data(self, exchange='binance', symbol='BTC/USDT', 
                              timeframe='1h', days=30):
        """Busca dados históricos reais da exchange"""
        exchange_class = getattr(ccxt, exchange)
        exch = exchange_class()
        
        since = exch.parse8601((datetime.now() - timedelta(days=days)).isoformat())
        
        ohlcv = exch.fetch_ohlcv(symbol, timeframe, since=since)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
    
    def run_backtest(self, df: pd.DataFrame, strategy: Dict) -> Dict:
        """
        Executa backtesting com dados históricos
        
        Args:
            df: DataFrame com dados históricos
            strategy: Parâmetros da estratégia
        """
        self.capital = self.capital_inicial
        self.trades = []
        
        position = None
        buy_signals = []
        sell_signals = []
        
        for i in range(len(df)):
            preco = df.iloc[i]['close']
            volume = df.iloc[i]['volume']
            timestamp = df.iloc[i]['timestamp']
            
            # Simula lógica da estratégia
            if position is None:
                # Verifica sinal de compra
                if self._check_buy_signal(df, i, strategy):
                    quantidade = self.capital / preco
                    valor_compra = quantidade * preco
                    taxa_paga = valor_compra * self.taxa
                    
                    position = {
                        'preco': preco,
                        'quantidade': quantidade,
                        'timestamp': timestamp,
                        'taxa': taxa_paga
                    }
                    
                    self.capital -= (valor_compra + taxa_paga)
                    
                    buy_signals.append({
                        'timestamp': timestamp,
                        'preco': preco,
                        'capital': self.capital
                    })
            
            else:
                # Verifica sinal de venda
                if self._check_sell_signal(df, i, position['preco'], strategy):
                    valor_venda = position['quantidade'] * preco
                    taxa_paga = valor_venda * self.taxa
                    
                    self.capital += (valor_venda - taxa_paga)
                    
                    lucro = ((preco - position['preco']) / position['preco']) * 100
                    
                    trade_info = {
                        'compra': position['timestamp'],
                        'venda': timestamp,
                        'preco_compra': position['preco'],
                        'preco_venda': preco,
                        'lucro': lucro,
                        'lucro_abs': valor_venda - (position['quantidade'] * position['preco']),
                        'taxas': position['taxa'] + taxa_paga,
                        'hold_time': (timestamp - position['timestamp']).total_seconds() / 3600
                    }
                    
                    self.trades.append(trade_info)
                    
                    sell_signals.append({
                        'timestamp': timestamp,
                        'preco': preco,
                        'capital': self.capital,
                        'lucro': lucro
                    })
                    
                    position = None
        
        # Calcula métricas
        self._calculate_metrics()
        
        return {
            'capital_final': self.capital,
            'lucro_total': self.capital - self.capital_inicial,
            'rentabilidade': ((self.capital - self.capital_inicial) / self.capital_inicial) * 100,
            'trades': len(self.trades),
            'trades_lucro': len([t for t in self.trades if t['lucro'] > 0]),
            'trades_prejuizo': len([t for t in self.trades if t['lucro'] <= 0]),
            'maior_lucro': max([t['lucro'] for t in self.trades]) if self.trades else 0,
            'maior_prejuizo': min([t['lucro'] for t in self.trades]) if self.trades else 0,
            'lucro_medio': np.mean([t['lucro'] for t in self.trades]) if self.trades else 0,
            'taxas_totais': sum([t['taxas'] for t in self.trades]) if self.trades else 0,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'trades_detalhados': self.trades,
            'metrics': self.metrics
        }
    
    def _calculate_metrics(self):
        """Calcula métricas de performance"""
        if not self.trades:
            return
        
        lucros = [t['lucro'] for t in self.trades]
        
        # Sharpe Ratio simplificado
        retorno_medio = np.mean(lucros)
        desvio_padrao = np.std(lucros)
        
        if desvio_padrao > 0:
            sharpe = (retorno_medio / desvio_padrao) * np.sqrt(252)  # Anualizado
        else:
            sharpe = 0
        
        # Drawdown
        capital_series = [self.capital_inicial]
        for t in self.trades:
            capital_series.append(capital_series[-1] * (1 + t['lucro']/100))
        
        max_capital = capital_series[0]
        drawdowns = []
        
        for cap in capital_series:
            if cap > max_capital:
                max_capital = cap
            drawdown = (cap - max_capital) / max_capital * 100
            drawdowns.append(drawdown)
        
        self.metrics = {
            'sharpe_ratio': sharpe,
            'max_drawdown': min(drawdowns),
            'win_rate': (len([l for l in lucros if l > 0]) / len(lucros)) * 100,
            'avg_win': np.mean([l for l in lucros if l > 0]) if any(l > 0 for l in lucros) else 0,
            'avg_loss': np.mean([l for l in lucros if l < 0]) if any(l < 0 for l in lucros) else 0,
            'profit_factor': abs(sum([l for l in lucros if l > 0]) / sum([l for l in lucros if l < 0])) if any(l < 0 for l in lucros) else float('inf')
        }
    
    def _check_buy_signal(self, df, i, strategy):
        """Implemente sua lógica de compra aqui"""
        if i < 2:
            return False
        
        preco_atual = df.iloc[i]['close']
        preco_anterior = df.iloc[i-1]['close']
        
        queda = (preco_atual - preco_anterior) / preco_anterior * 100
        
        return queda <= strategy.get('buy_threshold', -1)
    
    def _check_sell_signal(self, df, i, preco_compra, strategy):
        """Implemente sua lógica de venda aqui"""
        preco_atual = df.iloc[i]['close']
        
        lucro = (preco_atual - preco_compra) / preco_compra * 100
        
        # Com proteção contra quedas
        if i > 2:
            precos_periodo = df.iloc[max(0, i-10):i]['close']
            preco_minimo = precos_periodo.min()
            queda_maxima = (preco_minimo - preco_compra) / preco_compra * 100
            
            if queda_maxima <= strategy.get('stop_loss', -5):
                # Se teve queda brusca, só vende se lucro > 3%
                return lucro >= strategy.get('sell_threshold', 3)
        
        return lucro >= strategy.get('sell_threshold', 3)
💹 4. GESTÃO DE RISCO AVANÇADA
risk/risk_manager.py
python
from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta

class RiskManager:
    """Gerenciador de risco profissional"""
    
    def __init__(self, capital_inicial: float):
        self.capital_inicial = capital_inicial
        self.capital_atual = capital_inicial
        self.max_drawdown = 0
        self.peak_capital = capital_inicial
        self.consecutive_losses = 0
        self.daily_trades = 0
        self.last_reset = datetime.now()
        
        # Limites
        self.max_daily_trades = 5
        self.max_consecutive_losses = 3
        self.max_daily_loss = capital_inicial * 0.05  # 5% ao dia
        self.max_weekly_loss = capital_inicial * 0.15  # 15% na semana
        
        # Histórico
        self.trade_history = []
        self.daily_pnl = {}
        
    def check_trade_allowed(self, trade_value: float) -> Dict:
        """
        Verifica se o trade pode ser executado baseado em múltiplos fatores
        """
        self._reset_daily_counters()
        
        reasons = []
        allowed = True
        
        # 1. Limite diário de trades
        if self.daily_trades >= self.max_daily_trades:
            allowed = False
            reasons.append(f"Limite diário de {self.max_daily_trades} trades atingido")
        
        # 2. Perdas consecutivas
        if self.consecutive_losses >= self.max_consecutive_losses:
            allowed = False
            reasons.append(f"{self.consecutive_losses} perdas consecutivas - pausa forçada")
        
        # 3. Drawdown máximo
        current_drawdown = (self.peak_capital - self.capital_atual) / self.peak_capital * 100
        if current_drawdown > 10:  # 10% de drawdown
            allowed = False
            reasons.append(f"Drawdown de {current_drawdown:.1f}% - reduzindo posição")
        
        # 4. Tamanho da posição (não arriscar mais que 2% do capital)
        max_position_size = self.capital_atual * 0.02
        if trade_value > max_position_size:
            allowed = False
            reasons.append(f"Posição de R$ {trade_value:.2f} excede 2% do capital")
        
        # 5. Horário de trading (evitar noturno se quiser)
        hora_atual = datetime.now().hour
        if hora_atual < 9 or hora_atual > 18:  # Fora do horário comercial
            if self.capital_atual < self.capital_inicial * 1.1:  # Só se estiver no lucro
                allowed = False
                reasons.append("Fora do horário recomendado")
        
        return {
            'allowed': allowed,
            'reasons': reasons,
            'risk_score': self._calculate_risk_score(),
            'suggested_position': min(trade_value, self.capital_atual * 0.02)
        }
    
    def register_trade(self, trade_result: Dict):
        """Registra resultado do trade para análise de risco"""
        
        self.trade_history.append(trade_result)
        self.daily_trades += 1
        
        # Atualiza capital
        self.capital_atual += trade_result.get('pnl', 0)
        
        # Atualiza peak capital
        if self.capital_atual > self.peak_capital:
            self.peak_capital = self.capital_atual
        
        # Atualiza perdas consecutivas
        if trade_result.get('pnl', 0) < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Registra PnL diário
        today = datetime.now().date()
        if today not in self.daily_pnl:
            self.daily_pnl[today] = 0
        self.daily_pnl[today] += trade_result.get('pnl', 0)
    
    def _reset_daily_counters(self):
        """Reseta contadores diários"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_trades = 0
            self.last_reset = now
    
    def _calculate_risk_score(self) -> float:
        """Calcula score de risco atual (0-100)"""
        score = 0
        
        # Drawdown atual
        drawdown = (self.peak_capital - self.capital_atual) / self.peak_capital * 100
        if drawdown > 5:
            score += 30
        elif drawdown > 2:
            score += 15
        
        # Perdas consecutivas
        score += self.consecutive_losses * 10
        
        # Volatilidade recente
        if len(self.trade_history) >= 5:
            recent_trades = self.trade_history[-5:]
            volatility = np.std([t.get('pnl', 0) for t in recent_trades])
            if volatility > self.capital_atual * 0.01:
                score += 20
        
        return min(score, 100)
    
    def get_risk_report(self) -> Dict:
        """Gera relatório de risco"""
        return {
            'capital_atual': self.capital_atual,
            'peak_capital': self.peak_capital,
            'drawdown': (self.peak_capital - self.capital_atual) / self.peak_capital * 100,
            'consecutive_losses': self.consecutive_losses,
            'daily_trades': self.daily_trades,
            'risk_score': self._calculate_risk_score(),
            'total_trades': len(self.trade_history),
            'win_rate': len([t for t in self.trade_history if t.get('pnl', 0) > 0]) / len(self.trade_history) * 100 if self.trade_history else 0,
            'avg_trade': np.mean([t.get('pnl', 0) for t in self.trade_history]) if self.trade_history else 0
        }
🌐 5. SUPORTE A MÚLTIPLAS EXCHANGES E ARBITRAGEM
arbitrage/arbitrage_scanner.py
python
import ccxt
from typing import Dict, List
import asyncio
import threading
import time

class ArbitrageScanner:
    """Scanner de oportunidades de arbitragem entre exchanges"""
    
    def __init__(self):
        self.exchanges = {}
        self.prices = {}
        self.opportunities = []
        
    def add_exchange(self, exchange_id: str, api_key: str = None, secret: str = None):
        """Adiciona exchange ao scanner"""
        exchange_class = getattr(ccxt, exchange_id)
        
        if api_key and secret:
            exchange = exchange_class({
                'apiKey': api_key,
                'secret': secret,
                'enableRateLimit': True
            })
        else:
            exchange = exchange_class({'enableRateLimit': True})
        
        self.exchanges[exchange_id] = exchange
    
    def scan_prices(self, symbol: str = 'BTC/USDT'):
        """Escaneia preços em todas as exchanges"""
        prices = {}
        
        for name, exchange in self.exchanges.items():
            try:
                ticker = exchange.fetch_ticker(symbol)
                prices[name] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last'],
                    'timestamp': ticker['timestamp']
                }
            except Exception as e:
                print(f"Erro ao buscar {name}: {e}")
        
        return prices
    
    def find_arbitrage(self, symbol: str = 'BTC/USDT', min_spread: float = 0.5) -> List[Dict]:
        """
        Encontra oportunidades de arbitragem
        min_spread: spread mínimo em porcentagem
        """
        prices = self.scan_prices(symbol)
        
        opportunities = []
        
        exchanges_list = list(prices.keys())
        
        for i in range(len(exchanges_list)):
            for j in range(i + 1, len(exchanges_list)):
                ex1 = exchanges_list[i]
                ex2 = exchanges_list[j]
                
                if ex1 not in prices or ex2 not in prices:
                    continue
                
                # Oportunidade de comprar barato no ex1 e vender caro no ex2
                buy_price = prices[ex1]['ask']
                sell_price = prices[ex2]['bid']
                
                if buy_price and sell_price:
                    spread = (sell_price - buy_price) / buy_price * 100
                    
                    if spread > min_spread:
                        opportunities.append({
                            'type': 'ARBITRAGEM',
                            'buy_exchange': ex1,
                            'sell_exchange': ex2,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'spread': spread,
                            'profit_potential': spread - 0.2  # Desconta taxas
                        })
                
                # Oportunidade contrária
                buy_price = prices[ex2]['ask']
                sell_price = prices[ex1]['bid']
                
                if buy_price and sell_price:
                    spread = (sell_price - buy_price) / buy_price * 100
                    
                    if spread > min_spread:
                        opportunities.append({
                            'type': 'ARBITRAGEM',
                            'buy_exchange': ex2,
                            'sell_exchange': ex1,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'spread': spread,
                            'profit_potential': spread - 0.2
                        })
        
        # Ordena por maior spread
        opportunities.sort(key=lambda x: x['spread'], reverse=True)
        
        return opportunities
    
    def start_scanner(self, interval: int = 60):
        """Inicia scanner automático"""
        
        def scan_loop():
            while True:
                opportunities = self.find_arbitrage()
                
                if opportunities:
                    print(f"\n🚀 Oportunidades de Arbitragem ({len(opportunities)}):")
                    for opp in opportunities[:3]:  # Top 3
                        print(f"   • Comprar {opp['buy_exchange']} a ${opp['buy_price']:,.2f}")
                        print(f"     Vender {opp['sell_exchange']} a ${opp['sell_price']:,.2f}")
                        print(f"     Spread: {opp['spread']:.2f}% | Potencial: {opp['profit_potential']:.2f}%")
                
                time.sleep(interval)
        
        thread = threading.Thread(target=scan_loop, daemon=True)
        thread.start()
        
        return thread
🤖 6. MODO DE TREINAMENTO COM APRENDIZADO
ml/trainer.py
python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from datetime import datetime, timedelta
import ccxt

class MLTrainer:
    """Treina modelo de ML para melhorar decisões do bot"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.features = []
        self.labels = []
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara features para o modelo"""
        features = pd.DataFrame()
        
        # Preços e retornos
        features['price'] = df['close']
        features['returns_1h'] = df['close'].pct_change(1)
        features['returns_6h'] = df['close'].pct_change(6)
        features['returns_24h'] = df['close'].pct_change(24)
        
        # Volatilidade
        features['volatility_6h'] = df['close'].pct_change().rolling(6).std()
        features['volatility_24h'] = df['close'].pct_change().rolling(24).std()
        
        # Volume
        features['volume'] = df['volume']
        features['volume_ratio'] = df['volume'] / df['volume'].rolling(24).mean()
        
        # Indicadores técnicos
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        features['macd'] = exp1 - exp2
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_histogram'] = features['macd'] - features['macd_signal']
        
        # Bandas de Bollinger
        sma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        features['bb_upper'] = sma + (std * 2)
        features['bb_lower'] = sma - (std * 2)
        features['bb_position'] = (df['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        return features.dropna()
    
    def prepare_labels(self, df: pd.DataFrame, lookahead: int = 6) -> pd.Series:
        """
        Prepara labels: 1 se preço subir mais que 1% nas próximas 'lookahead' horas
        """
        future_returns = df['close'].shift(-lookahead) / df['close'] - 1
        labels = (future_returns > 0.01).astype(int)  # 1 se subir mais que 1%
        
        return labels
    
    def train(self, df: pd.DataFrame):
        """Treina modelo com dados históricos"""
        
        # Prepara dados
        features = self.prepare_features(df)
        labels = self.prepare_labels(df)
        
        # Alinha dados
        combined = pd.concat([features, labels], axis=1).dropna()
        X = combined.iloc[:, :-1]
        y = combined.iloc[:, -1]
        
        # Split treino/teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Treina modelo
        self.model.fit(X_train, y_train)
        
        # Avalia
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"📊 Acurácia do modelo: {accuracy:.2%}")
        
        # Importância das features
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n📈 Features mais importantes:")
        print(feature_importance.head(10))
        
        return accuracy
    
    def predict(self, features: pd.DataFrame) -> float:
        """Faz predição para o próximo movimento"""
        proba = self.model.predict_proba(features)[0]
        return proba[1]  # Probabilidade de subir
    
    def save_model(self, path: str):
        """Salva modelo treinado"""
        joblib.dump(self.model, path)
    
    def load_model(self, path: str):
        """Carrega modelo salvo"""
        self.model = joblib.load(path)


        
📱 7. APP MOBILE PARA MONITORAMENTO (continuação)
mobile/telegram_advanced.py (completo)
python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import matplotlib.pyplot as plt
import io
import pandas as pd
from datetime import datetime, timedelta

class TelegramBotAdvanced:
    """Bot do Telegram avançado para controle remoto"""
    
    def __init__(self, token: str, trading_bot):
        self.token = token
        self.trading_bot = trading_bot
        self.application = None
        self.authorized_users = []  # Lista de user_ids autorizados
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Menu principal"""
        user_id = update.effective_user.id
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Status Geral", callback_data='status'),
                InlineKeyboardButton("💰 Capital", callback_data='capital'),
            ],
            [
                InlineKeyboardButton("📈 Lucros Hoje", callback_data='profits_today'),
                InlineKeyboardButton("📊 Relatório Mensal", callback_data='report_month'),
            ],
            [
                InlineKeyboardButton("🛑 Parar Bot", callback_data='stop_bot'),
                InlineKeyboardButton("▶️ Iniciar Bot", callback_data='start_bot'),
            ],
            [
                InlineKeyboardButton("⚙️ Configurações", callback_data='config_menu'),
                InlineKeyboardButton("📉 Gráfico Preços", callback_data='chart_price'),
            ],
            [
                InlineKeyboardButton("🛡️ Proteção Ativa", callback_data='protection_status'),
                InlineKeyboardButton("🎯 Ajustar Estratégia", callback_data='adjust_strategy'),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 *Bot de Trading - Controle Remoto*\n\n"
            "Escolha uma opção abaixo:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa cliques nos botões"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'status':
            await self.show_status(query)
        elif query.data == 'capital':
            await self.show_capital(query)
        elif query.data == 'profits_today':
            await self.show_profits_today(query)
        elif query.data == 'report_month':
            await self.show_monthly_report(query)
        elif query.data == 'stop_bot':
            await self.stop_bot(query)
        elif query.data == 'start_bot':
            await self.start_bot(query)
        elif query.data == 'config_menu':
            await self.show_config_menu(query)
        elif query.data == 'chart_price':
            await self.send_price_chart(query)
        elif query.data == 'protection_status':
            await self.show_protection_status(query)
        elif query.data == 'adjust_strategy':
            await self.adjust_strategy_menu(query)
    
    async def show_status(self, query):
        """Mostra status completo do bot"""
        bot = self.trading_bot
        
        # Coleta dados
        capital = bot.capital_atual if hasattr(bot, 'capital_atual') else 0
        posicao = "📌 Em posição" if bot.strategy.position else "💤 Aguardando"
        trades_hoje = bot.strategy.daily_trades if hasattr(bot.strategy, 'daily_trades') else 0
        lucro_hoje = self.calcular_lucro_hoje()
        
        # Preço atual
        preco_atual = "Buscando..."
        try:
            ticker = bot.exchange.get_ticker()
            if ticker:
                preco_atual = f"R$ {ticker['last']:,.2f}"
        except:
            pass
        
        message = (
            f"🤖 *STATUS DO BOT*\n\n"
            f"💰 Capital: R$ {capital:.2f}\n"
            f"📊 Posição: {posicao}\n"
            f"📈 Preço BTC: {preco_atual}\n"
            f"📊 Trades hoje: {trades_hoje}\n"
            f"💵 Lucro hoje: R$ {lucro_hoje:+.2f}\n"
            f"🛡️ Proteção: {'✅ Ativa' if bot.strategy.position and bot.strategy.position.get('lowest_price', 0) < bot.strategy.position['buy_price'] else '⚪ Normal'}\n"
            f"⏰ Última atualização: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_capital(self, query):
        """Mostra detalhes do capital"""
        bot = self.trading_bot
        
        capital_inicial = 1000  # Pega do config
        capital_atual = bot.capital_atual if hasattr(bot, 'capital_atual') else capital_inicial
        
        lucro_total = capital_atual - capital_inicial
        percentual = (lucro_total / capital_inicial) * 100
        
        # Projeções
        projecao_mes = capital_atual * (1 + percentual/100) ** 30
        projecao_ano = capital_atual * (1 + percentual/100) ** 365
        
        message = (
            f"💰 *DETALHES DO CAPITAL*\n\n"
            f"Capital Inicial: R$ {capital_inicial:.2f}\n"
            f"Capital Atual: R$ {capital_atual:.2f}\n"
            f"Lucro/Prejuízo: R$ {lucro_total:+.2f}\n"
            f"Rentabilidade: {percentual:+.2f}%\n\n"
            f"📈 *Projeções:*\n"
            f"• Próximo mês: R$ {projecao_mes:.2f}\n"
            f"• Próximo ano: R$ {projecao_ano:.2f}\n\n"
            f"⚖️ *Risco:*\n"
            f"• Drawdown atual: {self.calcular_drawdown():.2f}%\n"
            f"• Trades com lucro: {self.calcular_win_rate():.1f}%"
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def send_price_chart(self, query):
        """Envia gráfico de preços"""
        try:
            # Coleta dados históricos
            bot = self.trading_bot
            df = bot.exchange.fetch_ohlcv('BTC/USDT', '1h', limit=48)
            
            if df is not None:
                # Cria gráfico
                plt.figure(figsize=(10, 6))
                plt.plot(df['timestamp'], df['close'], 'b-', linewidth=2)
                plt.title('BTC/USDT - Últimas 48 horas')
                plt.xlabel('Hora')
                plt.ylabel('Preço (R$)')
                plt.grid(True, alpha=0.3)
                
                # Adiciona linhas de suporte/resistência
                plt.axhline(y=df['close'].mean(), color='r', linestyle='--', alpha=0.5, label='Média')
                
                # Salva em memória
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                plt.close()
                
                # Envia foto
                await query.message.reply_photo(photo=buf, caption="📊 Gráfico BTC/USDT - Últimas 48h")
                
                keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("✅ Gráfico enviado!", reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ Erro ao gerar gráfico")
                
        except Exception as e:
            await query.edit_message_text(f"❌ Erro: {str(e)}")
    
    async def show_protection_status(self, query):
        """Mostra status da proteção contra quedas"""
        bot = self.trading_bot
        
        if not bot.strategy.position:
            message = "🛡️ *PROTEÇÃO*\n\nSem posição aberta no momento."
        else:
            pos = bot.strategy.position
            preco_compra = pos['buy_price']
            preco_minimo = pos.get('lowest_price', preco_compra)
            
            queda = (preco_minimo - preco_compra) / preco_compra * 100
            
            message = (
                f"🛡️ *STATUS DA PROTEÇÃO*\n\n"
                f"Preço de compra: R$ {preco_compra:,.2f}\n"
                f"Preço mínimo: R$ {preco_minimo:,.2f}\n"
                f"Queda máxima: {queda:.2f}%\n\n"
            )
            
            if queda <= -5:
                message += "⚠️ *PROTEÇÃO ATIVADA!*\n"
                message += "Bot está segurando posição até recuperar +3%."
                message += f"\n\nPreço alvo: R$ {preco_compra * 1.03:,.2f}"
            else:
                message += "✅ Proteção em standby (sem queda brusca)"
        
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def adjust_strategy_menu(self, query):
        """Menu para ajustar estratégia"""
        keyboard = [
            [InlineKeyboardButton("📉 Ajustar -1%", callback_data='adj_buy')],
            [InlineKeyboardButton("📈 Ajustar +3%", callback_data='adj_sell')],
            [InlineKeyboardButton("🛑 Ajustar Stop -5%", callback_data='adj_stop')],
            [InlineKeyboardButton("📊 Limite de trades", callback_data='adj_trades')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ *AJUSTAR ESTRATÉGIA*\n\n"
            "Selecione o parâmetro para ajustar:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def calcular_lucro_hoje(self):
        """Calcula lucro do dia"""
        # Implementar lógica
        return 0.0
    
    def calcular_drawdown(self):
        """Calcula drawdown atual"""
        # Implementar lógica
        return 0.0
    
    def calcular_win_rate(self):
        """Calcula taxa de acerto"""
        # Implementar lógica
        return 0.0
    
    async def stop_bot(self, query):
        """Para o bot"""
        self.trading_bot.running = False
        await query.edit_message_text("🛑 Bot parado com sucesso!")
    
    async def start_bot(self, query):
        """Inicia o bot"""
        self.trading_bot.running = True
        await query.edit_message_text("▶️ Bot iniciado com sucesso!")
    
    async def show_config_menu(self, query):
        """Menu de configurações"""
        keyboard = [
            [InlineKeyboardButton("💰 Ajustar capital", callback_data='config_capital')],
            [InlineKeyboardButton("🔔 Notificações", callback_data='config_notify')],
            [InlineKeyboardButton("🌙 Modo noturno", callback_data='config_night')],
            [InlineKeyboardButton("🔙 Voltar", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("⚙️ Configurações", reply_markup=reply_markup)
    
    def run(self):
        """Inicia o bot do Telegram"""
        self.application = Application.builder().token(self.token).build()
        
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        print("✅ Bot do Telegram iniciado!")
        self.application.run_polling()
        
        
        
💾 8. BANCO DE DADOS E PERSISTÊNCIA
database/db_manager.py
python
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import pandas as pd

class DatabaseManager:
    """Gerenciador de banco de dados SQLite"""
    
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa tabelas do banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                type TEXT,
                price REAL,
                quantity REAL,
                value REAL,
                fee REAL,
                profit_percentage REAL,
                profit_abs REAL,
                strategy_params TEXT
            )
        ''')
        
        # Tabela de capital histórico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capital_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                capital REAL,
                btc_price REAL
            )
        ''')
        
        # Tabela de configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME
            )
        ''')
        
        # Tabela de alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                type TEXT,
                message TEXT,
                read BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_trade(self, trade_data: Dict):
        """Salva um trade no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades 
            (timestamp, type, price, quantity, value, fee, profit_percentage, profit_abs, strategy_params)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            trade_data.get('type', ''),
            trade_data.get('price', 0),
            trade_data.get('quantity', 0),
            trade_data.get('value', 0),
            trade_data.get('fee', 0),
            trade_data.get('profit_percentage', 0),
            trade_data.get('profit_abs', 0),
            json.dumps(trade_data.get('strategy_params', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def save_capital_snapshot(self, capital: float, btc_price: float):
        """Salva snapshot do capital"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO capital_history (timestamp, capital, btc_price)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), capital, btc_price))
        
        conn.commit()
        conn.close()
    
    def get_trade_history(self, days: int = 30) -> pd.DataFrame:
        """Retorna histórico de trades como DataFrame"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT * FROM trades 
            WHERE timestamp >= date('now', '-{days} days')
            ORDER BY timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_capital_history(self, days: int = 30) -> pd.DataFrame:
        """Retorna histórico de capital"""
        conn = sqlite3.connect(self.db_path)
        
        query = f'''
            SELECT * FROM capital_history 
            WHERE timestamp >= date('now', '-{days} days')
            ORDER BY timestamp
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def save_setting(self, key: str, value: str):
        """Salva configuração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default=None):
        """Recupera configuração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else default
    
    def add_alert(self, alert_type: str, message: str):
        """Adiciona alerta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (timestamp, type, message)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), alert_type, message))
        
        conn.commit()
        conn.close()
    
    def get_unread_alerts(self) -> List[Dict]:
        """Retorna alertas não lidos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts WHERE read = 0 ORDER BY timestamp DESC
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'timestamp': row[1],
                'type': row[2],
                'message': row[3]
            })
        
        conn.close()
        return alerts
    
    def mark_alert_read(self, alert_id: int):
        """Marca alerta como lido"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE alerts SET read = 1 WHERE id = ?', (alert_id,))
        
        conn.commit()
        conn.close()
        
        
🔄 9. OTIMIZAÇÃO DE PERFORMANCE
optimization/optimizer.py
python
import numpy as np
from typing import Dict, List
import itertools
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

class StrategyOptimizer:
    """Otimizador de parâmetros da estratégia"""
    
    def __init__(self, backtest_engine):
        self.backtest = backtest_engine
        self.best_params = {}
        self.best_result = -float('inf')
        
    def optimize_parameters(self, df, param_grid: Dict, metric='sharpe'):
        """
        Otimiza parâmetros usando grid search
        
        Args:
            df: DataFrame com dados históricos
            param_grid: Dicionário com ranges de parâmetros
            metric: Métrica a otimizar ('sharpe', 'return', 'win_rate')
        """
        # Gera todas as combinações
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = list(itertools.product(*values))
        
        results = []
        
        # Otimização paralela
        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = []
            for combo in combinations:
                params = dict(zip(keys, combo))
                future = executor.submit(self._evaluate_params, df, params, metric)
                futures.append((params, future))
            
            for params, future in futures:
                try:
                    result = future.result(timeout=30)
                    results.append({
                        'params': params,
                        'metrics': result
                    })
                    
                    if result.get(metric, 0) > self.best_result:
                        self.best_result = result.get(metric, 0)
                        self.best_params = params
                        
                    print(f"✅ Testado: {params} -> {metric}: {result.get(metric, 0):.3f}")
                except Exception as e:
                    print(f"❌ Erro: {e}")
        
        return {
            'best_params': self.best_params,
            'best_result': self.best_result,
            'all_results': sorted(results, key=lambda x: x['metrics'].get(metric, 0), reverse=True)
        }
    
    def _evaluate_params(self, df, params: Dict, metric: str) -> Dict:
        """Avalia um conjunto de parâmetros"""
        result = self.backtest.run_backtest(df, params)
        return result.get('metrics', {})
    
    def walk_forward_optimization(self, df, param_grid: Dict, 
                                   train_size: int = 500, 
                                   test_size: int = 100):
        """
        Walk-forward optimization para evitar overfitting
        """
        results = []
        
        for i in range(0, len(df) - train_size - test_size, test_size):
            train_df = df.iloc[i:i+train_size]
            test_df = df.iloc[i+train_size:i+train_size+test_size]
            
            # Otimiza no treino
            opt_result = self.optimize_parameters(train_df, param_grid)
            best_params = opt_result['best_params']
            
            # Testa no período seguinte
            test_result = self.backtest.run_backtest(test_df, best_params)
            
            results.append({
                'period': i,
                'train_params': best_params,
                'test_result': test_result
            })
            
            print(f"Período {i}: Train -> Test: {test_result.get('rentabilidade', 0):.2f}%")
        
        return results

class ParameterSuggestion:
    """Sugere parâmetros baseado em análise de mercado"""
    
    @staticmethod
    def suggest_based_on_volatility(df) -> Dict:
        """Sugere parâmetros baseado na volatilidade atual"""
        
        # Calcula volatilidade recente
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(24)  # Volatilidade diária
        
        suggestions = {
            'low_volatility': {
                'buy_threshold': -0.5,
                'sell_threshold': 1.5,
                'stop_loss': -2.0
            },
            'medium_volatility': {
                'buy_threshold': -1.0,
                'sell_threshold': 3.0,
                'stop_loss': -5.0
            },
            'high_volatility': {
                'buy_threshold': -2.0,
                'sell_threshold': 5.0,
                'stop_loss': -8.0
            }
        }
        
        if volatility < 0.02:  # Baixa volatilidade
            regime = 'low_volatility'
        elif volatility < 0.04:  # Média volatilidade
            regime = 'medium_volatility'
        else:  # Alta volatilidade
            regime = 'high_volatility'
        
        return {
            'regime': regime,
            'volatility': volatility,
            'suggested_params': suggestions[regime]
        }
🧪 10. MODO PAPER TRADING AVANÇADO
paper_trading/simulator.py
python
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

class PaperTradingSimulator:
    """
    Simulador avançado de trading com cenários realistas
    """
    
    def __init__(self, capital_inicial=1000):
        self.capital_inicial = capital_inicial
        self.capital = capital_inicial
        self.positions = []
        self.trades = []
        self.scenario = 'normal'  # normal, crash, pump, lateral
        
    def set_scenario(self, scenario: str):
        """Define cenário de mercado para simulação"""
        valid_scenarios = ['normal', 'crash', 'pump', 'lateral', 'volatile']
        if scenario in valid_scenarios:
            self.scenario = scenario
            print(f"📊 Cenário definido: {scenario.upper()}")
    
    def generate_price_series(self, hours: int = 168) -> List[Dict]:
        """
        Gera série de preços realista baseada no cenário
        """
        prices = []
        current_price = 350000  # Preço inicial BTC
        
        for hour in range(hours):
            timestamp = datetime.now() + timedelta(hours=hour)
            
            # Define volatilidade baseada no cenário
            if self.scenario == 'normal':
                volatility = 0.01  # 1% de variação
                trend = 0.0002  # Leve tendência de alta
            elif self.scenario == 'crash':
                volatility = 0.03
                trend = -0.001  # Tendência de queda
            elif self.scenario == 'pump':
                volatility = 0.03
                trend = 0.001  # Tendência de alta forte
            elif self.scenario == 'lateral':
                volatility = 0.003  # Variação muito baixa
                trend = 0
            else:  # volatile
                volatility = 0.05  # Altíssima volatilidade
                trend = random.choice([-0.001, 0.001])
            
            # Gera variação
            change = np.random.normal(trend, volatility)
            current_price *= (1 + change)
            
            # Adiciona eventos extremos ocasionais
            if random.random() < 0.02:  # 2% de chance de evento
                if self.scenario == 'crash':
                    current_price *= 0.95  # Queda de 5%
                elif self.scenario == 'pump':
                    current_price *= 1.05  # Alta de 5%
            
            prices.append({
                'timestamp': timestamp,
                'price': current_price,
                'volume': random.uniform(100, 1000) * current_price / 1000
            })
        
        return prices
    
    async def run_simulation(self, strategy, hours: int = 168):
        """
        Executa simulação com a estratégia
        """
        price_series = self.generate_price_series(hours)
        
        print(f"\n🚀 INICIANDO PAPER TRADING - {hours} horas")
        print(f"💰 Capital inicial: R$ {self.capital:.2f}")
        print(f"📊 Cenário: {self.scenario.upper()}\n")
        
        for hour, data in enumerate(price_series):
            price = data['price']
            timestamp = data['timestamp']
            
            # Executa estratégia
            if not strategy.position:
                # Verifica compra
                if strategy.should_buy(price):
                    strategy.execute_buy(price)
                    self.positions.append({
                        'buy_price': price,
                        'buy_time': timestamp,
                        'quantity': self.capital / price
                    })
                    self.capital = 0
                    
                    print(f"🟢 [{timestamp.strftime('%d/%m %H:%M')}] COMPRA @ R$ {price:,.2f}")
            
            else:
                # Verifica venda
                if strategy.should_sell(price):
                    result = strategy.execute_sell(price)
                    self.capital = result['capital_atual'] if 'capital_atual' in result else self.capital
                    
                    print(f"🔴 [{timestamp.strftime('%d/%m %H:%M')}] VENDA @ R$ {price:,.2f} | Lucro: {result['profit_percentage']:.2f}%")
                    
                    self.trades.append(result)
            
            # Mostra progresso
            if hour % 24 == 0 and hour > 0:
                dia = hour // 24
                print(f"\n📅 Dia {dia} - Capital: R$ {self.capital if self.capital > 0 else self.positions[-1]['buy_price'] * self.positions[-1]['quantity']:.2f}")
        
        # Relatório final
        self.generate_report()
    
    def generate_report(self):
        """Gera relatório da simulação"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO PAPER TRADING")
        print("="*60)
        
        if self.trades:
            df_trades = pd.DataFrame(self.trades)
            
            print(f"\n📈 Estatísticas:")
            print(f"   Total de trades: {len(self.trades)}")
            print(f"   Trades com lucro: {len(df_trades[df_trades['profit_percentage'] > 0])}")
            print(f"   Trades com prejuízo: {len(df_trades[df_trades['profit_percentage'] <= 0])}")
            print(f"   Lucro médio: {df_trades['profit_percentage'].mean():.2f}%")
            print(f"   Maior lucro: {df_trades['profit_percentage'].max():.2f}%")
            print(f"   Maior prejuízo: {df_trades['profit_percentage'].min():.2f}%")
            
            # Calcula capital final
            capital_final = self.capital if self.capital > 0 else self.positions[-1]['buy_price'] * self.positions[-1]['quantity']
            lucro_total = capital_final - self.capital_inicial
            
            print(f"\n💰 Resultado Financeiro:")
            print(f"   Capital inicial: R$ {self.capital_inicial:.2f}")
            print(f"   Capital final: R$ {capital_final:.2f}")
            print(f"   Lucro/Prejuízo: R$ {lucro_total:+.2f}")
            print(f"   Rentabilidade: {(lucro_total/self.capital_inicial)*100:+.2f}%")
        else:
            print("Nenhum trade executado na simulação")
📦 11. ARQUIVO DE CONFIGURAÇÃO COMPLETO
config/advanced_settings.py
python
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class AdvancedSettings:
    """Configurações avançadas do bot"""
    
    # Trading
    symbol: str = "BTC/USDT"
    base_currency: str = "USDT"
    trade_quantity: float = 0.001
    
    # Estratégia Principal
    buy_threshold: float = -1.0  # %
    sell_threshold: float = 3.0   # %
    stop_loss: float = -5.0        # %
    
    # Proteção Avançada
    enable_dynamic_stop: bool = True
    trailing_stop: bool = True
    trailing_distance: float = 1.0  # %
    protection_trigger: float = -5.0  # Ativa proteção após queda de 5%
    
    # Limites
    max_daily_trades: int = 10
    max_consecutive_losses: int = 3
    max_drawdown: float = 15.0  # %
    min_volume_btc: float = 100  # Volume mínimo em BTC
    
    # Indicadores Técnicos
    use_rsi: bool = True
    rsi_period: int = 14
    rsi_oversold: int = 30
    rsi_overbought: int = 70
    
    use_macd: bool = True
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    use_bollinger: bool = True
    bb_period: int = 20
    bb_std: float = 2.0
    
    # Timeframes
    primary_timeframe: str = "1h"
    secondary_timeframe: str = "15m"
    analysis_periods: int = 100
    
    # Risk Management
    risk_per_trade: float = 2.0  # % do capital por trade
    max_position_size: float = 10.0  # % do capital máximo em posição
    use_kelly_criterion: bool = False
    
    # Notifications
    notify_on_trade: bool = True
    notify_on_drawdown: bool = True
    notify_daily_report: bool = True
    notify_time: str = "20:00"
    
    # Advanced Features
    use_ml_predictions: bool = False
    ml_model_path: Optional[str] = None
    
    enable_arbitrage: bool = False
    arbitrage_exchanges: list = None
    
    use_hedging: bool = False
    hedge_ratio: float = 0.3  # 30% hedge em stablecoins
    
    # Database
    save_trades: bool = True
    save_capital_history: bool = True
    save_signals: bool = False
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def save_to_file(self, filename: str = "config.json"):
        """Salva configurações em arquivo"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
    
    @classmethod
    def load_from_file(cls, filename: str = "config.json"):
        """Carrega configurações de arquivo"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except FileNotFoundError:
            return cls()


🚀 12. MAIN ATUALIZADO COM TODAS AS MELHORIAS (continuação)
main_advanced.py (completo)
python
#!/usr/bin/env python3
"""
Bot de Trading Avançado - Versão Completa
Com todas as melhorias implementadas
"""

import asyncio
import argparse
import signal
import sys
import threading
from pathlib import Path
from datetime import datetime
import time

# Importações avançadas
from core.trader import TradingBot
from core.strategy_avancada import EstrategiaAvancada
from core.indicators import AnaliseTecnica
from risk.risk_manager import RiskManager
from database.db_manager import DatabaseManager
from mobile.telegram_advanced import TelegramBotAdvanced
from paper_trading.simulator import PaperTradingSimulator
from config.advanced_settings import AdvancedSettings
from optimization.optimizer import StrategyOptimizer, ParameterSuggestion
from backtest.backtest_engine import BacktestEngine
from arbitrage.arbitrage_scanner import ArbitrageScanner
from ml.trainer import MLTrainer
from utils.logger import logger

class AdvancedTradingBot:
    """Versão avançada do bot com todas as funcionalidades"""
    
    def __init__(self):
        # Carrega configurações
        self.settings = AdvancedSettings.load_from_file()
        
        # Inicializa componentes core
        self.db = DatabaseManager()
        self.risk_manager = RiskManager(self.settings.trade_quantity * 350000)
        self.strategy = EstrategiaAvancada()
        self.indicators = AnaliseTecnica()
        self.backtest = BacktestEngine()
        self.paper_trading = PaperTradingSimulator()
        
        # Componentes opcionais
        self.telegram = None
        self.ml_trainer = None
        self.arbitrage = None
        self.optimizer = None
        
        # Status
        self.running = False
        self.mode = 'real'  # real, paper, backtest
        self.start_time = None
        
        # Threads
        self.threads = []
        
        logger.info("🚀 Bot Avançado inicializado com sucesso!")
        self._print_banner()
    
    def _print_banner(self):
        """Mostra banner de inicialização"""
        print("""
        ╔══════════════════════════════════════════════════════════╗
        ║     🤖 BOT DE TRADING AVANÇADO - VERSÃO COMPLETA        ║
        ║                                                          ║
        ║     🎯 Estratégia: -1% / +3% com Proteção               ║
        ║     🛡️ Risk Management Ativo                            ║
        ║     📊 Análise Técnica + ML                             ║
        ║     💹 Arbitragem entre Exchanges                       ║
        ║     📱 Controle via Telegram                            ║
        ║     💾 Banco de Dados SQLite                            ║
        ╚══════════════════════════════════════════════════════════╝
        """)
    
    def initialize_telegram(self, token: str):
        """Inicializa bot do Telegram"""
        try:
            self.telegram = TelegramBotAdvanced(token, self)
            telegram_thread = threading.Thread(target=self.telegram.run, daemon=True)
            telegram_thread.start()
            self.threads.append(telegram_thread)
            logger.info("✅ Telegram bot inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Telegram: {e}")
    
    def initialize_ml(self):
        """Inicializa módulo de Machine Learning"""
        try:
            self.ml_trainer = MLTrainer()
            if self.settings.ml_model_path:
                self.ml_trainer.load_model(self.settings.ml_model_path)
            logger.info("✅ ML Trainer inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar ML: {e}")
    
    def initialize_arbitrage(self):
        """Inicializa scanner de arbitragem"""
        try:
            self.arbitrage = ArbitrageScanner()
            # Adiciona exchanges principais
            self.arbitrage.add_exchange('binance')
            self.arbitrage.add_exchange('bybit')
            self.arbitrage.add_exchange('kraken')
            self.arbitrage.add_exchange('coinbase')
            
            # Inicia scanner automático
            scanner_thread = threading.Thread(
                target=self.arbitrage.start_scanner, 
                args=(60,), 
                daemon=True
            )
            scanner_thread.start()
            self.threads.append(scanner_thread)
            logger.info("✅ Arbitrage Scanner inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar arbitragem: {e}")
    
    def initialize_optimizer(self):
        """Inicializa otimizador de estratégia"""
        try:
            self.optimizer = StrategyOptimizer(self.backtest)
            logger.info("✅ Strategy Optimizer inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar optimizer: {e}")
    
    def run_paper_trading(self, days: int = 30):
        """Executa modo paper trading"""
        self.mode = 'paper'
        logger.info(f"📊 Iniciando PAPER TRADING por {days} dias")
        
        # Busca dados históricos
        df = self.backtest.fetch_historical_data(days=days)
        
        # Define cenário
        scenario = input("Escolha cenário (normal/crash/pump/lateral/volatile): ").lower()
        self.paper_trading.set_scenario(scenario if scenario else 'normal')
        
        # Executa simulação
        asyncio.run(self.paper_trading.run_simulation(self.strategy, hours=days*24))
    
    def run_backtest(self, days: int = 90, optimize: bool = False):
        """Executa modo backtesting"""
        self.mode = 'backtest'
        logger.info(f"📊 Iniciando BACKTEST de {days} dias")
        
        # Busca dados históricos
        logger.info("Buscando dados históricos...")
        df = self.backtest.fetch_historical_data(days=days)
        
        if optimize:
            # Otimização de parâmetros
            logger.info("🔍 Iniciando otimização de parâmetros...")
            
            param_grid = {
                'buy_threshold': [-0.5, -1.0, -1.5, -2.0],
                'sell_threshold': [2.0, 2.5, 3.0, 3.5, 4.0],
                'stop_loss': [-3.0, -4.0, -5.0, -6.0, -7.0]
            }
            
            results = self.optimizer.optimize_parameters(df, param_grid, metric='sharpe')
            
            logger.info(f"✅ Melhores parâmetros encontrados:")
            logger.info(f"   {results['best_params']}")
            logger.info(f"   Sharpe Ratio: {results['best_result']:.3f}")
            
            # Usa melhores parâmetros
            strategy_params = results['best_params']
        else:
            # Usa parâmetros atuais
            strategy_params = {
                'buy_threshold': self.settings.buy_threshold,
                'sell_threshold': self.settings.sell_threshold,
                'stop_loss': self.settings.stop_loss
            }
        
        # Executa backtest
        logger.info("Executando backtest...")
        result = self.backtest.run_backtest(df, strategy_params)
        
        # Mostra resultados
        self._show_backtest_results(result)
        
        # Salva no banco
        self.db.save_setting('last_backtest', str(result))
        
        return result
    
    def _show_backtest_results(self, result: dict):
        """Mostra resultados do backtest"""
        print("\n" + "="*60)
        print("📊 RESULTADOS DO BACKTEST")
        print("="*60)
        
        print(f"\n💰 RESULTADO FINANCEIRO:")
        print(f"   Capital Inicial: R$ {self.backtest.capital_inicial:.2f}")
        print(f"   Capital Final: R$ {result['capital_final']:.2f}")
        print(f"   Lucro Total: R$ {result['lucro_total']:+.2f}")
        print(f"   Rentabilidade: {result['rentabilidade']:+.2f}%")
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total de Trades: {result['trades']}")
        print(f"   Trades com Lucro: {result['trades_lucro']}")
        print(f"   Trades com Prejuízo: {result['trades_prejuizo']}")
        print(f"   Win Rate: {result['trades_lucro']/result['trades']*100:.1f}%" if result['trades'] > 0 else "   Win Rate: N/A")
        print(f"   Maior Lucro: {result['maior_lucro']:.2f}%")
        print(f"   Maior Prejuízo: {result['maior_prejuizo']:.2f}%")
        print(f"   Lucro Médio: {result['lucro_medio']:.2f}%")
        
        print(f"\n💸 TAXAS:")
        print(f"   Taxas Totais: R$ {result['taxas_totais']:.2f}")
        print(f"   Taxas como % do Lucro: {(result['taxas_totais']/result['lucro_total'])*100:.1f}%" if result['lucro_total'] > 0 else "   Taxas: N/A")
        
        if 'metrics' in result:
            print(f"\n📊 MÉTRICAS DE RISCO:")
            print(f"   Sharpe Ratio: {result['metrics'].get('sharpe_ratio', 0):.3f}")
            print(f"   Max Drawdown: {result['metrics'].get('max_drawdown', 0):.2f}%")
            print(f"   Profit Factor: {result['metrics'].get('profit_factor', 0):.3f}")
    
    def run_real(self):
        """Executa modo real com dinheiro de verdade"""
        self.mode = 'real'
        logger.warning("⚠️  MODO REAL ATIVADO - DINHEIRO DE VERDADE EM JOGO!")
        
        # Verifica configurações de segurança
        self._check_safety_settings()
        
        # Pergunta confirmação
        response = input("\n❓ TEM CERTEZA QUE DESEJA CONTINUAR? (digite 'SIM' para confirmar): ")
        if response != 'SIM':
            logger.info("Operação cancelada pelo usuário")
            return
        
        # Inicializa componentes
        from core.exchange import ExchangeManager
        self.exchange = ExchangeManager()
        
        # Registra início
        self.start_time = datetime.now()
        self.running = True
        
        # Inicia loop principal
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.shutdown()
    
    def _check_safety_settings(self):
        """Verifica configurações de segurança"""
        logger.info("🔒 Verificando configurações de segurança...")
        
        # Verifica stop loss
        if self.settings.stop_loss >= 0:
            logger.error("❌ STOP LOSS não configurado! Configure um valor negativo.")
            sys.exit(1)
        
        # Verifica limite de trades
        if self.settings.max_daily_trades > 20:
            logger.warning("⚠️ Limite de trades diário muito alto (>20)")
        
        # Verifica tamanho da posição
        if self.settings.trade_quantity * 350000 > self.risk_manager.capital_atual * 0.1:
            logger.warning("⚠️ Posição maior que 10% do capital")
        
        logger.info("✅ Verificações de segurança concluídas")
    
    def _main_loop(self):
        """Loop principal do bot"""
        logger.info("▶️ Iniciando loop principal...")
        
        check_interval = 60  # segundos
        last_snapshot = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # 1. Obtém preço atual
                ticker = self.exchange.get_ticker()
                if not ticker:
                    time.sleep(check_interval)
                    continue
                
                current_price = ticker['last']
                
                # 2. Atualiza indicadores
                self.strategy.update_price_history(current_price)
                
                # 3. Verifica sinais de trading
                if not self.strategy.position:
                    # Análise para compra
                    analysis = self.strategy.analisar_momento_compra(current_price)
                    
                    if analysis['decisao']:
                        logger.info(f"🎯 SINAL DE COMPRA! Confiança: {analysis['confianca']:.1f}%")
                        for motivo in analysis['motivos']:
                            logger.info(f"   • {motivo}")
                        
                        # Verifica risco
                        trade_value = current_price * self.settings.trade_quantity
                        risk_check = self.risk_manager.check_trade_allowed(trade_value)
                        
                        if risk_check['allowed']:
                            order = self.exchange.create_buy_order()
                            if order:
                                position = self.strategy.execute_buy(current_price)
                                
                                # Registra no banco
                                self.db.save_trade({
                                    'type': 'BUY',
                                    'price': current_price,
                                    'quantity': self.settings.trade_quantity,
                                    'value': trade_value,
                                    'fee': trade_value * 0.001,
                                    'strategy_params': analysis
                                })
                                
                                # Snapshot
                                self.db.save_capital_snapshot(
                                    self.risk_manager.capital_atual,
                                    current_price
                                )
                        else:
                            logger.warning(f"⚠️ Trade bloqueado pelo risk manager: {risk_check['reasons']}")
                
                else:
                    # Análise para venda
                    analysis = self.strategy.analisar_momento_venda(
                        current_price, 
                        self.strategy.position['buy_price']
                    )
                    
                    if analysis['decisao']:
                        logger.info(f"🎯 SINAL DE VENDA! Confiança: {analysis['confianca']:.1f}%")
                        for motivo in analysis['motivos']:
                            logger.info(f"   • {motivo}")
                        
                        order = self.exchange.create_sell_order()
                        if order:
                            result = self.strategy.execute_sell(current_price)
                            
                            # Registra trade
                            self.db.save_trade({
                                'type': 'SELL',
                                'price': current_price,
                                'quantity': self.settings.trade_quantity,
                                'value': current_price * self.settings.trade_quantity,
                                'fee': current_price * self.settings.trade_quantity * 0.001,
                                'profit_percentage': result['profit_percentage'],
                                'profit_abs': result['profit_abs'],
                                'strategy_params': analysis
                            })
                            
                            # Registra no risk manager
                            self.risk_manager.register_trade({
                                'pnl': result['profit_abs'],
                                'percentage': result['profit_percentage']
                            })
                            
                            # Snapshot
                            self.db.save_capital_snapshot(
                                self.risk_manager.capital_atual,
                                current_price
                            )
                
                # Snapshot periódico (a cada 15 minutos)
                if current_time - last_snapshot > 900:
                    self.db.save_capital_snapshot(
                        self.risk_manager.capital_atual,
                        current_price
                    )
                    last_snapshot = current_time
                
                # Verifica alerts
                self._check_alerts(current_price)
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop principal: {e}")
                time.sleep(check_interval)
    
    def _check_alerts(self, current_price: float):
        """Verifica condições de alerta"""
        
        # Drawdown alert
        drawdown = self.risk_manager.get_risk_report()['drawdown']
        if drawdown > 10:
            msg = f"⚠️ Drawdown alto: {drawdown:.1f}%"
            logger.warning(msg)
            self.db.add_alert('drawdown', msg)
        
        # Lucro significativo
        if self.strategy.position:
            profit = (current_price - self.strategy.position['buy_price']) / self.strategy.position['buy_price'] * 100
            if profit > 5:
                msg = f"🎯 Lucro de {profit:.1f}% na posição atual"
                logger.info(msg)
                self.db.add_alert('profit', msg)
    
    def generate_report(self):
        """Gera relatório completo de performance"""
        logger.info("📊 Gerando relatório de performance...")
        
        # Busca dados do banco
        trades_df = self.db.get_trade_history(days=30)
        capital_df = self.db.get_capital_history(days=30)
        
        if trades_df.empty:
            logger.info("Nenhum trade encontrado no período")
            return
        
        print("\n" + "="*70)
        print("📈 RELATÓRIO DE PERFORMANCE - 30 DIAS")
        print("="*70)
        
        # Estatísticas de trades
        total_trades = len(trades_df)
        trades_lucro = len(trades_df[trades_df['profit_percentage'] > 0])
        trades_prejuizo = len(trades_df[trades_df['profit_percentage'] <= 0])
        
        print(f"\n📊 ESTATÍSTICAS DE TRADES:")
        print(f"   Total de Trades: {total_trades}")
        print(f"   Trades com Lucro: {trades_lucro} ({trades_lucro/total_trades*100:.1f}%)")
        print(f"   Trades com Prejuízo: {trades_prejuizo} ({trades_prejuizo/total_trades*100:.1f}%)")
        print(f"   Lucro Médio: {trades_df['profit_percentage'].mean():.2f}%")
        print(f"   Maior Lucro: {trades_df['profit_percentage'].max():.2f}%")
        print(f"   Maior Prejuízo: {trades_df['profit_percentage'].min():.2f}%")
        
        # Resultado financeiro
        if not capital_df.empty:
            capital_inicial = capital_df.iloc[0]['capital']
            capital_final = capital_df.iloc[-1]['capital']
            lucro_total = capital_final - capital_inicial
            
            print(f"\n💰 RESULTADO FINANCEIRO:")
            print(f"   Capital Inicial: R$ {capital_inicial:.2f}")
            print(f"   Capital Final: R$ {capital_final:.2f}")
            print(f"   Lucro/Prejuízo: R$ {lucro_total:+.2f}")
            print(f"   Rentabilidade: {(lucro_total/capital_inicial)*100:+.2f}%")
        
        # Performance por dia
        print(f"\n📅 PERFORMANCE DIÁRIA:")
        trades_df['date'] = pd.to_datetime(trades_df['timestamp']).dt.date
        daily_pnl = trades_df.groupby('date')['profit_abs'].sum()
        
        for date, pnl in daily_pnl.items():
            print(f"   {date}: R$ {pnl:+.2f}")
        
        print("="*70)
    
    def shutdown(self):
        """Desliga o bot com segurança"""
        logger.info("🛑 Iniciando desligamento seguro...")
        
        self.running = False
        
        # Salva snapshot final
        try:
            if hasattr(self, 'exchange'):
                ticker = self.exchange.get_ticker()
                if ticker:
                    self.db.save_capital_snapshot(
                        self.risk_manager.capital_atual,
                        ticker['last']
                    )
        except:
            pass
        
        # Salva configurações
        self.settings.save_to_file()
        
        logger.info("👋 Bot desligado com sucesso!")
        sys.exit(0)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Bot de Trading Avançado')
    
    parser.add_argument('--mode', type=str, default='paper',
                        choices=['real', 'paper', 'backtest', 'optimize'],
                        help='Modo de operação')
    
    parser.add_argument('--days', type=int, default=30,
                        help='Dias para backtest/paper trading')
    
    parser.add_argument('--telegram', type=str,
                        help='Token do Telegram bot')
    
    parser.add_argument('--ml', action='store_true',
                        help='Ativar Machine Learning')
    
    parser.add_argument('--arbitrage', action='store_true',
                        help='Ativar arbitragem')
    
    parser.add_argument('--optimize', action='store_true',
                        help='Otimizar parâmetros')
    
    parser.add_argument('--report', action='store_true',
                        help='Gerar relatório')
    
    args = parser.parse_args()
    
    # Cria bot
    bot = AdvancedTradingBot()
    
    # Inicializa componentes opcionais
    if args.telegram:
        bot.initialize_telegram(args.telegram)
    
    if args.ml:
        bot.initialize_ml()
    
    if args.arbitrage:
        bot.initialize_arbitrage()
    
    if args.optimize:
        bot.initialize_optimizer()
    
    # Executa modo escolhido
    if args.mode == 'paper':
        bot.run_paper_trading(days=args.days)
    
    elif args.mode == 'backtest':
        bot.run_backtest(days=args.days, optimize=args.optimize)
    
    elif args.mode == 'real':
        bot.run_real()
    
    elif args.mode == 'optimize':
        if not bot.optimizer:
            bot.initialize_optimizer()
        df = bot.backtest.fetch_historical_data(days=args.days)
        
        param_grid = {
            'buy_threshold': [-0.5, -1.0, -1.5, -2.0],
            'sell_threshold': [2.0, 2.5, 3.0, 3.5, 4.0],
            'stop_loss': [-3.0, -4.0, -5.0, -6.0, -7.0]
        }
        
        results = bot.optimizer.optimize_parameters(df, param_grid)
        print(f"\n✅ Melhores parâmetros: {results['best_params']}")
    
    # Gera relatório se solicitado
    if args.report:
        bot.generate_report()

if __name__ == "__main__":
    main()
📋 13. EXEMPLO DE USO
examples/usage_examples.py
python
"""
Exemplos de uso do bot avançado
"""

# 1. Backtest com otimização
python main_advanced.py --mode backtest --days 90 --optimize

# 2. Paper trading por 60 dias
python main_advanced.py --mode paper --days 60

# 3. Modo real com Telegram e ML
python main_advanced.py --mode real --telegram SEU_TOKEN --ml

# 4. Apenas otimizar parâmetros
python main_advanced.py --mode optimize --days 180

# 5. Gerar relatório dos últimos 30 dias
python main_advanced.py --report

# 6. Modo real com arbitragem
python main_advanced.py --mode real --arbitrage --telegram SEU_TOKEN

# 7. Backtest com todos os recursos
python main_advanced.py --mode backtest --days 365 --optimize --ml --report
🎯 RESUMO DAS MELHORIAS IMPLEMENTADAS
text
╔══════════════════════════════════════════════════════════════╗
║  ✅ MELHORIAS IMPLEMENTADAS                                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📊 ANÁLISE TÉCNICA                                          ║
║  ├─ RSI para identificar sobrecomprado/sobrevendido         ║
║  ├─ MACD para tendências                                     ║
║  ├─ Bandas de Bollinger para volatilidade                   ║
║  └─ Volume Profile para suporte/resistência                 ║
║                                                              ║
║  🎯 ESTRATÉGIA AVANÇADA                                      ║
║  ├─ Múltiplos indicadores com pesos                         ║
║  ├─ Score de confiança para decisões                        ║
║  ├─ Proteção melhorada contra quedas                        ║
║  └─ Análise multifatorial                                   ║
║                                                              ║
║  💹 ARBITRAGEM                                               ║
║  ├─ Scanner entre múltiplas exchanges                       ║
║  ├─ Detecção automática de spreads                          ║
║  └─ Thread dedicada para monitoramento                      ║
║                                                              ║
║  🤖 MACHINE LEARNING                                         ║
║  ├─ Random Forest para predições                            ║
║  ├─ Feature engineering                                     ║
║  ├─ Treinamento com dados históricos                        ║
║  └─ Importância de features                                 ║
║                                                              ║
║  🛡️ RISK MANAGEMENT                                          ║
║  ├─ Limite diário de trades                                 ║
║  ├─ Controle de perdas consecutivas                         ║
║  ├─ Max drawdown                                            ║
║  ├─ Tamanho de posição baseado em risco                     ║
║  └─ Score de risco dinâmico                                  ║
║                                                              ║
║  📱 TELEGRAM AVANÇADO                                        ║
║  ├─ Menu interativo com botões                              ║
║  ├─ Gráficos de preço                                       ║
║  ├─ Status em tempo real                                    ║
║  ├─ Controle remoto do bot                                  ║
║  └─ Alertas personalizados                                  ║
║                                                              ║
║  💾 BANCO DE DADOS                                           ║
║  ├─ SQLite para persistência                                ║
║  ├─ Histórico completo de trades                            ║
║  ├─ Snapshots de capital                                    ║
║  ├─ Alertas e notificações                                  ║
║  └─ Configurações persistidas                               ║
║                                                              ║
║  🔄 OTIMIZAÇÃO                                               ║
║  ├─ Grid search paralelo                                    ║
║  ├─ Walk-forward optimization                               ║
║  ├─ Sugestão baseada em volatilidade                        ║
║  └─ Múltiplas métricas (Sharpe, Return, Win Rate)           ║
║                                                              ║
║  🧪 PAPER TRADING                                            ║
║  ├─ Cenários realistas (crash, pump, lateral)               ║
║  ├─ Geração de preços sintéticos                            ║
║  ├─ Eventos extremos aleatórios                             ║
║  └─ Relatórios detalhados                                   ║
║                                                              ║
║  📊 BACKTESTING                                              ║
║  ├─ Dados históricos reais                                  ║
║  ├─ Múltiplas exchanges                                     ║
║  ├─ Cálculo de métricas profissionais                       ║
║  ├─ Sharpe Ratio, Drawdown, Profit Factor                   ║
║  └─ Visualização de resultados                              ║
╚══════════════════════════════════════════════════════════════╝


Aqui está a estrutura completa de pastas e arquivos para você criar no VSCode e gerenciar com GitHub Desktop:

text
🤖 trading-bot-avancado/
│
├── 📂 .github/
│   └── 📂 workflows/
│       └── 📄 tests.yml
│
├── 📂 .vscode/
│   ├── 📄 settings.json
│   └── 📄 launch.json
│
├── 📂 config/
│   ├── 📄 __init__.py
│   ├── 📄 settings.py
│   └── 📄 advanced_settings.py
│
├── 📂 core/
│   ├── 📄 __init__.py
│   ├── 📄 exchange.py
│   ├── 📄 strategy.py
│   ├── 📄 strategy_avancada.py
│   ├── 📄 indicators.py
│   └── 📄 trader.py
│
├── 📂 risk/
│   ├── 📄 __init__.py
│   └── 📄 risk_manager.py
│
├── 📂 database/
│   ├── 📄 __init__.py
│   └── 📄 db_manager.py
│
├── 📂 mobile/
│   ├── 📄 __init__.py
│   └── 📄 telegram_advanced.py
│
├── 📂 paper_trading/
│   ├── 📄 __init__.py
│   └── 📄 simulator.py
│
├── 📂 backtest/
│   ├── 📄 __init__.py
│   ├── 📄 backtest_engine.py
│   └── 📄 results/
│
├── 📂 optimization/
│   ├── 📄 __init__.py
│   └── 📄 optimizer.py
│
├── 📂 arbitrage/
│   ├── 📄 __init__.py
│   └── 📄 arbitrage_scanner.py
│
├── 📂 ml/
│   ├── 📄 __init__.py
│   ├── 📄 trainer.py
│   └── 📂 models/
│
├── 📂 utils/
│   ├── 📄 __init__.py
│   ├── 📄 logger.py
│   ├── 📄 notifications.py
│   └── 📄 helpers.py
│
├── 📂 tests/
│   ├── 📄 __init__.py
│   ├── 📄 test_strategy.py
│   ├── 📄 test_exchange.py
│   └── 📄 test_risk.py
│
├── 📂 data/
│   ├── 📄 .gitkeep
│   ├── 📂 logs/
│   ├── 📂 history/
│   └── 📂 exports/
│
├── 📂 examples/
│   ├── 📄 usage_examples.py
│   └── 📄 quick_start.py
│
├── 📂 scripts/
│   ├── 📄 setup_windows.bat
│   ├── 📄 run_backtest.bat
│   ├── 📄 run_paper.bat
│   └── 📄 run_real.bat
│
├── 📄 .env
├── 📄 .env.example
├── 📄 .gitignore
├── 📄 requirements.txt
├── 📄 requirements-dev.txt
├── 📄 main.py
├── 📄 main_advanced.py
├── 📄 README.md
├── 📄 LICENSE
└── 📄 trading_bot.db
📝 CONTEÚDO DE CADA ARQUIVO
1. .gitignore
gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite3

# Logs
logs/
*.log
data/logs/*

# Configurações locais
.env
config_local.py

# IDE
.vscode/
.idea/
*.swp
*.swo

# Arquivos de dados
data/history/*
!data/history/.gitkeep
data/exports/*

# Modelos ML
ml/models/*
!ml/models/.gitkeep

# Relatórios
*.html
*.pdf
reports/

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# GitHub Desktop
.DS_Store
2. requirements.txt
txt
# Core
ccxt>=4.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
numpy>=1.24.0

# Utils
colorama>=0.4.6
schedule>=1.2.0
requests>=2.31.0

# Database
sqlite3  # built-in

# Telegram
python-telegram-bot>=20.0

# Análise Técnica
ta-lib>=0.4.28
scipy>=1.10.0

# Machine Learning
scikit-learn>=1.2.0
joblib>=1.2.0

# Visualização
matplotlib>=3.7.0
seaborn>=0.12.0

# Backtesting
plotly>=5.14.0

# WebSocket
websocket-client>=1.5.0

# Async
aiohttp>=3.8.0
asyncio>=3.4.3
3. requirements-dev.txt
txt
# Testing
pytest>=7.3.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-mock>=3.11.0

# Linting
flake8>=6.0.0
pylint>=2.17.0
black>=23.0.0
isort>=5.12.0
mypy>=1.3.0

# Documentation
sphinx>=6.2.0
sphinx-rtd-theme>=1.2.0

# Profiling
memory-profiler>=0.61.0
line-profiler>=4.0.0
4. .env.example
env
# ============================================
# CONFIGURAÇÕES DA EXCHANGE
# ============================================

# Exchange (binance, bybit, kraken, coinbase)
EXCHANGE_ID=binance

# API Keys (NUNCA compartilhe!)
API_KEY=sua_api_key_aqui
API_SECRET=seu_api_secret_aqui

# Modo de teste (true para testes sem dinheiro real)
USE_SANDBOX=true

# ============================================
# CONFIGURAÇÕES DE TRADING
# ============================================

# Par de trading
SYMBOL=BTC/USDT

# Quantidade a ser negociada (em BTC)
TRADE_QUANTITY=0.001

# Estratégia principal
BUY_THRESHOLD=-1.0        # Comprar quando cair -1%
SELL_THRESHOLD=3.0        # Vender quando subir +3%
STOP_LOSS=-5.0            # Stop loss em -5%

# Limites
MAX_DAILY_TRADES=10       # Máximo de trades por dia
MAX_CONSECUTIVE_LOSSES=3  # Máximo de perdas consecutivas

# ============================================
# NOTIFICAÇÕES TELEGRAM
# ============================================

TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# ============================================
# CONFIGURAÇÕES AVANÇADAS
# ============================================

# Indicadores Técnicos
USE_RSI=true
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70

USE_MACD=true
USE_BOLLINGER=true

# Machine Learning
USE_ML=false
ML_MODEL_PATH=ml/models/latest.pkl

# Arbitragem
USE_ARBITRAGE=false
ARBITRAGE_MIN_SPREAD=0.5

# ============================================
# LOGGING
# ============================================

LOG_LEVEL=INFO
LOG_FILE=data/logs/trading_bot.log
5. .vscode/settings.json
json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length",
        "100"
    ],
    "editor.formatOnSave": true,
    "editor.rulers": [100],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.git": true,
        "**/.DS_Store": true,
        "**/venv": true,
        "**/env": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
6. .vscode/launch.json
json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Bot Principal",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "args": ["--mode", "paper", "--days", "30"]
        },
        {
            "name": "Python: Backtest",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main_advanced.py",
            "console": "integratedTerminal",
            "args": ["--mode", "backtest", "--days", "90", "--optimize"]
        },
        {
            "name": "Python: Paper Trading",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main_advanced.py",
            "console": "integratedTerminal",
            "args": ["--mode", "paper", "--days", "60"]
        },
        {
            "name": "Python: Testes",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"]
        }
    ]
}
7. scripts/setup_windows.bat
batch
@echo off
echo ========================================
echo Configurando Bot de Trading no Windows
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8 ou superior
    pause
    exit /b 1
)

REM Cria ambiente virtual
echo Criando ambiente virtual...
python -m venv venv

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instala dependências
echo Instalando dependências...
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Cria estrutura de pastas
echo Criando estrutura de pastas...
mkdir data\logs 2>nul
mkdir data\history 2>nul
mkdir data\exports 2>nul
mkdir ml\models 2>nul
mkdir backtest\results 2>nul

REM Copia arquivo de exemplo
if not exist .env (
    echo Criando arquivo .env a partir do exemplo...
    copy .env.example .env
)

echo.
echo ========================================
echo ✅ Configuracao concluida com sucesso!
echo ========================================
echo.
echo Proximos passos:
echo 1. Edite o arquivo .env com suas configuracoes
echo 2. Execute: python main.py --mode paper
echo 3. Para testar: python main_advanced.py --mode backtest
echo.
pause
8. scripts/run_paper.bat
batch
@echo off
call venv\Scripts\activate.bat
python main_advanced.py --mode paper --days %1
pause
9. scripts/run_backtest.bat
batch
@echo off
call venv\Scripts\activate.bat
python main_advanced.py --mode backtest --days %1 --optimize
pause
10. scripts/run_real.bat (CUIDADO!)
batch
@echo off
echo ========================================
echo ⚠️  ATENCAO - MODO REAL
echo ========================================
echo.
echo Voce esta prestes a usar DINHEIRO REAL!
echo.
set /p confirm="Digite 'SIM' para continuar: "
if not "%confirm%"=="SIM" (
    echo Operacao cancelada.
    pause
    exit /b
)
call venv\Scripts\activate.bat
python main_advanced.py --mode real
pause
11. utils/helpers.py
python
import os
import json
import platform
from datetime import datetime
from typing import Any, Dict

class SystemHelper:
    """Utilitários do sistema"""
    
    @staticmethod
    def get_system_info() -> Dict:
        """Retorna informações do sistema"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'python': platform.python_version(),
            'machine': platform.machine(),
            'node': platform.node()
        }
    
    @staticmethod
    def ensure_directories():
        """Garante que todos os diretórios necessários existam"""
        directories = [
            'data/logs',
            'data/history',
            'data/exports',
            'ml/models',
            'backtest/results',
            'tests/reports'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

class FileHelper:
    """Utilitários de arquivo"""
    
    @staticmethod
    def save_json(data: Any, filename: str):
        """Salva dados em JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_json(filename: str) -> Any:
        """Carrega dados de JSON"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    @staticmethod
    def save_report(data: Dict, report_type: str):
        """Salva relatório com timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"reports/{report_type}_{timestamp}.json"
        FileHelper.save_json(data, filename)
        return filename

class NumberHelper:
    """Utilitários de números"""
    
    @staticmethod
    def format_currency(value: float, currency: str = 'R$') -> str:
        """Formata valor monetário"""
        return f"{currency} {value:,.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Formata porcentagem"""
        return f"{value:+.2f}%"
    
    @staticmethod
    def format_btc(value: float) -> str:
        """Formata quantidade de BTC"""
        return f"{value:.8f} BTC"



TRADING-BOT-AVANCADO
├── .vscode/
├── backtest/
├── config/
├── core/
├── database/
├── data/
├── examples/
├── ml/
├── mobile/
├── optimization/
├── paper_trading/
├── risk/
├── scripts/
├── tests/
├── utils/
├── .env
├── .env.example
├── .gitignore
├── main.py
├── main_advanced.py
├── README.md
├── requirements.txt
└── trading_bot.db



