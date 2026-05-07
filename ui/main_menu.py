import customtkinter as ctk
from ui.lab1_ui import Lab1Frame
from ui.lab2_ui import Lab2Frame
from ui.lab3_ui import Lab3Frame
from ui.lab4_ui import Lab4Frame
from ui.lab5_ui import Lab5Frame


ctk.set_appearance_mode("light")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My Labs - Cryptography")
        self.geometry("1000x700")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1E293B")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo = ctk.CTkLabel(self.sidebar, text="LABS MENU", text_color="white",
                                 font=("Arial", 18, "bold"))
        self.logo.pack(pady=30)

        self.btn_lab1 = ctk.CTkButton(self.sidebar, text="Лабораторна №1",
                                      fg_color="#334155", hover_color="#475569",
                                      command=self.show_lab1)
        self.btn_lab1.pack(pady=10, padx=20, fill="x")

        self.btn_lab2 = ctk.CTkButton(self.sidebar, text="Лабораторна №2",
                                      fg_color="#334155", hover_color="#475569",
                                      command=self.show_lab2)
        self.btn_lab2.pack(pady=10, padx=20, fill="x")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.current_frame = None
        self.show_lab1()

        self.btn_lab3 = ctk.CTkButton(self.sidebar, text="Лабораторна №3",
                                      fg_color="#334155", command=self.show_lab3)
        self.btn_lab3.pack(pady=10, padx=20, fill="x")

        self.btn_lab4 = ctk.CTkButton(self.sidebar, text="Лабораторна №4",
                                      fg_color="#334155", command=self.show_lab4)
        self.btn_lab4.pack(pady=10, padx=20, fill="x")

        self.btn_lab5 = ctk.CTkButton(self.sidebar, text="Лабораторна №5",
                                  fg_color="#334155", command=self.show_lab5)
        self.btn_lab5.pack(pady=10, padx=20, fill="x")
    def show_lab1(self):
        self._switch_frame(Lab1Frame)
        self._highlight_button(self.btn_lab1)

    def show_lab2(self):
        self._switch_frame(Lab2Frame)
        self._highlight_button(self.btn_lab2)

    def show_lab3(self):
        self._switch_frame(Lab3Frame)
        self._highlight_button(self.btn_lab3)

    def show_lab4(self):
        self._switch_frame(Lab4Frame)
        self._highlight_button(self.btn_lab4)

    def show_lab5(self):
        self._switch_frame(Lab5Frame)
        self._highlight_button(self.btn_lab5)

    def _switch_frame(self, frame_class):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.container)
        self.current_frame.pack(fill="both", expand=True)

    def _highlight_button(self, active_btn):
        self.btn_lab1.configure(fg_color="#334155")
        self.btn_lab2.configure(fg_color="#334155")
        active_btn.configure(fg_color="#3B82F6")

def start_app():
    app = MainApp()
    app.mainloop()

if __name__ == "__main__":
    start_app()