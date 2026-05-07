import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from labs import lab4

FRAME_COLOR = "#F0F4F8"
BUTTON_COLOR = "#3B82F6"
TEXT_COLOR = "#1E293B"
GREEN = "#10B981"
RED = "#EF4444"
AMBER = "#F59E0B"


class Lab4Frame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._private_key = None
        self._public_key = None

        ctk.CTkLabel(
            self,
            text="RSA Encryption (Lab 4)",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT_COLOR,
        ).pack(pady=15)

        info = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        info.pack(padx=20, pady=(0, 10), fill="x")
        ctk.CTkLabel(
            info,
            text="Шифрування: RSA-OAEP (SHA-256) | Розмір ключа: 1024, 2048 або 4096 біт",
            font=("Segoe UI", 12, "italic"),
            text_color="#64748B",
        ).pack(pady=6)

        key_row = ctk.CTkFrame(self, fg_color="transparent")
        key_row.pack(pady=4)
        ctk.CTkLabel(key_row, text="Розмір ключа:", text_color=TEXT_COLOR,
                     font=("Segoe UI", 13)).pack(side="left", padx=(0, 8))
        self.key_size_var = ctk.StringVar(value="2048")
        for size in ("1024", "2048", "4096"):
            ctk.CTkRadioButton(
                key_row, text=f"{size} біт",
                variable=self.key_size_var, value=size,
                text_color=TEXT_COLOR,
            ).pack(side="left", padx=6)

        key_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        key_btn_row.pack(pady=6)

        ctk.CTkButton(key_btn_row, text="🔑 Генерувати ключі",
                      fg_color=BUTTON_COLOR, command=self._generate_keys,
                      width=170).pack(side="left", padx=6)

        ctk.CTkButton(key_btn_row, text="💾 Зберегти ключі",
                      fg_color="#6366F1", command=self._save_keys,
                      width=150).pack(side="left", padx=6)

        ctk.CTkButton(key_btn_row, text="📂 Завантажити ключі",
                      fg_color="#8B5CF6", command=self._load_keys,
                      width=170).pack(side="left", padx=6)

        self.key_status = ctk.CTkLabel(
            self, text="⚠ Ключі не завантажено",
            font=("Segoe UI", 12), text_color=AMBER,
        )
        self.key_status.pack(pady=2)

        ctk.CTkFrame(self, height=1, fg_color="#CBD5E1").pack(fill="x", padx=20, pady=8)

        crypto_row = ctk.CTkFrame(self, fg_color="transparent")
        crypto_row.pack(pady=6)

        ctk.CTkButton(crypto_row, text="🔒 ЗАШИФРУВАТИ файл",
                      fg_color=BUTTON_COLOR, command=self._encrypt,
                      width=200).pack(side="left", padx=10)

        ctk.CTkButton(crypto_row, text="🔓 ДЕШИФРУВАТИ файл",
                      fg_color=GREEN, command=self._decrypt,
                      width=200).pack(side="left", padx=10)

        bench_row = ctk.CTkFrame(self, fg_color="transparent")
        bench_row.pack(pady=4)
        ctk.CTkButton(bench_row, text="⚡ Бенчмарк RSA vs RC5",
                      fg_color=AMBER, text_color="#1E293B",
                      command=self._benchmark, width=200).pack()

        self.result_box = ctk.CTkTextbox(
            self, fg_color="white", corner_radius=12,
            font=("Consolas", 13),
        )
        self.result_box.pack(padx=20, pady=10, fill="both", expand=True)

    def log(self, text: str, color: str = ""):
        self.result_box.insert("end", f"> {text}\n")
        self.result_box.see("end")

    def _no_keys_check(self, need_private=False) -> bool:
        if self._public_key is None:
            self.log("❌ Спочатку згенеруйте або завантажте ключі")
            return True
        if need_private and self._private_key is None:
            self.log("❌ Приватний ключ відсутній")
            return True
        return False

    def _update_key_status(self):
        if self._private_key and self._public_key:
            bits = self._private_key.key_size
            self.key_status.configure(
                text=f"✅ Ключі готові  ({bits}-біт RSA)",
                text_color=GREEN,
            )
        elif self._public_key:
            self.key_status.configure(
                text="⚠ Тільки публічний ключ (шифрування доступне)",
                text_color=AMBER,
            )
        else:
            self.key_status.configure(
                text="⚠ Ключі не завантажено",
                text_color=AMBER,
            )

    def _generate_keys(self):
        key_size = int(self.key_size_var.get())
        self.log(f"⏳ Генерація {key_size}-бітних ключів RSA…")

        def worker():
            priv, pub = lab4.generate_key_pair(key_size)
            self._private_key = priv
            self._public_key = pub
            self.after(0, lambda: (
                self._update_key_status(),
                self.log(f"✅ Ключі згенеровано ({key_size} біт)"),
            ))

        threading.Thread(target=worker, daemon=True).start()

    def _save_keys(self):
        if self._no_keys_check(need_private=True):
            return
        directory = filedialog.askdirectory(title="Оберіть папку для збереження ключів")
        if not directory:
            return
        priv_path = os.path.join(directory, "private_key.pem")
        pub_path = os.path.join(directory, "public_key.pem")
        try:
            lab4.save_private_key(self._private_key, priv_path)
            lab4.save_public_key(self._public_key, pub_path)
            self.log(f"✅ Ключі збережено:\n   {priv_path}\n   {pub_path}")
        except Exception as e:
            self.log(f"❌ Помилка збереження: {e}")

    def _load_keys(self):
        choice = messagebox.askyesnocancel(
            "Завантаження ключів",
            "Завантажити приватний ключ?\n(Так — приватний, Ні — лише публічний)",
        )
        if choice is None:
            return
        try:
            if choice:
                path = filedialog.askopenfilename(
                    title="Оберіть приватний ключ (PEM)",
                    filetypes=[("PEM", "*.pem"), ("Всі файли", "*.*")],
                )
                if not path:
                    return
                self._private_key = lab4.load_private_key(path)
                self._public_key = self._private_key.public_key()
                self.log(f"✅ Приватний ключ завантажено: {os.path.basename(path)}")
            else:
                path = filedialog.askopenfilename(
                    title="Оберіть публічний ключ (PEM)",
                    filetypes=[("PEM", "*.pem"), ("Всі файли", "*.*")],
                )
                if not path:
                    return
                self._public_key = lab4.load_public_key(path)
                self._private_key = None
                self.log(f"✅ Публічний ключ завантажено: {os.path.basename(path)}")
            self._update_key_status()
        except Exception as e:
            self.log(f"❌ Помилка завантаження ключа: {e}")

    def _encrypt(self):
        if self._no_keys_check():
            return
        path = filedialog.askopenfilename(title="Оберіть файл для шифрування")
        if not path:
            return
        self.log(f"⏳ Шифрування: {os.path.basename(path)}…")

        def worker():
            try:
                out = lab4.encrypt_file(path, self._public_key)
                size = os.path.getsize(out)
                self.after(0, lambda: self.log(
                    f"✅ Зашифровано → {os.path.basename(out)}  ({size:,} байт)"
                ))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Помилка шифрування: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _decrypt(self):
        if self._no_keys_check(need_private=True):
            return
        path = filedialog.askopenfilename(
            title="Оберіть зашифрований файл",
            filetypes=[("ENC", "*.enc"), ("Всі файли", "*.*")],
        )
        if not path:
            return
        self.log(f"⏳ Дешифрування: {os.path.basename(path)}…")

        def worker():
            try:
                out = lab4.decrypt_file(path, self._private_key)
                size = os.path.getsize(out)
                self.after(0, lambda: self.log(
                    f"✅ Розшифровано → {os.path.basename(out)}  ({size:,} байт)"
                ))
            except Exception as e:
                error_type = str(type(e))
                error_details = str(e)

                if "ValueError" in error_type or "Decryption failed" in error_details:
                    msg = "Невірний приватний ключ RSA! Ви намагаєтесь розшифрувати файл чужим ключем."
                else:
                    msg = f"Не вдалося розшифрувати файл. {error_details}"

                self.after(0, lambda: self.log(f"❌ Помилка дешифрування: {msg}"))
                self.after(0, lambda: messagebox.showerror("Помилка доступу", msg))

        threading.Thread(target=worker, daemon=True).start()

    def _benchmark(self):
        if self._no_keys_check(need_private=True):
            return
        data_size = 100
        self.log(f"⏳ Бенчмарк: RSA vs RC5 на файлі {data_size} КБ… Зачекайте.")

        def worker():
            import sys
            import io

            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()

            try:
                lab4.benchmark_rsa_vs_rc5(self._public_key, self._private_key, data_size_kb=data_size)
                output_text = mystdout.getvalue()
                self.after(0, lambda: self.log(f"\n{output_text}"))
            except AttributeError:
                self.after(0, lambda: self.log("❌ Помилка: Функцію benchmark_rsa_vs_rc5 не знайдено у lab4.py"))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Помилка бенчмарку: {e}"))
            finally:
                sys.stdout = old_stdout

        threading.Thread(target=worker, daemon=True).start()