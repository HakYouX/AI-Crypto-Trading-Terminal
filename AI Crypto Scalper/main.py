import tkinter as tk
from ui.main_window import ProfessionalCryptoTrader

def main():
    try:
        root = tk.Tk()
        app = ProfessionalCryptoTrader(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        print("Убедитесь, что установлены все зависимости:")
        print("pip install pandas numpy requests matplotlib scikit-learn")

if __name__ == "__main__":
    main()