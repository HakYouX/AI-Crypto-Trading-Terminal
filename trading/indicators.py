import numpy as np
import pandas as pd

class TechnicalIndicators:
    def __init__(self):
        pass
        
    def calculate_advanced_indicators(self, df):
        """Расчет продвинутых технических индикаторов"""
        if df is None or len(df) < 50:  # Нужно достаточно данных для индикаторов
            return None
            
        closes = df['close'].values  # Цены закрытия как numpy массив
        
        # SMA (Simple Moving Average) - простая скользящая средняя
        sma_20 = np.mean(closes[-20:])  # 20-периодная SMA
        sma_50 = np.mean(closes[-50:])  # 50-периодная SMA
        
        # RSI (Relative Strength Index) - индекс относительной силы
        if len(closes) >= 16:
            delta = np.diff(closes[-15:])  # Разницы между ценами
            gain = np.where(delta > 0, delta, 0)  # Положительные изменения
            loss = np.where(delta < 0, -delta, 0)  # Отрицательные изменения
            
            avg_gain = np.mean(gain) if np.sum(gain) > 0 else 0.001  # Средний прирост
            avg_loss = np.mean(loss) if np.sum(loss) > 0 else 0.001  # Средняя потеря
            
            rs = avg_gain / avg_loss  # Относительная сила
            rsi = 100 - (100 / (1 + rs))  # RSI формула
        else:
            rsi = 50  # Значение по умолчанию
        
        # MACD (Moving Average Convergence Divergence)
        ema_12 = np.mean(closes[-12:]) if len(closes) >= 12 else closes[-1]  # 12-периодная EMA
        ema_26 = np.mean(closes[-26:]) if len(closes) >= 26 else closes[-1]  # 26-периодная EMA
        macd = ema_12 - ema_26  # Линия MACD
        
        # Bollinger Bands - полосы Боллинджера
        if len(closes) >= 20:
            bb_upper = np.mean(closes[-20:]) + 2 * np.std(closes[-20:])  # Верхняя полоса
            bb_lower = np.mean(closes[-20:]) - 2 * np.std(closes[-20:])  # Нижняя полоса
            # Позиция текущей цены относительно полос (0-1)
            bb_position = (closes[-1] - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
        else:
            bb_position = 0.5
        
        # Volume analysis - анализ объема
        if len(df) >= 20:
            volume_sma = np.mean(df['volume'].values[-20:])  # SMA объема
            current_volume = df['volume'].values[-1]  # Текущий объем
            volume_ratio = current_volume / volume_sma if volume_sma != 0 else 1  # Отношение объема к среднему
        else:
            volume_ratio = 1
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'macd': macd,
            'bb_position': bb_position,
            'volume_ratio': volume_ratio,
            'current_price': closes[-1],
            'timestamp': df['timestamp'].iloc[-1]
        }