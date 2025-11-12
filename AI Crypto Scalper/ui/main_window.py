import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime

from config import COLORS, BYBIT_SERVERS, DEFAULT_SETTINGS
from ui.control_panel import ControlPanel
from ui.chart_manager import ChartManager
from trading.data_provider import DataProvider
from trading.indicators import TechnicalIndicators
from trading.ai_predictor import AIPredictor
from utils.logger import TradingLogger

class ProfessionalCryptoTrader:
    def __init__(self, root):
        self.root = root
        self.colors = COLORS
        
        # Настройка главного окна
        self.root.title("🚀 AI Crypto Trading Terminal v3.0 (BYBIT + Predictions)")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors['bg'])
        
        # Инициализация компонентов
        self.data_provider = DataProvider(BYBIT_SERVERS[0])
        self.indicators = TechnicalIndicators()
        self.ai_predictor = AIPredictor()
        self.logger = TradingLogger()
        
        # Переменные состояния
        self.is_running = False
        self.current_server = BYBIT_SERVERS[0]
        self.signals_history = []
        self.ping_time = 0
        
        # Инициализируем атрибуты для виджетов
        self.ping_label = None
        self.connection_info = None
        self.log_text = None
        self.control_panel = None
        self.chart_manager = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель
        self.setup_header(main_container)
        
        # Основное содержимое
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Левая панель (управление)
        self.control_panel = ControlPanel(content_frame, self)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Правая панель (график и логи)
        self.setup_display_panel(content_frame)
        
    def setup_header(self, parent):
        """Верхняя панель с информацией"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Заголовок
        title_label = tk.Label(header_frame, 
                              text="🚀 AI Crypto Trading Terminal v3.0 (BYBIT + AI Predictions)", 
                              font=("Arial", 16, "bold"), 
                              bg=self.colors['bg'], fg=self.colors['text'])
        title_label.pack(side=tk.LEFT)
        
        # Информация о подключении
        self.connection_info = tk.Label(header_frame, 
                                       text="Подключение: ●", 
                                       font=("Arial", 10),
                                       bg=self.colors['bg'], fg="#22c55e")
        self.connection_info.pack(side=tk.RIGHT, padx=10)
        
        # Пинг
        self.ping_label = tk.Label(header_frame, 
                                  text="Пинг: -- мс", 
                                  font=("Arial", 10),
                                  bg=self.colors['bg'], fg=self.colors['text'])
        self.ping_label.pack(side=tk.RIGHT, padx=10)
        
    def setup_display_panel(self, parent):
        """Панель с графиком и логами"""
        display_frame = tk.Frame(parent, bg=self.colors['bg'])
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # График
        self.chart_manager = ChartManager(display_frame)
        self.chart_manager.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Логи
        log_frame = tk.LabelFrame(display_frame, text="Торговые сигналы & AI Анализ", 
                                 bg=self.colors['card_bg'], fg=self.colors['text'],
                                 padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 bg=self.colors['card_bg'], 
                                                 fg=self.colors['text'],
                                                 font=("Consolas", 9),
                                                 relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log_message(self, message, signal_type="info"):
        """Логирование с цветовым кодированием"""
        if self.log_text:  # Проверяем что log_text инициализирован
            self.logger.log_message(self.log_text, message, signal_type, self.colors)
        
    def change_server(self, server_name):
        """Смена сервера BYBIT"""
        for server in BYBIT_SERVERS:
            if server['name'] == server_name:
                self.current_server = server
                self.data_provider.set_server(server)
                self.log_message(f"Сервер изменен на: {server_name}", "info")
                # Запускаем измерение пинга в отдельном потоке
                threading.Thread(target=self.measure_ping, daemon=True).start()
                break
    
    def measure_ping(self):
        """Измерение пинга до сервера"""
        ping_time = self.data_provider.measure_ping()
        
        # Обновляем UI в главном потоке
        self.root.after(0, self._update_ping_display, ping_time)
    
    def _update_ping_display(self, ping_time):
        """Обновление отображения пинга (вызывается в главном потоке)"""
        if ping_time is not None:
            self.ping_time = ping_time
            if self.ping_label:  # Проверяем что ping_label инициализирован
                self.ping_label.config(text=f"Пинг: {self.ping_time} мс")
                
                # Цветовая индикация качества соединения
                if self.ping_time < 40:
                    color, status = "#22c55e", "● Идеально"
                elif self.ping_time < 80:
                    color, status = "#eab308", "● Быстро"
                elif self.ping_time < 150:
                    color, status = "#f97316", "● Нормально"
                else:
                    color, status = "#ef4444", "● Медленно"
                
                if self.connection_info:  # Проверяем что connection_info инициализирован
                    self.connection_info.config(text=f"{status} | {self.current_server['name']}", fg=color)
        else:
            if self.ping_label:
                self.ping_label.config(text="Пинг: -- мс")
            if self.connection_info:
                self.connection_info.config(text="● Ошибка подключения", fg="#ef4444")
    
    def start_analysis(self):
        """Запуск анализа"""
        if not self.is_running:
            self.is_running = True
            if self.control_panel:
                self.control_panel.start_btn.config(state=tk.DISABLED)
                self.control_panel.stop_btn.config(state=tk.NORMAL)
            
            symbol = self.control_panel.symbol_var.get() if self.control_panel else "BTCUSDT"
            self.log_message(f"🚀 Запуск AI анализа для {symbol}", "info")
            self.log_message(f"📡 Используется сервер: {self.current_server['name']}", "info")
            self.log_message("🤖 AI модель обучается на исторических данных...", "prediction")
            
            thread = threading.Thread(target=self.trading_loop, daemon=True)
            thread.start()
    
    def stop_analysis(self):
        """Остановка анализа"""
        self.is_running = False
        if self.control_panel:
            self.control_panel.start_btn.config(state=tk.NORMAL)
            self.control_panel.stop_btn.config(state=tk.DISABLED)
        self.log_message("⏹️ Анализ остановлен пользователем", "info")
    
    def trading_loop(self):
        """Основной торговый цикл"""
        while self.is_running:
            try:
                # Периодически измеряем пинг
                if not hasattr(self, 'ping_counter'):
                    self.ping_counter = 0
                
                self.ping_counter += 1
                if self.ping_counter >= 10:
                    threading.Thread(target=self.measure_ping, daemon=True).start()
                    self.ping_counter = 0
                
                symbol = self.control_panel.symbol_var.get() if self.control_panel else "BTCUSDT"
                
                # Получаем данные
                market_data = self.data_provider.get_market_data(symbol)
                
                if market_data is not None and len(market_data) > 50:
                    # Обучаем модель
                    if not self.ai_predictor.is_model_trained:
                        self.ai_predictor.train_prediction_model(market_data)
                        if self.ai_predictor.is_model_trained:
                            self.log_message("🤖 AI модель успешно обучена!", "prediction")
                    
                    # Получаем предсказания
                    future_prices = None
                    if self.ai_predictor.is_model_trained and self.control_panel and self.control_panel.show_predictions_var.get():
                        future_prices = self.ai_predictor.predict_future_prices(
                            market_data['close'].values,
                            self.control_panel.prediction_length_var.get() if self.control_panel else 5
                        )
                        
                        if future_prices is not None:
                            predicted_change = ((future_prices[-1] - market_data['close'].iloc[-1]) / market_data['close'].iloc[-1]) * 100
                            direction = "рост" if predicted_change > 0 else "падение"
                            self.log_message(f"📊 AI предсказывает {direction} на {abs(predicted_change):.1f}%", "prediction")
                    
                    # Расчет индикаторов
                    indicators = self.indicators.calculate_advanced_indicators(market_data)
                    
                    if indicators:  # Проверяем что индикаторы рассчитаны
                        # AI решение
                        aggressiveness = self.control_panel.aggressiveness_var.get() if self.control_panel else 0.7
                        commission = self.control_panel.commission_var.get() if self.control_panel else 0.1
                        min_profit = self.control_panel.min_profit_var.get() if self.control_panel else 0.2
                        
                        signal, confidence = self.ai_predictor.ai_trading_decision(
                            indicators, 
                            future_prices,
                            aggressiveness,
                            commission,
                            min_profit
                        )
                        
                        # Обновляем график
                        if self.chart_manager:
                            chart_type = self.control_panel.chart_type_var.get() if self.control_panel else "candles"
                            show_predictions = self.control_panel.show_predictions_var.get() if self.control_panel else True
                            
                            self.chart_manager.update_chart(
                                market_data, 
                                symbol,
                                chart_type,
                                show_predictions,
                                future_prices,
                                signal,
                                indicators['current_price']
                            )
                        
                        # Логируем сильные сигналы
                        if signal != "HOLD" and confidence > 0.6:
                            signal_data = {
                                'timestamp': datetime.now(),
                                'symbol': symbol,
                                'signal': signal,
                                'confidence': confidence,
                                'price': indicators['current_price'],
                                'server': self.current_server['name'],
                                'prediction_used': future_prices is not None
                            }
                            self.signals_history.append(signal_data)
                            
                            if signal == "BUY":
                                message = f"🚀 ПОКУПКА! Уверенность: {confidence:.1%} | Цена: {indicators['current_price']:.4f}"
                                self.log_message(message, "buy")
                            else:
                                message = f"🔻 ПРОДАЖА! Уверенность: {confidence:.1%} | Цена: {indicators['current_price']:.4f}"
                                self.log_message(message, "sell")
                        
                        # Обновляем статистику
                        if self.control_panel:
                            buy_count = len([s for s in self.signals_history if s['signal'] == 'BUY'])
                            sell_count = len([s for s in self.signals_history if s['signal'] == 'SELL'])
                            self.control_panel.update_stats(
                                len(self.signals_history),
                                buy_count,
                                sell_count,
                                self.ai_predictor.is_model_trained,
                                self.ping_time,
                                self.current_server['name']
                            )
                
                # Пауза между анализами
                for i in range(5):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_message(f"Ошибка в торговом цикле: {e}", "error")
                time.sleep(5)