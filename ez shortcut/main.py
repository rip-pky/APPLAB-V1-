import os
import shutil
import tkinter as tk
from tkinter import messagebox
import winshell
import customtkinter as ctk
import ctypes
from PIL import Image, ImageTk
import win32ui
import win32gui
import webbrowser

# Configuração do tema MD3-like
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppLab(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AppLab - Gerenciador de Aplicativos")
        self.geometry("900x600")

        self.apps = {} 
        self.selected_app_name = None

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (Barra Lateral)
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="AppLab", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Buscar programa...")
        self.search_entry.pack(pady=10, padx=10, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_apps)

        # Botões de Ação na Sidebar
        self.btn_run = ctk.CTkButton(self.sidebar, text="Executar", command=self.run_app, fg_color="#4CAF50", hover_color="#388E3C")
        self.btn_run.pack(pady=10, padx=20, fill="x")

        self.btn_admin = ctk.CTkButton(self.sidebar, text="Executar (Adm)", command=lambda: self.run_app(admin=True), fg_color="#F44336", hover_color="#D32F2F")
        self.btn_admin.pack(pady=10, padx=20, fill="x")

        self.btn_folder = ctk.CTkButton(self.sidebar, text="Abrir Local", command=self.open_file_location, fg_color="#FF9800", hover_color="#F57C00")
        self.btn_folder.pack(pady=10, padx=20, fill="x")

        self.btn_desktop = ctk.CTkButton(self.sidebar, text="Add Desktop", command=self.add_to_desktop)
        self.btn_desktop.pack(pady=10, padx=20, fill="x")

        self.btn_properties = ctk.CTkButton(self.sidebar, text="Propriedades", command=self.show_properties, fg_color="#9C27B0", hover_color="#7B1FA2")
        self.btn_properties.pack(pady=10, padx=20, fill="x")

        self.btn_refresh = ctk.CTkButton(self.sidebar, text="Atualizar Lista", command=self.load_apps, fg_color="transparent", border_width=2, border_color="#1f538d")
        self.btn_refresh.pack(pady=(20, 10), padx=20, fill="x")

        self.btn_about = ctk.CTkButton(self.sidebar, text="Sobre", command=self.show_about, fg_color="transparent", text_color="#888888")
        self.btn_about.pack(side="bottom", pady=20, padx=20, fill="x")

        # Área Principal de Conteúdo
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.content_frame, text="Programas Instalados", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Lista de Apps (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#1a1a1a", corner_radius=10)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.app_buttons = []

        self.load_apps()

    def get_icon(self, path, size=32):
        """Extrai o ícone de um arquivo .lnk ou .exe"""
        try:
            shell = ctypes.windll.shell32
            h_icon = ctypes.c_void_p()
            if shell.ExtractIconExW(path, 0, None, ctypes.byref(h_icon), 1):
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, size, size)
                hdc = hdc.CreateCompatibleDC()
                hdc.SelectObject(hbmp)
                hdc.DrawIcon((0, 0), h_icon.value)
                
                bmpinfo = hbmp.GetInfo()
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)
                win32gui.DestroyIcon(h_icon.value)
                return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        except:
            pass
        return None

    def load_apps(self):
        paths = [
            os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]

        self.apps.clear()
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.app_buttons = []

        for path in paths:
            if os.path.exists(path):
                for root_dir, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(".lnk"):
                            name = file.replace(".lnk", "")
                            full_path = os.path.join(root_dir, file)
                            if name not in self.apps:
                                self.apps[name] = full_path
        
        self.render_apps()

    def render_apps(self, filter_text=""):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.app_buttons = []

        for name, path in self.apps.items():
            if filter_text.lower() in name.lower():
                icon = self.get_icon(path)
                btn = ctk.CTkButton(
                    self.scroll_frame, 
                    text=name, 
                    image=icon, 
                    anchor="w", 
                    fg_color="transparent", 
                    text_color="white",
                    hover_color="#2b2b2b",
                    height=45,
                    command=lambda n=name: self.select_app(n)
                )
                btn.pack(fill="x", pady=2, padx=5)
                # Bind de Clique Duplo
                btn.bind("<Double-Button-1>", lambda e, n=name: self.on_double_click(n))
                self.app_buttons.append(btn)

    def on_double_click(self, name):
        self.select_app(name)
        self.run_app()

    def select_app(self, name):
        self.selected_app_name = name
        # Destacar o selecionado
        for btn in self.app_buttons:
            if btn.cget("text") == name:
                btn.configure(fg_color="#1f538d")
            else:
                btn.configure(fg_color="transparent")

    def filter_apps(self, event):
        self.render_apps(self.search_entry.get())

    def get_selected_app(self):
        if self.selected_app_name:
            return self.selected_app_name, self.apps[self.selected_app_name]
        return None

    def run_app(self, admin=False):
        selected = self.get_selected_app()
        if selected:
            name, path = selected
            try:
                if admin:
                    # Executa como Administrador usando ShellExecute
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)
                else:
                    os.startfile(path)
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o programa: {e}")

    def show_properties(self):
        selected = self.get_selected_app()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um programa primeiro.")
            return

        name, path = selected
        try:
            shortcut = winshell.shortcut(path)
            
            # Janela de propriedades estilo MD3
            prop_win = ctk.CTkToplevel(self)
            prop_win.title(f"Propriedades - {name}")
            prop_win.geometry("500x380")
            prop_win.after(100, lambda: prop_win.focus()) # Garante que a janela apareça na frente

            ctk.CTkLabel(prop_win, text="Propriedades do Atalho", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
            
            frame = ctk.CTkFrame(prop_win, fg_color="#2b2b2b")
            frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

            def add_row(label, text):
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=5)
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=100, anchor="w").pack(side="left")
                entry = ctk.CTkEntry(row)
                entry.insert(0, str(text))
                entry.configure(state="readonly") # Apenas leitura mas permite copiar
                entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

            add_row("Nome:", name)
            add_row("Destino:", shortcut.path)
            add_row("Início em:", shortcut.working_directory)
            add_row("Descrição:", shortcut.description or "N/A")
            add_row("Arquivo:", path)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler propriedades: {e}")

    def open_file_location(self):
        selected = self.get_selected_app()
        if selected:
            _, path = selected
            try:
                # Winshell pega o alvo real do atalho
                target = winshell.shortcut(path).path
                if not target: target = path
                os.system(f'explorer /select,"{target}"')
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir a pasta: {e}")

    def add_to_desktop(self):
        selected = self.get_selected_app()
        if selected:
            name, path = selected
            try:
                desktop = winshell.desktop()
                destination = os.path.join(desktop, os.path.basename(path))
                shutil.copy(path, destination)
                messagebox.showinfo("Sucesso", f"Atalho para '{name}' criado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar atalho: {e}")

    def show_about(self):
        about_win = ctk.CTkToplevel(self)
        about_win.title("Sobre - AppLab")
        about_win.geometry("450x220")
        about_win.resizable(False, False)
        about_win.after(100, lambda: about_win.focus())
        about_win.attributes("-topmost", True)

        # Frame principal com bordas arredondadas
        frame = ctk.CTkFrame(about_win, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Container central para alinhar foto e texto
        content_layout = ctk.CTkFrame(frame, fg_color="transparent")
        content_layout.pack(expand=True)

        # --- Espaço para a foto do asset ---
        # Para usar sua foto, salve um arquivo como 'asset.png' na pasta do projeto e descomente as linhas abaixo:
        # try:
        #     img = ctk.CTkImage(Image.open("asset.png"), size=(80, 80))
        #     ctk.CTkLabel(content_layout, image=img, text="").pack(side="left", padx=(0, 20))
        # except:
        #     pass

        # Coluna de Informações
        info = ctk.CTkFrame(content_layout, fg_color="transparent")
        info.pack(side="left")

        ctk.CTkLabel(info, text="AppLab v1", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info, text="by: juu.dev", font=ctk.CTkFont(size=14, slant="italic")).pack(anchor="w")

        link = ctk.CTkLabel(info, text="GitHub: rip-pky", text_color="#1f538d", cursor="hand2", font=ctk.CTkFont(underline=True))
        link.pack(anchor="w", pady=(15, 0))
        link.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/rip-pky"))

if __name__ == "__main__":
    app = AppLab()
    app.mainloop()
