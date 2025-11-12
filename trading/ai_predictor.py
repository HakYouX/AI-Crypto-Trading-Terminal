import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AIPredictor:
    def __init__(self):
        self.prediction_model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_model_trained = False
        
    def train_prediction_model(self, price_data):
        """Обучение модели для предсказания цены"""
        if len(price_data) < 30:  # Нужно минимум 30 точек для обучения
            return None
            
        try:
            # Подготовка данных для обучения
            prices = price_data['close'].values  # Берем только цены закрытия
            
            # Создаем признаки: предыдущие цены
            X = []  # Признаки (исторические данные)
            y = []  # Целевые значения (будущие цены)
            
            lookback = 10  # Смотрим на 10 предыдущих свечей
            forecast = 5   # Предсказываем на 5 свечей вперед
            
            # Создаем обучающие примеры
            for i in range(lookback, len(prices) - forecast):
                X.append(prices[i-lookback:i])  # 10 предыдущих цен
                y.append(prices[i:i+forecast])  # 5 следующих цен
            
            if len(X) < 5:  # Нужно минимум 5 примеров
                return None
                
            X = np.array(X)  # Преобразуем в numpy массивы
            y = np.array(y)
            
            # Обучаем модель
            self.prediction_model.fit(X, y)
            self.is_model_trained = True
            
            return self.prediction_model
            
        except Exception as e:
            print(f"Ошибка обучения модели: {e}")
            return None
    
    def predict_future_prices(self, current_prices, steps=5):
        """Предсказание будущих цен"""
        if not self.is_model_trained or len(current_prices) < 10:  # Проверка готовности модели
            return None
            
        try:
            # Берем последние 10 цен для предсказания
            if len(current_prices) > 10:
                input_data = current_prices[-10:]
            else:
                input_data = current_prices
                
            input_data = np.array(input_data).reshape(1, -1)  # Подгоняем под формат модели
            
            # Предсказываем
            prediction = self.prediction_model.predict(input_data)[0]
            
            return prediction
            
        except Exception as e:
            print(f"Ошибка предсказания: {e}")
            return None
            
    def ai_trading_decision(self, indicators, future_prices=None, aggressiveness=0.7, commission=0.1, min_profit=0.2):
        """Улучшенный AI для принятия торговых решений с учетом предсказаний"""
        if indicators is None:
            return "HOLD", 0.5
        
        # Веса для различных факторов принятия решения
        weights = {
            'trend': 0.25,  # Тренд
            'momentum': 0.25,  # Моментум
            'volatility': 0.15,  # Волатильность
            'volume': 0.15,  # Объем
            'prediction': 0.2  # Предсказания AI
        }
        
        # Анализ тренда
        trend_score = 0
        if indicators['sma_20'] > indicators['sma_50']:  # Бычий тренд
            trend_score += 1
        if indicators['macd'] > 0:  # MACD выше нуля
            trend_score += 1
        
        # Анализ моментума
        momentum_score = 0
        if 30 <= indicators['rsi'] <= 45:  # RSI в зоне перепроданности (покупка)
            momentum_score += 2
        elif indicators['rsi'] < 30:  # Сильная перепроданность
            momentum_score += 1
        elif indicators['rsi'] > 70:  # RSI в зоне перекупленности (продажа)
            momentum_score -= 2
        elif indicators['rsi'] > 55:  # Начало перекупленности
            momentum_score -= 1
        
        # Анализ волатильности
        volatility_score = 0
        if indicators['bb_position'] < 0.2:  # Возле нижней полосы Боллинджера (покупка)
            volatility_score += 1
        elif indicators['bb_position'] > 0.8:  # Возле верхней полосы Боллинджера (продажа)
            volatility_score -= 1
        
        # Анализ объема
        volume_score = 0
        if indicators['volume_ratio'] > 1.5:  # Объем выше среднего
            volume_score = 1 if trend_score > 0 else -1  # Подтверждает тренд
        
        # Анализ предсказаний AI
        prediction_score = 0
        if future_prices is not None and len(future_prices) > 0:
            current_price = indicators['current_price']
            predicted_change = (future_prices[-1] - current_price) / current_price * 100
            
            if predicted_change > 1.0:  # Предсказан рост >1%
                prediction_score += 2
            elif predicted_change > 0.5:  # Предсказан рост >0.5%
                prediction_score += 1
            elif predicted_change < -1.0:  # Предсказано падение >1%
                prediction_score -= 2
            elif predicted_change < -0.5:  # Предсказано падение >0.5%
                prediction_score -= 1
        
        # Общий счет с весами
        total_score = (
            trend_score * weights['trend'] +
            momentum_score * weights['momentum'] +
            volatility_score * weights['volatility'] +
            volume_score * weights['volume'] +
            prediction_score * weights['prediction']
        )
        
        total_score *= aggressiveness  # Учет агрессивности
        effective_commission = commission / 100 + min_profit / 100
        
        if total_score > effective_commission:  # Сигнал на покупку
            confidence = min(0.95, 0.5 + total_score)
            return "BUY", confidence
        elif total_score < -effective_commission:  # Сигнал на продажу
            confidence = min(0.95, 0.5 - total_score)
            return "SELL", confidence
        else:  # Удержание позиции
            return "HOLD", 0.5