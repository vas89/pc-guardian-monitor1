import customtkinter as ctk

# --- КОНСТАНТЫ СТИЛЯ (ДИЗАЙН) ---
BG_COLOR = "#1E1E24"         # Глубокий графитовый фон
SIDEBAR_COLOR = "#141419"    # Темный фон меню
ACCENT_BLUE = "#00A8E8"      # Неоновый синий акцент

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
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, py=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.current_tab = None
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

    def show_dashboard(self):
        self.set_active_button(self.btn_dashboard)
        self.clear_content()
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Экран Дашборда (В разработке на Шаге 2)", font=("Segoe UI", 18))
        self.current_tab.grid(row=0, column=0)

    def show_processes(self):
        self.set_active_button(self.btn_processes)
        self.clear_content()
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Диспетчер процессов (В разработке)", font=("Segoe UI", 18))
        self.current_tab.grid(row=0, column=0)

    def show_threats(self):
        self.set_active_button(self.btn_threats)
        self.clear_content()
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Анализатор скрытых майнеров (В разработке на Шаге 3)", font=("Segoe UI", 18))
        self.current_tab.grid(row=0, column=0)

    def show_settings(self):
        self.set_active_button(self.btn_settings)
        self.clear_content()
        self.current_tab = ctk.CTkLabel(self.content_frame, text="Настройки приложения", font=("Segoe UI", 18))
        self.current_tab.grid(row=0, column=0)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()
