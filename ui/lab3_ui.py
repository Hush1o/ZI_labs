import customtkinter as ctk
from tkinter import filedialog
import os
from labs import lab3

FRAME_COLOR = "#F0F4F8"
BUTTON_COLOR = "#3B82F6"
TEXT_COLOR = "#1E293B"


class Lab3Frame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(self, text="RC5 Encryption (16 Variant)",
                                  font=("Segoe UI", 24, "bold"), text_color=TEXT_COLOR)
        self.label.pack(pady=15)

        self.info_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        self.info_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(self.info_frame, text="Параметри варіанту: w=16, r=20, b=8",
                     font=("Segoe UI", 13, "italic"), text_color="#64748B").pack(pady=5)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Введіть парольну фразу для MD5",
                                       show="*", height=40)
        self.pass_entry.pack(padx=20, pady=10, fill="x")

        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=10)

        self.btn_enc = ctk.CTkButton(btn_container, text="ЗАШИФРУВАТИ", fg_color=BUTTON_COLOR,
                                     command=lambda: self.run_rc5('encrypt'))
        self.btn_enc.pack(side="left", padx=10)

        self.btn_dec = ctk.CTkButton(btn_container, text="ДЕШИФРУВАТИ", fg_color="#10B981",
                                     command=lambda: self.run_rc5('decrypt'))
        self.btn_dec.pack(side="left", padx=10)

        self.result_box = ctk.CTkTextbox(self, fg_color="white", corner_radius=12, font=("Consolas", 13))
        self.result_box.pack(padx=20, pady=10, fill="both", expand=True)

    def log(self, text):
        self.result_box.insert("end", f"> {text}\n")
        self.result_box.see("end")

    def run_rc5(self, mode):
        path = filedialog.askopenfilename()
        pwd = self.pass_entry.get()

        if not path or not pwd:
            self.log("❌ Оберіть файл та введіть пароль")
            return

        try:
            out = lab3.process_file(path, pwd, w=16, r=20, b=8, mode=mode)
            self.log(f"✅ Успіх ({mode})! Файл: {os.path.basename(out)}")
        except Exception as e:
            self.log(f"❌ Помилка: {str(e)}")