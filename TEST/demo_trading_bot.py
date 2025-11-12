import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import time
import json

class CryptoTradingBot:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Crypto Trading Bot")
        self.root.geometry("800x600")
        
        self.is_running = False
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Выбор криптовалюты
        ttk.Label(control_frame, text="Криптовалюта:").grid(row=0, column=0, padx=5, pady=5)
        self.symbol_var = tk.StringVar(value="BTCUSDT")
        symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]
        symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var, 
                                   values=symbols, width=12)
        symbol_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Интервал
        ttk.Label(control_frame, text="Интервал:").grid(row=0, column=2, padx=5, pady=5)
        self.interval_var = tk.StringVar(value="1m")
        intervals = ["1m", "3m", "5m", "15m"]
        interval_combo = ttk.Combobox(control_frame, textvariable=self.interval_var, 
                                     values=intervals, width=8)
        interval_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Кнопки
        self.start_btn = ttk.Button(control_frame, text="СТАРТ", 
                                   command=self.start_analysis)
        self.start_btn.grid(row=0, column=4, padx=10, pady=5)
        
        self.stop_btn = ttk.Button(control_frame, text="СТОП", 
                                  command=self.stop_analysis, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, 
                                foreground="blue", font=("Arial", 10, "bold"))
        status_label.grid(row=0, column=6, padx=20, pady=5)
        
        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог торговых сигналов")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, 
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Статистика
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_var = tk.StringVar(value="Сигналы: 0 | Покупки: 0 | Продажи: 0")
        ttk.Label(stats_frame, textvariable=self.stats_var).pack()
        
        # Инициализация счетчиков
        self.signal_count = 0
        self.buy_count = 0
        self.sell_count = 0
    
    def log(self, message, signal_type="info"):
        """Логирование сообщений"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Цвета для разных типов сообщений
        colors = {
            "buy": "green",
            "sell": "red",
            "error": "orange",
            "info": "black"
        }
        
        tag = signal_type.upper()
        color = colors.get(signal_type, "black")
        
        # Добавляем сообщение
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Применяем цвет
        if signal_type in ["buy", "sell", "error"]:
            start_index = f"{self.log_text.index('end-2c')}"
            self.log_text.tag_add(tag, start_index, "end-1c")
            self.log_text.tag_config(tag, foreground=color, font=("Consolas", 9, "bold"))
        
        self.log_text.see(tk.END)
        self.root.update()
    
    def get_market_data(self, symbol, interval, limit=50):
        """Получение данных с Binance"""
        try:
            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            # Создаем DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Конвертируем цены в числа
            price_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in price_columns:
                df[col] = pd.to_numeric(df[col])
            
            return df[price_columns].values
            
        except Exception as e:
            self.log(f"Ошибка получения данных: {e}", "error")
            return None
    
    def analyze_market(self, price_data):
        """Улучшенный анализ рынка"""
        if price_data is None or len(price_data) < 20:
            return "HOLD", 0.5, 0
        
        closes = price_data[:, 3]  # Цены закрытия
        current_price = closes[-1]
        
        # Убедимся, что есть достаточное количество данных
        if len(closes) < 20:
            return "HOLD", 0.5, current_price
        
        # Скользящие средние (разные периоды для лучшего анализа)
        sma_fast = np.mean(closes[-5:])    # 5 периодов - быстрая
        sma_slow = np.mean(closes[-15:])   # 15 периодов - медленная
        
        # RSI расчет (исправленный)
        period = 14
        if len(closes) >= period + 1:
            deltas = np.diff(closes[-period-1:])
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains) if np.sum(gains) > 0 else 0.001
            avg_loss = np.mean(losses) if np.sum(losses) > 0 else 0.001
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50
        
        # MACD (простой)
        ema_12 = np.mean(closes[-12:])
        ema_26 = np.mean(closes[-26:]) if len(closes) >= 26 else ema_12
        macd = ema_12 - ema_26
        
        # Волатильность (ATR-like)
        high_low = price_data[-14:, 1] - price_data[-14:, 2]  # high - low
        volatility = np.mean(high_low) / current_price * 100
        
        # **УЛУЧШЕННАЯ ЛОГИКА СИГНАЛОВ**
        buy_score = 0
        sell_score = 0
        
        # === ПОКУПКА ===
        # 1. Быстрая MA выше медленной (тренд вверх)
        if sma_fast > sma_slow:
            buy_score += 2
        
        # 2. RSI показывает перепроданность (30-40) - ЛУЧШЕЕ время для покупки
        if 25 <= rsi <= 40:
            buy_score += 3
        elif 40 < rsi <= 50:  # Нейтральная зона, но с потенциалом роста
            buy_score += 1
        
        # 3. MACD положительный
        if macd > 0:
            buy_score += 1
        
        # 4. Умеренная волатильность (не слишком спокойно, не слишком бурно)
        if 0.5 <= volatility <= 3.0:
            buy_score += 1
        
        # === ПРОДАЖА ===
        # 1. Быстрая MA ниже медленной (тренд вниз)
        if sma_fast < sma_slow:
            sell_score += 2
        
        # 2. RSI показывает перекупленность (60-70) - время продавать
        if 60 <= rsi <= 75:
            sell_score += 3
        elif 50 <= rsi < 60:  # Нейтральная зона, но с риском падения
            sell_score += 1
        
        # 3. MACD отрицательный
        if macd < 0:
            sell_score += 1
        
        # 4. Высокая волатильность (рискованный рынок)
        if volatility > 3.0:
            sell_score += 1
        
        # === РЕШЕНИЕ ===
        total_signals = buy_score + sell_score
        if total_signals == 0:
            return "HOLD", 0.5, current_price
        
        # Рассчитываем уверенность более консервативно
        if buy_score > sell_score:
            confidence = min(0.85, 0.4 + (buy_score / 10))  # Макс 85%
            return "BUY", confidence, current_price
        elif sell_score > buy_score:
            confidence = min(0.85, 0.4 + (sell_score / 10))  # Макс 85%
            return "SELL", confidence, current_price
        else:
            return "HOLD", 0.5, current_price
    
    def trading_loop(self):
        """Основной цикл торговли"""
        while self.is_running:
            try:
                symbol = self.symbol_var.get()
                interval = self.interval_var.get()
                
                # Получаем данные
                market_data = self.get_market_data(symbol, interval)
                
                if market_data is not None:
                    # Анализируем
                    signal, confidence, price = self.analyze_market(market_data)
                    
                    # Обновляем статистику
                    self.signal_count += 1
                    
                    # Логируем сильные сигналы
                    if signal != "HOLD" and confidence > 0.6:
                        if signal == "BUY":
                            self.buy_count += 1
                            self.log(f"🚀 ПОКУПКА! Уверенность: {confidence:.1%} | Цена: {price:.4f}", "buy")
                        else:
                            self.sell_count += 1
                            self.log(f"🔻 ПРОДАЖА! Уверенность: {confidence:.1%} | Цена: {price:.4f}", "sell")
                        
                        # Обновляем статистику
                        self.stats_var.set(f"Сигналы: {self.signal_count} | Покупки: {self.buy_count} | Продажи: {self.sell_count}")
                    
                    # Периодический статус
                    if self.signal_count % 10 == 0:
                        self.log(f"Анализ активен... Обработано {self.signal_count} сигналов")
                
                # Пауза 5 секунд
                for i in range(15):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log(f"Ошибка в основном цикле: {e}", "error")
                time.sleep(5)
    
    def start_analysis(self):
        """Запуск анализа"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log(f"🚀 Запуск AI анализа для {self.symbol_var.get()}", "info")
            self.status_var.set("Анализ активен...")
            
            # Запуск в отдельном потоке
            thread = threading.Thread(target=self.trading_loop, daemon=True)
            thread.start()
    
    def stop_analysis(self):
        """Остановка анализа"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Анализ остановлен")
        self.log("⏹️ Анализ остановлен пользователем", "info")

def main():
    try:
        root = tk.Tk()
        app = CryptoTradingBot(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        print("Убедитесь, что установлены все зависимости:")
        print("pip install pandas numpy requests")

if __name__ == "__main__":
    main()