import customtkinter as ctk
import psutil
import threading
import time

# --- КОНСТАНТЫ СТИЛЯ (ДИЗАЙН) ---
BG_COLOR = "#1E1E24"         # Глубокий графитовый фон
SIDEBAR_COLOR = "#141419"    # Темный фон меню
ACCENT_BLUE = "#00A8E8"      # Неоновый синий акцент
TEXT_MUTED = "#7A7A85"       # Серый цвет для подписей

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройки главного окна
        self.title("PC Guardian & Monitor")
        self.geometry("1000x650")
        self.configure(fg_color=BG_COLOR)
        
        # Настройка сетки окна
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Переменные для хранения данных датчиков
        self.cpu_usage = 0
        self.ram_usage = 0

        # Боковое меню (Sidebar)
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Заголовок приложения
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="PC GUARDIAN", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=ACCENT_BLUE
        )
        self.logo_label.grid(row=0, column=0, padx=20, py=30)

        # Кнопки навигации
        self.btn_dashboard = self.create_menu_button("📊 Дашборд", row=1, command=self.show_dashboard)
        self.btn_processes = self.create_menu_button("⚙️ Процессы", row=2, command=self.show_processes)
        self.btn_threats = self.create_menu_button("🛡️ Анализ угроз", row=3, command=self.show_threats)
        self.btn_settings = self.create_menu_button("🔧 Настройки", row=4, command=self.show_settings)

        # Контейнер для экранов
        self.content_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", px=20, py=20)
        
        self.current_tab = None
        self.active_tab_name = ""
        
        # Запуск фонового потока для обновления системных данных
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.update_system_stats, daemon=True)
        self.monitor_thread.start()

        # При старте открываем Дашборд
        self.show_dashboard()

    def create_menu_button(self, text, row, command):
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text, 
            anchor="w", 
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color="#A3A3A3",
            hover_color="#23232A",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            command=command
        )
        btn.grid(row=row, column=0, sticky="ew", padx=15, py=5)
        return btn

    def set_active_button(self, active_btn):
        for btn in [self.btn_dashboard, self.btn_processes, self.btn_threats, self.btn_settings]:
            if btn == active_btn:
                btn.configure(fg_color="#23232A", text_color=ACCENT_BLUE, font=ctk.CTkFont(weight="bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#A3A3A3", font=ctk.CTkFont(weight="normal"))

    def clear_content(self):
        if self.current_tab is not None:
            self.current_tab.destroy()

    def update_system_stats(self):
        """Фоновая функция, которая собирает данные каждую секунду"""
        while self.is_running:
            self.cpu_usage = psutil.cpu_percent(interval=None)
            self.ram_usage = psutil.virtual_memory().percent
            
            # Безопасно обновляем элементы интерфейса, если мы на вкладке Дашборд
            if self.active_tab_name == "dashboard" and hasattr(self, 'cpu_progress'):
                try:
                    self.cpu_progress.set(self.cpu_usage / 100)
                    self.cpu_label.configure(text=f"{int(self.cpu_usage)}%")
                    
                    self.ram_progress.set(self.ram_usage / 100)
                    self.ram_label.configure(text=f"{int(self.ram_usage)}%")
                except Exception:
                    pass
            time.sleep(1)

    def show_dashboard(self):
        self.set_active_button(self.btn_dashboard)
        self.clear_content()
        self.active_tab_name = "dashboard"

        # Создаем контейнер для дашборда
        self.current_tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_tab.pack(fill="both", expand=True)

        # Заголовок вкладки
        title = ctk.CTkLabel(self.current_tab, text="Мониторинг системы в реальном времени", font=("Segoe UI", 22, "bold"))
        title.pack(anchor="w", py=10)

        # --- КАРТОЧКА CPU ---
        cpu_frame = ctk.CTkFrame(self.current_tab, fg_color="#141419", corner_radius=10, height=100)
        cpu_frame.pack(fill="x", py=10, px=5)
        
        cpu_title = ctk.CTkLabel(cpu_frame, text="Центральный процессор (CPU)", font=("Segoe UI", 14, "bold"))
        cpu_title.place(x=15, y=15)
        
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame, width=500, height=12, progress_color=ACCENT_BLUE)
        self.cpu_progress.place(x=15, y=50)
        self.cpu_progress.set(self.cpu_usage / 100)

        self.cpu_label = ctk.CTkLabel(cpu_frame, text=f"{int(self.cpu_usage)}%", font=("Segoe UI", 16, "bold"), text_color=ACCENT_BLUE)
        self.cpu_label.place(x=530, y=43)

        # --- КАРТОЧКА RAM ---
        ram_frame = ctk.CTkFrame(self.current_tab, fg_color="#141419", corner_radius=10, height=100)
        ram_frame.pack(fill="x", py=10, px=5)
        
        ram_title = ctk.CTkLabel(ram_frame, text="Оперативная память (RAM)", font=("Segoe UI", 14, "bold"))
        ram_title.place(x=15, y=15)
        
        self.ram_progress = ctk.CTkProgressBar(ram_frame, width=500, height=12, progress_color="#00D26A")
        self.ram_progress.place(x=15, y=50)
        self.ram_progress.set(self.ram_usage / 100)

        self.ram_label = ctk.CTkLabel(ram_frame, text=f"{int(self.ram_usage)}%", font=("Segoe UI", 16, "bold"), text_color="#00D26A")
        self.ram_label.place(x=530, y=43)

    def show_processes(self):
        self.set_active_button(self.btn_processes)
        self.clear_content()
        self.active_tab_name = "processes"
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Диспетчер процессов (В разработке)", font=("Segoe UI", 18))
        self.current_tab.pack(pady=50)

    def show_threats(self):
        self.set_active_button(self.btn_threats)
        self.clear_content()
        self.active_tab_name = "threats"
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Анализатор скрытых майнеров (Будет на Шаге 3)", font=("Segoe UI", 18))
        self.current_tab.pack(pady=50)

    def show_settings(self):
        self.set_active_button(self.btn_settings)
        self.clear_content()
        self.active_tab_name = "settings"
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Настройки приложения", font=("Segoe UI", 18))
        self.current_tab.pack(pady=50)

    def destroy(self):
        self.is_running = False  # Останавливаем фоновый поток при закрытии
        super().destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()
