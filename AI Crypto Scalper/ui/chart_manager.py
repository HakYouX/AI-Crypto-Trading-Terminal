import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import COLORS

class ChartManager(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg'])
        self.colors = COLORS
        
        self.setup_chart()
        
    def setup_chart(self):
        """Инициализация графика"""
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
        self.chart_canvas = FigureCanvasTkAgg(self.fig, self)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Инициализируем пустой график
        self.ax.clear()
        self.ax.set_title('Загрузка данных...', color=self.colors['text'], pad=20)
        self.ax.set_xlabel('', color=self.colors['text'])
        self.ax.set_ylabel('Цена (USDT)', color=self.colors['text'])
        self.ax.grid(True, alpha=0.2)
        self.chart_canvas.draw()
        
    def update_chart(self, df, symbol, chart_type, show_predictions, future_prices=None, signal=None, signal_price=None):
        """Обновление графика с AI предсказаниями"""
        if df is None or len(df) < 20:
            return
            
        self.ax.clear()
        
        # Основной график (последние 50 свечей)
        display_data = df.tail(50).copy()
        current_price = display_data['close'].iloc[-1]
        
        # ОСНОВНОЙ ГРАФИК
        if chart_type == "candles":
            # Свечной график
            for i, (idx, row) in enumerate(display_data.iterrows()):
                color = '#22c55e' if row['close'] >= row['open'] else '#ef4444'
                
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
        if show_predictions and future_prices is not None:
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
            
            # Зона уверенности предсказаний
            if len(future_prices) > 0:
                confidence_band = np.array(future_prices) * 0.02
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
            marker = '^' if signal == "BUY" else 'v'
            
            last_idx = len(display_data) - 1
            self.ax.scatter(last_idx, current_price,
                           color=color, marker=marker, s=200, zorder=10,
                           edgecolors='white', linewidth=2.5,
                           label=f'{signal} сигнал')
        
        # НАСТРОЙКА ГРАФИКА
        self.ax.set_title(f'{symbol} | BYBIT | Real-time + AI Predictions', 
                         color=self.colors['text'], fontsize=14, pad=20, fontweight='bold')
        self.ax.set_ylabel('Цена (USDT)', color=self.colors['text'], fontsize=12)
        self.ax.grid(True, alpha=0.2, linestyle='-')
        self.ax.set_xticks([])
        self.ax.tick_params(colors=self.colors['text'], labelsize=10)
        
        # ЛЕГЕНДА
        self.ax.legend(facecolor=self.colors['card_bg'], 
                      edgecolor=self.colors['card_bg'],
                      fontsize=9, loc='upper left',
                      framealpha=0.9)
        
        # ИНФОРМАЦИЯ О ЦЕНЕ
        if len(display_data) > 1:
            price_change = current_price - display_data['close'].iloc[-2]
            change_percent = (price_change / display_data['close'].iloc[-2] * 100)
        else:
            price_change = 0
            change_percent = 0
            
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
        
        if future_prices is not None and show_predictions and len(future_prices) > 0:
            y_min = min(y_min, min(future_prices) * 0.998)
            y_max = max(y_max, max(future_prices) * 1.002)
        
        # Добавляем небольшой отступ
        price_range = y_max - y_min
        self.ax.set_ylim(bottom=y_min - price_range * 0.02, top=y_max + price_range * 0.02)
        
        self.chart_canvas.draw()