import requests
import pandas as pd
import time

class DataProvider:
    def __init__(self, server):
        self.server = server
        
    def set_server(self, server):
        """Установка сервера"""
        self.server = server
        
    def measure_ping(self):
        """Измерение пинга до сервера BYBIT"""
        try:
            server_url = self.server['url']
            
            start_time = time.time()
            response = requests.get(f'{server_url}/v5/market/time', timeout=3)
            
            if response.status_code == 200:
                ping_time = int((time.time() - start_time) * 1000)
                return ping_time
            else:
                return None
                
        except Exception as e:
            return None
    
    def get_market_data(self, symbol, interval='1', limit=100):
        """Получение рыночных данных с BYBIT"""
        try:
            url = f"{self.server['url']}/v5/market/kline"
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
            print(f"Ошибка получения данных: {e}")
            return None