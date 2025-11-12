# Цветовая схема
COLORS = {
    'bg': '#0d1421',
    'card_bg': '#1e293b',
    'text': '#e2e8f0',
    'accent': '#3b82f6',
    'buy': '#22c55e',
    'sell': '#ef4444',
    'profit': '#10b981',
    'loss': '#ef4444',
    'prediction': '#8b5cf6',
    'error': '#ef4444',        # Добавляем недостающие цвета
    'warning': '#eab308'       # Добавляем недостающие цвета
}

# Серверы BYBIT
BYBIT_SERVERS = [
    {'name': 'Европа (Лондон)', 'url': 'https://api.bybit.com'},
    {'name': 'Сингапур', 'url': 'https://api.bybit.com'},
    {'name': 'США', 'url': 'https://api.bybit.com'},
]

# Популярные торговые пары
POPULAR_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
    "DOGEUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT", "BNBUSDT",
    "AVAXUSDT", "LINKUSDT", "ATOMUSDT", "UNIUSDT", "XLMUSDT"
]

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    'commission': 0.1,
    'min_profit': 0.2,
    'aggressiveness': 0.7,
    'prediction_length': 5,
    'show_predictions': True,
    'chart_type': 'candles'
}