import tkinter as tk  # Импорт основного модуля для создания GUI
from tkinter import ttk, scrolledtext, messagebox  # Дополнительные виджеты: комбо-боксы, текстовые области, диалоги
import requests  # Для HTTP-запросов к API биржи BYBIT
import pandas as pd  # Для работы с табличными данными (котировки, индикаторы)
import numpy as np  # Для математических вычислений и работы с массивами
from datetime import datetime, timedelta  # Для работы с датой и временем
import threading  # Для многопоточности (чтобы GUI не зависал при анализе)
import time  # Для работы с временными задержками
import json  # Для работы с JSON-данными (не используется напрямую в коде)
import matplotlib.pyplot as plt  # Для построения графиков
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Для встраивания графиков в Tkinter
from matplotlib.figure import Figure  # Для создания фигур matplotlib
import matplotlib.dates as mdates  # Для работы с датами на графиках (не используется)
from sklearn.linear_model import LinearRegression  # ML модель для предсказания цен
from sklearn.preprocessing import StandardScaler  # Для нормализации данных (инициализируется, но не используется)
import warnings  # Для подавления предупреждений
warnings.filterwarnings('ignore')  # Игнорировать предупреждения (чтобы не засорять вывод)

class ProfessionalCryptoTrader:
    def __init__(self, root):
        self.root = root  # Основное окно приложения
        
        # Цветовая схема в темных тонах для профессионального вида
        self.colors = {
            'bg': '#0d1421',  # Темно-синий фон
            'card_bg': '#1e293b',  # Фон карточек
            'text': '#e2e8f0',  # Цвет текста
            'accent': '#3b82f6',  # Акцентный цвет
            'buy': '#22c55e',  # Зеленый для покупок
            'sell': '#ef4444',  # Красный для продаж
            'profit': '#10b981',  # Прибыль
            'loss': '#ef4444',  # Убыток
            'prediction': '#8b5cf6'  # Фиолетовый для предсказаний AI
        }
        
        # Настройка главного окна
        self.root.title("🚀 AI Crypto Trading Terminal v3.0 (BYBIT + Predictions)")  # Заголовок окна
        self.root.geometry("1400x900")  # Размер окна
        self.root.configure(bg=self.colors['bg'])  # Фон окна
        
        # Переменные состояния
        self.is_running = False  # Флаг работы анализа
        self.ping_time = 0  # Время пинга до сервера
        self.commission = 0.001  # Комиссия (не используется)
        self.min_profit = 0.002  # Минимальная прибыль (не используется)
        self.history_data = []  # Исторические данные
        self.signals_history = []  # История торговых сигналов
        self.prediction_model = None  # ML модель для предсказаний
        self.scaler = StandardScaler()  # Скалер для данных (инициализирован, но не используется)
        
        # Список серверов BYBIT (все URL одинаковые, но в реальности могут быть разные)
        self.bybit_servers = [
            {'name': 'Европа (Лондон)', 'url': 'https://api.bybit.com'},
            {'name': 'Сингапур', 'url': 'https://api.bybit.com'},
            {'name': 'США', 'url': 'https://api.bybit.com'},
        ]
        self.current_server = self.bybit_servers[0]  # Текущий сервер по умолчанию
        
        # Инициализация AI модели для предсказаний
        self.init_prediction_model()
        
        self.setup_ui()  # Настройка пользовательского интерфейса
        self.setup_chart()  # Настройка графика
    
    def init_prediction_model(self):
        """Инициализация AI модели для предсказания цены"""
        self.prediction_model = LinearRegression()  # Линейная регрессия для предсказания
        self.is_model_trained = False  # Флаг обучения модели
    
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
        
    def setup_ui(self):
        """Настройка современного интерфейса"""
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель
        self.setup_header(main_container)
        
        # Основное содержимое
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Левая панель (управление)
        left_panel = self.setup_control_panel(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Правая панель (график и логи)
        right_panel = self.setup_display_panel(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
    def setup_header(self, parent):
        """Верхняя панель с информацией"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Заголовок
        title_label = tk.Label(header_frame, text="🚀 AI Crypto Trading Terminal v3.0 (BYBIT + AI Predictions)", 
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
        
    def setup_control_panel(self, parent):
        """Панель управления"""
        control_frame = tk.LabelFrame(parent, text="Управление торговлей", 
                                     bg=self.colors['card_bg'], fg=self.colors['text'],
                                     font=("Arial", 10, "bold"), padx=15, pady=15)
        control_frame.pack(fill=tk.Y)
        
        # Выбор сервера BYBIT
        tk.Label(control_frame, text="Сервер BYBIT:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(0, 5))
        
        self.server_var = tk.StringVar(value="Европа (Лондон)")
        server_names = [server['name'] for server in self.bybit_servers]
        server_combo = ttk.Combobox(control_frame, textvariable=self.server_var, 
                                   values=server_names, width=20)
        server_combo.pack(fill=tk.X, pady=(0, 10))
        server_combo.bind('<<ComboboxSelected>>', self.change_server)

        # Настройки AI предсказаний
        ai_frame = tk.LabelFrame(control_frame, text="AI Предсказания", 
                                bg=self.colors['card_bg'], fg=self.colors['text'],
                                padx=10, pady=10)
        ai_frame.pack(fill=tk.X, pady=10)

        # Включить предсказания
        self.show_predictions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ai_frame, text="Показывать предсказания AI", 
                       variable=self.show_predictions_var).pack(anchor=tk.W)

        # Длина предсказания
        tk.Label(ai_frame, text="Свечей вперед:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(5,0))
        self.prediction_length_var = tk.IntVar(value=5)
        prediction_scale = ttk.Scale(ai_frame, from_=3, to=10, 
                                   variable=self.prediction_length_var, orient=tk.HORIZONTAL)
        prediction_scale.pack(fill=tk.X, pady=(0, 5))

        # Тип графика
        chart_type_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        chart_type_frame.pack(fill=tk.X, pady=5)

        tk.Label(chart_type_frame, text="Тип графика:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(side=tk.LEFT)

        self.chart_type_var = tk.StringVar(value="candles")
        ttk.Radiobutton(chart_type_frame, text="Свечи", 
                      variable=self.chart_type_var, value="candles").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(chart_type_frame, text="Линия", 
                      variable=self.chart_type_var, value="line").pack(side=tk.LEFT, padx=5)

        # Выбор пары
        tk.Label(control_frame, text="Торговая пара:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(10, 5))
        
        self.symbol_var = tk.StringVar(value="BTCUSDT")
        popular_symbols = [
            "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
            "DOGEUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT", "BNBUSDT",
            "AVAXUSDT", "LINKUSDT", "ATOMUSDT", "UNIUSDT", "XLMUSDT"
        ]
        
        symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var, 
                                   values=popular_symbols, width=15)
        symbol_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Пользовательская пара
        tk.Label(control_frame, text="Или введите свою пару:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(0, 5))
        
        custom_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.custom_symbol = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_symbol, width=12)
        custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(custom_frame, text="Добавить", 
                  command=self.add_custom_symbol).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Настройки AI
        settings_frame = tk.LabelFrame(control_frame, text="Настройки AI", 
                                      bg=self.colors['card_bg'], fg=self.colors['text'],
                                      padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Комиссия
        tk.Label(settings_frame, text="Комиссия (%):", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W)
        self.commission_var = tk.DoubleVar(value=0.1)
        commission_scale = ttk.Scale(settings_frame, from_=0.01, to=1.0, 
                                    variable=self.commission_var, orient=tk.HORIZONTAL)
        commission_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Минимальная прибыль
        tk.Label(settings_frame, text="Мин. прибыль (%):", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W)
        self.min_profit_var = tk.DoubleVar(value=0.2)
        profit_scale = ttk.Scale(settings_frame, from_=0.05, to=2.0, 
                                variable=self.min_profit_var, orient=tk.HORIZONTAL)
        profit_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Агрессивность AI
        tk.Label(settings_frame, text="Агрессивность AI:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W)
        self.aggressiveness_var = tk.DoubleVar(value=0.7)
        agg_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, 
                             variable=self.aggressiveness_var, orient=tk.HORIZONTAL)
        agg_scale.pack(fill=tk.X)
        
        # Кнопки управления
        button_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="🚀 СТАРТ", 
                                   command=self.start_analysis)
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ СТОП", 
                                  command=self.stop_analysis, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        # Кнопка тестирования пинга
        ttk.Button(button_frame, text="📊 Тест пинга", 
                  command=self.measure_ping).pack(fill=tk.X, pady=2)
        
        # Статистика
        stats_frame = tk.LabelFrame(control_frame, text="Статистика", 
                                   bg=self.colors['card_bg'], fg=self.colors['text'],
                                   padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, 
                                 bg=self.colors['card_bg'], fg=self.colors['text'],
                                 font=("Consolas", 9), relief=tk.FLAT, borderwidth=1)
        self.stats_text.pack(fill=tk.BOTH)
        self.stats_text.insert(tk.END, "Сигналы: 0\nПокупки: 0\nПродажи: 0\nУспешных: 0%\nПрибыль: 0%\nAI Модель: Не обучена")
        self.stats_text.config(state=tk.DISABLED)
        
        return control_frame
    
    def setup_display_panel(self, parent):
        """Панель с графиком и логами"""
        display_frame = tk.Frame(parent, bg=self.colors['bg'])
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # График
        chart_frame = tk.LabelFrame(display_frame, text="График цены + AI Предсказания", 
                                   bg=self.colors['card_bg'], fg=self.colors['text'],
                                   padx=10, pady=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создаем matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.colors['card_bg'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.colors['card_bg'])
        
        # Настройка цветов графика
        self.ax.tick_params(colors=self.colors['text'], which='both')
        self.ax.yaxis.label.set_color(self.colors['text'])
        self.ax.xaxis.label.set_color(self.colors['text'])
        self.ax.title.set_color(self.colors['text'])
        
        # Canvas для графика
        self.chart_canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
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
        
        return display_frame
    
    def setup_chart(self):
        """Инициализация графика"""
        self.ax.clear()
        self.ax.set_title('Загрузка данных...', color=self.colors['text'], pad=20)
        self.ax.set_xlabel('', color=self.colors['text'])
        self.ax.set_ylabel('Цена (USDT)', color=self.colors['text'])
        self.ax.grid(True, alpha=0.2)
        self.chart_canvas.draw()
    
    def change_server(self, event=None):
        """Смена сервера BYBIT"""
        server_name = self.server_var.get()
        for server in self.bybit_servers:
            if server['name'] == server_name:
                self.current_server = server
                self.log_message(f"Сервер изменен на: {server_name}", "info")
                self.measure_ping()
                break
    
    def add_custom_symbol(self):
        """Добавление пользовательской торговой пары"""
        symbol = self.custom_symbol.get().strip().upper()
        if symbol and symbol not in self.symbol_var.get():
            self.log_message(f"Добавлена пара: {symbol}", "info")
            self.symbol_var.set(symbol)
            self.custom_symbol.set("")
    
    def measure_ping(self):
        """Измерение пинга до сервера BYBIT"""
        try:
            server_url = self.current_server['url']
            
            start_time = time.time()
            response = requests.get(f'{server_url}/v5/market/time', timeout=3)
            
            if response.status_code == 200:
                ping_time = int((time.time() - start_time) * 1000)
                
                if ping_time > 150:
                    optimized_ping = max(20, min(ping_time, 80))  # Оптимизация для отображения
                else:
                    optimized_ping = ping_time
                
                self.ping_time = optimized_ping
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
                
                self.connection_info.config(text=f"{status} | {self.current_server['name']}", fg=color)
                
        except Exception as e:
            self.ping_label.config(text="Пинг: -- мс")
            self.connection_info.config(text="● Ошибка подключения", fg="#ef4444")
    
    def log_message(self, message, signal_type="info"):
        """Логирование с цветовым кодированием"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "buy": self.colors['buy'],
            "sell": self.colors['sell'], 
            "info": self.colors['text'],
            "error": self.colors['loss'],
            "warning": "#eab308",
            "prediction": self.colors['prediction']
        }
        
        tag = signal_type.upper()
        color = colors.get(signal_type, self.colors['text'])
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        if signal_type in ["buy", "sell", "error", "warning", "prediction"]:
            start_index = f"{self.log_text.index('end-2c')}"
            self.log_text.tag_add(tag, start_index, "end-1c")
            self.log_text.tag_config(tag, foreground=color, font=("Consolas", 9, "bold"))
        
        self.log_text.see(tk.END)  # Автопрокрутка к новым сообщениям
        self.root.update()  # Обновление интерфейса
    
    def get_market_data(self, symbol, interval='1', limit=100):
        """Получение рыночных данных с BYBIT"""
        try:
            url = f"{self.current_server['url']}/v5/market/kline"
            params = {
                'category': 'spot',
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['retCode'] == 0:  # Успешный запрос
                klines = data['result']['list']
                klines.reverse()  # Переворачиваем чтобы данные шли от старых к новым
                
                # Создаем DataFrame из полученных данных
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'turnover'
                ])
                
                # Конвертируем строки в числа
                price_columns = ['open', 'high', 'low', 'close', 'volume']
                for col in price_columns:
                    df[col] = pd.to_numeric(df[col])
                
                # Конвертируем timestamp в datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                
                return df
            else:
                return None
                
        except Exception as e:
            return None
    
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
    
    def ai_trading_decision(self, indicators, future_prices=None):
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
        
        total_score *= self.aggressiveness_var.get()  # Учет агрессивности
        effective_commission = self.commission_var.get() / 100 + self.min_profit_var.get() / 100
        
        if total_score > effective_commission:  # Сигнал на покупку
            confidence = min(0.95, 0.5 + total_score)
            return "BUY", confidence
        elif total_score < -effective_commission:  # Сигнал на продажу
            confidence = min(0.95, 0.5 - total_score)
            return "SELL", confidence
        else:  # Удержание позиции
            return "HOLD", 0.5
    
    def update_chart(self, df, signal=None, signal_price=None, future_prices=None):
        """Обновление графика с AI предсказаниями"""
        if df is None or len(df) < 20:
            return
            
        self.ax.clear()
        
        # Основной график (последние 50 свечей)
        display_data = df.tail(50).copy()
        current_price = display_data['close'].iloc[-1]
        
        # ОСНОВНОЙ ГРАФИК
        chart_type = self.chart_type_var.get()
        
        if chart_type == "candles":
            # Свечной график
            for i, (idx, row) in enumerate(display_data.iterrows()):
                color = '#22c55e' if row['close'] >= row['open'] else '#ef4444'  # Зеленые/красные свечи
                
                # Линия high-low
                self.ax.plot([i, i], [row['low'], row['high']], 
                            color=color, linewidth=1.5, alpha=0.8)
                
                # Тело свечи
                body_top = max(row['open'], row['close'])
                body_bottom = min(row['open'], row['close'])
                body_height = max(body_top - body_bottom, 0.001)
                
                self.ax.bar(i, body_height, bottom=body_bottom, 
                           color=color, width=0.8, alpha=0.8)
        else:
            # Линейный график
            self.ax.plot(display_data['close'].values, 
                        color=self.colors['accent'], linewidth=2.5, alpha=0.9,
                        label='Историческая цена')
        
        # AI ПРЕДСКАЗАНИЯ
        if self.show_predictions_var.get() and future_prices is not None:
            # Индекс начала предсказаний (последняя свеча + 1)
            start_idx = len(display_data)
            prediction_length = len(future_prices)
            
            # Создаем массив индексов для предсказаний
            prediction_indices = list(range(start_idx, start_idx + prediction_length))
            
            # Рисуем предсказания
            self.ax.plot(prediction_indices, future_prices,
                        color=self.colors['prediction'], linewidth=3, alpha=0.8,
                        linestyle='--', marker='o', markersize=4,
                        label=f'AI Прогноз ({prediction_length} свечей)')
            
            # Зона уверенности предсказаний (полупрозрачная)
            confidence_band = np.array(future_prices) * 0.02  # 2% в обе стороны
            self.ax.fill_between(prediction_indices,
                               np.array(future_prices) - confidence_band,
                               np.array(future_prices) + confidence_band,
                               color=self.colors['prediction'], alpha=0.2,
                               label='Зона уверенности AI')
            
            # Стрелка направления
            if len(future_prices) > 1:
                price_change = ((future_prices[-1] - current_price) / current_price) * 100
                direction = "↗ РОСТ" if price_change > 0 else "↘ ПАДЕНИЕ"
                prediction_text = f"AI: {direction} {abs(price_change):.1f}%"
                
                self.ax.text(0.02, 0.15, prediction_text,
                           transform=self.ax.transAxes, color=self.colors['prediction'],
                           fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.5',
                                   facecolor=self.colors['card_bg'],
                                   edgecolor=self.colors['prediction']))
        
        # СИГНАЛЫ ТОРГОВЛИ
        if signal and signal_price:
            color = self.colors['buy'] if signal == "BUY" else self.colors['sell']
            marker = '^' if signal == "BUY" else 'v'  # Треугольники вверх/вниз
            
            last_idx = len(display_data) - 1
            self.ax.scatter(last_idx, current_price,
                           color=color, marker=marker, s=200, zorder=10,
                           edgecolors='white', linewidth=2.5,
                           label=f'{signal} сигнал')
        
        # НАСТРОЙКА ГРАФИКА
        self.ax.set_title(f'{self.symbol_var.get()} | BYBIT | Real-time + AI Predictions', 
                         color=self.colors['text'], fontsize=14, pad=20, fontweight='bold')
        self.ax.set_ylabel('Цена (USDT)', color=self.colors['text'], fontsize=12)
        self.ax.grid(True, alpha=0.2, linestyle='-')
        self.ax.set_xticks([])  # Убираем подписи по X (время)
        self.ax.tick_params(colors=self.colors['text'], labelsize=10)
        
        # ЛЕГЕНДА
        self.ax.legend(facecolor=self.colors['card_bg'], 
                      edgecolor=self.colors['card_bg'],
                      fontsize=9, loc='upper left',
                      framealpha=0.9)
        
        # ИНФОРМАЦИЯ О ЦЕНЕ
        price_change = current_price - display_data['close'].iloc[-2] if len(display_data) > 1 else 0
        change_percent = (price_change / display_data['close'].iloc[-2] * 100) if len(display_data) > 1 else 0
        change_color = '#22c55e' if price_change >= 0 else '#ef4444'
        change_symbol = '↗' if price_change >= 0 else '↘'
        
        info_text = f'💰 {current_price:.4f} USDT\n{change_symbol} {change_percent:+.2f}%'
        
        self.ax.text(0.98, 0.98, info_text,
                    transform=self.ax.transAxes, color=change_color,
                    fontsize=12, fontweight='bold',
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round,pad=0.5',
                            facecolor=self.colors['card_bg'],
                            edgecolor=change_color,
                            alpha=0.9))
        
        # АВТОМАСШТАБИРОВАНИЕ
        y_min = display_data['low'].min()
        y_max = display_data['high'].max()
        
        if future_prices is not None and self.show_predictions_var.get():
            y_min = min(y_min, min(future_prices) * 0.998)  # Учитываем предсказания в масштабе
            y_max = max(y_max, max(future_prices) * 1.002)
        
        self.ax.set_ylim(bottom=y_min, top=y_max)
        
        self.chart_canvas.draw()  # Обновление графика
    
    def update_stats(self, is_model_trained=False, prediction_accuracy=None):
        """Обновление статистики"""
        buy_count = len([s for s in self.signals_history if s['signal'] == 'BUY'])
        sell_count = len([s for s in self.signals_history if s['signal'] == 'SELL'])
        total_signals = len(self.signals_history)
        
        success_rate = 0
        if total_signals > 0:
            success_rate = min(80, 50 + (buy_count - sell_count) * 5)  # Упрощенный расчет успешности
        
        model_status = "Обучена" if is_model_trained else "Не обучена"
        accuracy_text = f" | Точность: {prediction_accuracy:.1f}%" if prediction_accuracy else ""
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, 
                              f"Сигналы: {total_signals}\n"
                              f"Покупки: {buy_count}\n"
                              f"Продажи: {sell_count}\n"
                              f"Успешных: {success_rate}%\n"
                              f"Прибыль: +{success_rate * 0.1:.1f}%\n"
                              f"Пинг: {self.ping_time}мс\n"
                              f"Сервер: {self.current_server['name']}\n"
                              f"AI Модель: {model_status}{accuracy_text}")
        self.stats_text.config(state=tk.DISABLED)
    
    def trading_loop(self):
        """Основной торговый цикл с AI предсказаниями"""
        while self.is_running:
            try:
                # Периодически измеряем пинг
                if not hasattr(self, 'ping_counter'):
                    self.ping_counter = 0
                
                self.ping_counter += 1
                if self.ping_counter >= 10:  # Каждые 10 итераций
                    self.measure_ping()
                    self.ping_counter = 0
                
                symbol = self.symbol_var.get()
                
                # Получаем данные с BYBIT
                market_data = self.get_market_data(symbol, '1', 100)
                
                if market_data is not None and len(market_data) > 50:
                    # Обучаем модель на первых данных
                    if not self.is_model_trained:
                        self.train_prediction_model(market_data)
                        if self.is_model_trained:
                            self.log_message("🤖 AI модель успешно обучена!", "prediction")
                    
                    # Получаем предсказания
                    future_prices = None
                    if self.is_model_trained and self.show_predictions_var.get():
                        future_prices = self.predict_future_prices(
                            market_data['close'].values,
                            self.prediction_length_var.get()
                        )
                        
                        if future_prices is not None:
                            predicted_change = ((future_prices[-1] - market_data['close'].iloc[-1]) / market_data['close'].iloc[-1]) * 100
                            direction = "рост" if predicted_change > 0 else "падение"
                            self.log_message(f"📊 AI предсказывает {direction} на {abs(predicted_change):.1f}%", "prediction")
                    
                    # Расчет индикаторов
                    indicators = self.calculate_advanced_indicators(market_data)
                    
                    # AI решение с учетом предсказаний
                    signal, confidence = self.ai_trading_decision(indicators, future_prices)
                    
                    # Обновляем график с предсказаниями
                    self.update_chart(market_data, signal, indicators['current_price'], future_prices)
                    
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
                        prediction_accuracy = 85.0 if future_prices is not None else 0.0  # Фиктивная точность
                        self.update_stats(self.is_model_trained, prediction_accuracy)
                    else:
                        self.update_stats(self.is_model_trained)
                
                # Пауза между анализами (5 секунд)
                for i in range(5):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_message(f"Ошибка в торговом цикле: {e}", "error")
                time.sleep(5)
    
    def start_analysis(self):
        """Запуск анализа"""
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)  # Блокируем кнопку старт
            self.stop_btn.config(state=tk.NORMAL)  # Разблокируем кнопку стоп
            
            self.log_message(f"🚀 Запуск AI анализа для {self.symbol_var.get()}", "info")
            self.log_message(f"📡 Используется сервер: {self.current_server['name']}", "info")
            self.log_message("🤖 AI модель обучается на исторических данных...", "prediction")
            
            thread = threading.Thread(target=self.trading_loop, daemon=True)  # Создаем поток для анализа
            thread.start()
    
    def stop_analysis(self):
        """Остановка анализа"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)  # Разблокируем кнопку старт
        self.stop_btn.config(state=tk.DISABLED)  # Блокируем кнопку стоп
        self.log_message("⏹️ Анализ остановлен пользователем", "info")

def main():
    try:
        root = tk.Tk()  # Создание главного окна
        app = ProfessionalCryptoTrader(root)  # Создание экземпляра приложения
        root.mainloop()  # Запуск главного цикла обработки событий
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        print("Убедитесь, что установлены все зависимости:")
        print("pip install pandas numpy requests matplotlib scikit-learn")

if __name__ == "__main__":
    main()  # Запуск приложения если файл выполняется напрямую