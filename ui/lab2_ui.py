import os
import customtkinter as ctk
from tkinter import filedialog
from labs import lab2

FRAME_COLOR = "#F0F4F8"
BUTTON_COLOR = "#3B82F6"
HOVER_COLOR = "#2563EB"
TEXT_COLOR = "#1E293B"
DEFAULT_FONT = "Segoe UI"

class Lab2Frame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.log_file = "lab2_results.txt"

        self.label = ctk.CTkLabel(self, text="MD5 Hash & Integrity",
                                  font=(DEFAULT_FONT, 24, "bold"), text_color=TEXT_COLOR)
        self.label.pack(pady=15)

        self.text_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        self.text_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(self.text_frame, text="1. Хешування тексту:",
                     font=(DEFAULT_FONT, 14, "bold"), text_color=TEXT_COLOR).pack(pady=5)

        inner_text = ctk.CTkFrame(self.text_frame, fg_color="transparent")
        inner_text.pack(fill="x", padx=20, pady=10)

        self.text_entry = ctk.CTkEntry(inner_text, placeholder_text="Введіть текст для хешування", width=400)
        self.text_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.btn_hash_text = ctk.CTkButton(inner_text, text="HASH TEXT", command=self.hash_text,
                                           fg_color=BUTTON_COLOR, hover_color=HOVER_COLOR)
        self.btn_hash_text.pack(side="right")

        self.file_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        self.file_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(self.file_frame, text="2. Робота з файлами та цілісність:",
                     font=(DEFAULT_FONT, 14, "bold"), text_color=TEXT_COLOR).pack(pady=5)

        self.expected_hash_entry = ctk.CTkEntry(self.file_frame,
                                                placeholder_text="Еталонний MD5 (можна вставити вручну)")
        self.expected_hash_entry.pack(fill="x", padx=20, pady=5)

        file_btns_inner = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        file_btns_inner.pack(fill="x", padx=20, pady=10)

        self.btn_file_hash = ctk.CTkButton(file_btns_inner, text="ОТРИМАТИ ХЕШ ФАЙЛУ",
                                           command=self.hash_file, fg_color="#10B981")
        self.btn_file_hash.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_verify = ctk.CTkButton(file_btns_inner, text="ПЕРЕВІРИТИ (РУЧНИЙ ХЕШ)",
                                        command=self.verify_integrity, fg_color="#F59E0B")
        self.btn_verify.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_verify_md5_file = ctk.CTkButton(file_btns_inner, text="ПЕРЕВІРИТИ ЗА MD5 ФАЙЛОМ",
                                                 command=self.verify_with_md5_file,
                                                 fg_color="#8B5CF6")
        self.btn_verify_md5_file.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.result_box = ctk.CTkTextbox(self, fg_color="white", text_color="#334155",
                                         corner_radius=12, font=("Consolas", 13))
        self.result_box.pack(padx=20, pady=10, fill="both", expand=True)

    def write_to_log(self, text):
        self.result_box.insert("end", f"> {text}\n\n")
        self.result_box.see("end")

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"> {text}\n\n")
        except Exception as e:
            print(f"Помилка запису у файл: {e}")

    def hash_text(self):
        txt = self.text_entry.get()
        h = lab2.get_string_hash(txt)
        self.write_to_log(f"Текст: '{txt}'\nMD5: {h}")

    def hash_file(self):
        path = filedialog.askopenfilename()
        if path:
            h = lab2.get_file_hash(path)
            self.write_to_log(f"Файл: {os.path.basename(path)}\nMD5: {h}")

    def verify_integrity(self):
        path = filedialog.askopenfilename()
        expected = self.expected_hash_entry.get().strip()

        if not path:
            return
        if not expected:
            self.write_to_log("❌ Введіть еталонний хеш")
            return

        is_valid = lab2.verify_file_integrity(path, expected)
        status = "✅ ЦІЛІСНІСТЬ ПІДТВЕРДЖЕНО" if is_valid else "❌ ФАЙЛ ЗМІНЕНО"
        self.write_to_log(f"Перевірка: {os.path.basename(path)}\nРезультат: {status}")

    def verify_with_md5_file(self):
        file_path = filedialog.askopenfilename(title="Виберіть файл для перевірки")
        if not file_path:
            return

        md5_path = filedialog.askopenfilename(title="Виберіть файл з MD5 хешем")
        if not md5_path:
            return

        try:
            with open(md5_path, "r", encoding="utf-8") as f:
                expected_hash = f.read().strip()

            actual_hash = lab2.get_file_hash(file_path)

            if actual_hash.lower() == expected_hash.lower():
                status = "✅ ЦІЛІСНІСТЬ ПІДТВЕРДЖЕНО"
            else:
                status = "❌ ФАЙЛ ЗМІНЕНО АБО ПОШКОДЖЕНО"

            self.write_to_log(
                f"Файл: {os.path.basename(file_path)}\n"
                f"MD5 файл: {os.path.basename(md5_path)}\n"
                f"Очікуваний: {expected_hash}\n"
                f"Отриманий: {actual_hash}\n"
                f"Результат: {status}"
            )

        except Exception as e:
            self.write_to_log(f"❌ Помилка: {e}")