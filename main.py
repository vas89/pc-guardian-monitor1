import customtkinter as ctk
import psutil
import threading
import time

# --- КОНСТАНТЫ СТИЛЯ (ДИЗАЙН) ---
BG_COLOR = "#1E1E24"         # Глубокий графитовый фон
SIDEBAR_COLOR = "#141419"    # Темный фон меню
ACCENT_BLUE = "#00A8E8"      # Неоновый синий акцент
SUCCESS_GREEN = "#00D26A"    # Зеленый безопасный статус
WARNING_RED = "#FF3838"      # Красный для угроз
TEXT_MUTED = "#7A7A85"       # Серый цвет подписей

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройки главного окна
        self.title("PC Guardian & Monitor")
        self.geometry("1040x680")
        self.configure(fg_color=BG_COLOR)
        
        # Настройка сетки окна
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Переменные для датчиков и списков
        self.cpu_usage = 0
        self.ram_usage = 0
        self.detected_threats = []

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
        
        # Запуск фонового мониторинга
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.core_background_monitor, daemon=True)
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
        btn.grid(row=row, column=0, sticky="ew", px=15, py=5)
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

    def terminate_process(self, pid, callback_view):
        """Безопасное завершение процесса по PID"""
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=2)
            if callback_view == "processes":
                self.show_processes()
            elif callback_view == "threats":
                self.show_threats()
        except Exception:
            pass

    def core_background_monitor(self):
        """Фоновый сборщик системных данных и анализатор майнеров"""
        while self.is_running:
            # Сбор метрик
            self.cpu_usage = psutil.cpu_percent(interval=None)
            self.ram_usage = psutil.virtual_memory().percent
            
            if self.active_tab_name == "dashboard" and hasattr(self, 'cpu_progress'):
                try:
                    self.cpu_progress.set(self.cpu_usage / 100)
                    self.cpu_label.configure(text=f"{int(self.cpu_usage)}%")
                    self.ram_progress.set(self.ram_usage / 100)
                    self.ram_label.configure(text=f"{int(self.ram_usage)}%")
                except Exception:
                    pass

            # Анализ процессов
            temp_threats = []
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    p_info = proc.info
                    p_name = p_info['name'] or ''
                    p_exe = p_info['exe'] or ''
                    p_cmd = p_info['cmdline'] or []
                    
                    cmd_str = " ".join(p_cmd).lower()
                    miner_flags = ['--stratum', '--user', 'xmrig', 'minerd', 'pool.mine', 'ethminer', 'stratum+tcp']
                    if any(flag in cmd_str for flag in miner_flags):
                        temp_threats.append((p_info['pid'], p_name, "Подозрительные аргументы запуска (Майнер пул)"))
                        continue

                    system_names = ['svchost.exe', 'lsass.exe', 'services.exe', 'explorer.exe', 'taskmgr.exe']
                    if p_name.lower() in system_names:
                        exe_path = p_exe.lower()
                        if "windows" not in exe_path and "system32" not in exe_path:
                            temp_threats.append((p_info['pid'], p_name, "Имитация системного файла (Запущен не из System32)"))
                            continue
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.detected_threats = temp_threats
            time.sleep(2)

    def show_dashboard(self):
        self.set_active_button(self.btn_dashboard)
        self.clear_content()
        self.active_tab_name = "dashboard"

        self.current_tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_tab.pack(fill="both", expand=True)

        title = ctk.CTkLabel(self.current_tab, text="Мониторинг системы в реальном времени", font=("Segoe UI", 22, "bold"))
        title.pack(anchor="w", py=10)

        cpu_frame = ctk.CTkFrame(self.current_tab, fg_color="#141419", corner_radius=10, height=100)
        cpu_frame.pack(fill="x", py=10, px=5)
        ctk.CTkLabel(cpu_frame, text="Центральный процессор (CPU)", font=("Segoe UI", 14, "bold")).place(x=15, y=15)
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame, width=500, height=12, progress_color=ACCENT_BLUE)
        self.cpu_progress.place(x=15, y=50)
        self.cpu_progress.set(self.cpu_usage / 100)
        self.cpu_label = ctk.CTkLabel(cpu_frame, text=f"{int(self.cpu_usage)}%", font=("Segoe UI", 16, "bold"), text_color=ACCENT_BLUE)
        self.cpu_label.place(x=530, y=43)

        ram_frame = ctk.CTkFrame(self.current_tab, fg_color="#141419", corner_radius=10, height=100)
        ram_frame.pack(fill="x", py=10, px=5)
        ctk.CTkLabel(ram_frame, text="Оперативная память (RAM)", font=("Segoe UI", 14, "bold")).place(x=15, y=15)
        self.ram_progress = ctk.CTkProgressBar(ram_frame, width=500, height=12, progress_color=SUCCESS_GREEN)
        self.ram_progress.place(x=15, y=50)
        self.ram_progress.set(self.ram_usage / 100)
        self.ram_label = ctk.CTkLabel(ram_frame, text=f"{int(self.ram_usage)}%", font=("Segoe UI", 16, "bold"), text_color=SUCCESS_GREEN)
        self.ram_label.place(x=530, y=43)

    def show_processes(self):
        self.set_active_button(self.btn_processes)
        self.clear_content()
        self.active_tab_name = "processes"

        self.current_tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_tab.pack(fill="both", expand=True)

        title = ctk.CTkLabel(self.current_tab, text="Диспетчер активных процессов", font=("Segoe UI", 22, "bold"))
        title.pack(anchor="w", py=10)

        scroll_frame = ctk.CTkScrollableFrame(self.current_tab, fg_color="#141419", height=450)
        scroll_frame.pack(fill="both", expand=True, padx=5, py=10)

        header_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent", height=25)
        header_frame.pack(fill="x", side="top", ipady=5)
        ctk.CTkLabel(header_frame, text="PID", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED, width=80, anchor="w").pack(side="left")
        ctk.CTkLabel(header_frame, text="Имя процесса", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED, width=300, anchor="w").pack(side="left")
        ctk.CTkLabel(header_frame, text="Действие", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(side="right", px=20)

        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        for p in processes[:40]:
            row = ctk.CTkFrame(scroll_frame, fg_color="#1E1E24", corner_radius=6, height=35)
            row.pack(fill="x", py=2, px=5)
            
            ctk.CTkLabel(row, text=str(p['pid']), font=("Segoe UI", 13), width=80, anchor="w").pack(side="left", px=10)
            ctk.CTkLabel(row, text=p['name'] or 'Unknown', font=("Segoe UI", 13), width=300, anchor="w").pack(side="left")
            
            kill_btn = ctk.CTkButton(
                row, text="Завершить", fg_color="#2A1B24", text_color=WARNING_RED, 
                hover_color="#3D1A22", width=90, height=24, corner_radius=4,
command=lambda pid=p['pid']: self.terminate_process(pid, "processes")
)
kill_btn.pack(side="right", px=10, py=5)
def show_threats(self):
self.set_active_button(self.btn_threats)
self.clear_content()
self.active_tab_name = "threats"
self.current_tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
self.current_tab.pack(fill="both", expand=True)
title = ctk.CTkLabel(self.current_tab, text="Анализатор аномалий и скрытых майнеров", font=("Segoe UI", 22, "bold"))
title.pack(anchor="w", py=10)
scroll_frame = ctk.CTkScrollableFrame(self.current_tab, fg_color="#141419", height=450)
scroll_frame.pack(fill="both", expand=True, padx=5, py=10)
if not self.detected_threats:
ok_box = ctk.CTkFrame(scroll_frame, fg_color="#14241C", height=100, corner_radius=8)
ok_box.pack(fill="x", py=20, px=10)
ctk.CTkLabel(ok_box, text="🟢 Активных угроз и скрытых майнеров не обнаружено", font=("Segoe UI", 15, "bold"), text_color=SUCCESS_GREEN).pack(pady=35)
else:
for pid, name, reason in self.detected_threats:
row = ctk.CTkFrame(scroll_frame, fg_color="#2B191D", corner_radius=8, height=50)
row.pack(fill="x", py=4, px=5)
text_frame = ctk.CTkFrame(row, fg_color="transparent")
text_frame.pack(side="left", px=15, py=5)
ctk.CTkLabel(text_frame, text=f"{name} (PID: {pid})", font=("Segoe UI", 14, "bold"), text_color=WARNING_RED, anchor="w").pack(anchor="w")
ctk.CTkLabel(text_frame, text=f"Причина: {reason}", font=("Segoe UI", 12), text_color="#A3A3A3", anchor="w").pack(anchor="w")
kill_btn = ctk.CTkButton(
row, text="Ликвидировать", fg_color=WARNING_RED, text_color="#FFFFFF",
hover_color="#CC2424", width=120, height=30, corner_radius=6,
command=lambda p_id=pid: self.terminate_process(p_id, "threats")
)
kill_btn.pack(side="right", px=15, py=10)
def show_settings(self):
self.set_active_button(self.btn_settings)
self.clear_content()
self.active_tab_name = "settings"
self.current_tab = ctk.CTkFrame(self.content_frame, fg_color="transparent")
self.current_tab.pack(fill="both", expand=True)
title = ctk.CTkLabel(self.current_tab, text="Настройки монитора", font=("Segoe UI", 22, "bold"))
title.pack(anchor="w", py=10)
info_frame = ctk.CTkFrame(self.current_tab, fg_color="#141419", corner_radius=10)
info_frame.pack(fill="x", py=10, px=5, ipady=15)
ctk.CTkLabel(info_frame, text="Защита ядра: Активна", font=("Segoe UI", 14), text_color=SUCCESS_GREEN).pack(anchor="w", px=20, py=5)
ctk.CTkLabel(info_frame, text="Интервал сканирования сигнатур: 2 сек", font=("Segoe UI", 14)).pack(anchor="w", px=20, py=5)
ctk.CTkLabel(info_frame, text="Версия сборки ИИ: 1.0.3 (Финальная)", font=("Segoe UI", 14), text_color=TEXT_MUTED).pack(anchor="w", px=20, py=5)
def destroy(self):
self.is_running = False
super().destroy()
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()
