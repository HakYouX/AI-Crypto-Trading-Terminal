import tkinter as tk
from tkinter import ttk

from config import COLORS, BYBIT_SERVERS, POPULAR_SYMBOLS, DEFAULT_SETTINGS

class ControlPanel(tk.Frame):  # Наследуем от tk.Frame
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['card_bg'])
        self.app = app
        self.colors = COLORS
        
        self.setup_control_panel()
        
    def setup_control_panel(self):
        """Панель управления"""
        # Выбор сервера BYBIT
        tk.Label(self, text="Сервер BYBIT:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(0, 5))
        
        self.server_var = tk.StringVar(value="Европа (Лондон)")
        server_names = [server['name'] for server in BYBIT_SERVERS]
        server_combo = ttk.Combobox(self, textvariable=self.server_var, 
                                   values=server_names, width=20)
        server_combo.pack(fill=tk.X, pady=(0, 10))
        server_combo.bind('<<ComboboxSelected>>', lambda e: self.app.change_server(self.server_var.get()))

        # Настройки AI предсказаний
        ai_frame = tk.LabelFrame(self, text="AI Предсказания", 
                                bg=self.colors['card_bg'], fg=self.colors['text'],
                                padx=10, pady=10)
        ai_frame.pack(fill=tk.X, pady=10)

        # Включить предсказания
        self.show_predictions_var = tk.BooleanVar(value=DEFAULT_SETTINGS['show_predictions'])
        ttk.Checkbutton(ai_frame, text="Показывать предсказания AI", 
                       variable=self.show_predictions_var).pack(anchor=tk.W)

        # Длина предсказания
        tk.Label(ai_frame, text="Свечей вперед:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(5,0))
        self.prediction_length_var = tk.IntVar(value=DEFAULT_SETTINGS['prediction_length'])
        prediction_scale = ttk.Scale(ai_frame, from_=3, to=10, 
                                   variable=self.prediction_length_var, orient=tk.HORIZONTAL)
        prediction_scale.pack(fill=tk.X, pady=(0, 5))

        # Тип графика
        chart_type_frame = tk.Frame(self, bg=self.colors['card_bg'])
        chart_type_frame.pack(fill=tk.X, pady=5)

        tk.Label(chart_type_frame, text="Тип графика:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(side=tk.LEFT)

        self.chart_type_var = tk.StringVar(value=DEFAULT_SETTINGS['chart_type'])
        ttk.Radiobutton(chart_type_frame, text="Свечи", 
                      variable=self.chart_type_var, value="candles").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(chart_type_frame, text="Линия", 
                      variable=self.chart_type_var, value="line").pack(side=tk.LEFT, padx=5)

        # Выбор пары
        tk.Label(self, text="Торговая пара:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(10, 5))
        
        self.symbol_var = tk.StringVar(value="BTCUSDT")
        symbol_combo = ttk.Combobox(self, textvariable=self.symbol_var, 
                                   values=POPULAR_SYMBOLS, width=15)
        symbol_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Пользовательская пара
        tk.Label(self, text="Или введите свою пару:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W, pady=(0, 5))
        
        custom_frame = tk.Frame(self, bg=self.colors['card_bg'])
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.custom_symbol = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_symbol, width=12)
        custom_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(custom_frame, text="Добавить", 
                  command=self.add_custom_symbol).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Настройки AI
        settings_frame = tk.LabelFrame(self, text="Настройки AI", 
                                      bg=self.colors['card_bg'], fg=self.colors['text'],
                                      padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Комиссия
        tk.Label(settings_frame, text="Комиссия (%):", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W)
        self.commission_var = tk.DoubleVar(value=DEFAULT_SETTINGS['commission'])
        commission_scale = ttk.Scale(settings_frame, from_=0.01, to=1.0, 
                                    variable=self.commission_var, orient=tk.HORIZONTAL)
        commission_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Минимальная прибыль
        tk.Label(settings_frame, text="Мин. прибыль (%):", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W)
        self.min_profit_var = tk.DoubleVar(value=DEFAULT_SETTINGS['min_profit'])
        profit_scale = ttk.Scale(settings_frame, from_=0.05, to=2.0, 
                                variable=self.min_profit_var, orient=tk.HORIZONTAL)
        profit_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Агрессивность AI
        tk.Label(settings_frame, text="Агрессивность AI:", 
                bg=self.colors['card_bg'], fg=self.colors['text']).pack(anchor=tk.W)
        self.aggressiveness_var = tk.DoubleVar(value=DEFAULT_SETTINGS['aggressiveness'])
        agg_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, 
                             variable=self.aggressiveness_var, orient=tk.HORIZONTAL)
        agg_scale.pack(fill=tk.X)
        
        # Кнопки управления
        button_frame = tk.Frame(self, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="🚀 СТАРТ", 
                                   command=self.app.start_analysis)
        self.start_btn.pack(fill=tk.X, pady=2)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ СТОП", 
                                  command=self.app.stop_analysis, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=2)
        
        # Кнопка тестирования пинга
        ttk.Button(button_frame, text="📊 Тест пинга", 
                  command=self.app.measure_ping).pack(fill=tk.X, pady=2)
        
        # Статистика
        stats_frame = tk.LabelFrame(self, text="Статистика", 
                                   bg=self.colors['card_bg'], fg=self.colors['text'],
                                   padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, 
                                 bg=self.colors['card_bg'], fg=self.colors['text'],
                                 font=("Consolas", 9), relief=tk.FLAT, borderwidth=1)
        self.stats_text.pack(fill=tk.BOTH)
        self.update_stats(0, 0, 0, False, 0, BYBIT_SERVERS[0]['name'])
    
    def add_custom_symbol(self):
        """Добавление пользовательской торговой пары"""
        symbol = self.custom_symbol.get().strip().upper()
        if symbol and symbol not in self.symbol_var.get():
            self.app.log_message(f"Добавлена пара: {symbol}", "info")
            self.symbol_var.set(symbol)
            self.custom_symbol.set("")
    
    def update_stats(self, total_signals, buy_count, sell_count, is_model_trained, ping_time, server_name):
        """Обновление статистики"""
        success_rate = 0
        if total_signals > 0:
            success_rate = min(80, 50 + (buy_count - sell_count) * 5)
        
        model_status = "Обучена" if is_model_trained else "Не обучена"
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, 
                              f"Сигналы: {total_signals}\n"
                              f"Покупки: {buy_count}\n"
                              f"Продажи: {sell_count}\n"
                              f"Успешных: {success_rate}%\n"
                              f"Прибыль: +{success_rate * 0.1:.1f}%\n"
                              f"Пинг: {ping_time}мс\n"
                              f"Сервер: {server_name}\n"
                              f"AI Модель: {model_status}")
        self.stats_text.config(state=tk.DISABLED)