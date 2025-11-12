import tkinter as tk
from datetime import datetime

class TradingLogger:
    def __init__(self):
        pass
        
    def log_message(self, log_widget, message, signal_type="info", colors=None):
        """Логирование с цветовым кодированием"""
        if colors is None:
            colors = {
                'text': '#e2e8f0',
                'buy': '#22c55e',
                'sell': '#ef4444', 
                'error': '#ef4444',
                'warning': '#eab308',
                'prediction': '#8b5cf6'
            }
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "buy": colors.get('buy', '#22c55e'),
            "sell": colors.get('sell', '#ef4444'), 
            "info": colors.get('text', '#e2e8f0'),
            "error": colors.get('error', '#ef4444'),
            "warning": colors.get('warning', '#eab308'),
            "prediction": colors.get('prediction', '#8b5cf6')
        }
        
        tag = signal_type.upper()
        color = color_map.get(signal_type, colors.get('text', '#e2e8f0'))
        
        log_widget.insert(tk.END, f"[{timestamp}] {message}\n")
        
        if signal_type in ["buy", "sell", "error", "warning", "prediction"]:
            start_index = f"{log_widget.index('end-2c')}"
            log_widget.tag_add(tag, start_index, "end-1c")
            log_widget.tag_config(tag, foreground=color, font=("Consolas", 9, "bold"))
        
        log_widget.see(tk.END)  # Автопрокрутка к новым сообщениями