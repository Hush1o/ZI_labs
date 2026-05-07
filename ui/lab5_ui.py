import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from labs import lab5

FRAME_COLOR = "#F0F4F8"
BUTTON_COLOR = "#3B82F6"
TEXT_COLOR  = "#1E293B"
GREEN  = "#10B981"
RED    = "#EF4444"
AMBER  = "#F59E0B"
PURPLE = "#8B5CF6"


class Lab5Frame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._private_key = None
        self._public_key  = None
        self._last_signature: bytes | None = None   # підпис останнього рядка

        # ── Заголовок ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="DSS Digital Signature (Lab 5)",
            font=("Segoe UI", 24, "bold"),
            text_color=TEXT_COLOR,
        ).pack(pady=15)

        info = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        info.pack(padx=20, pady=(0, 10), fill="x")
        ctk.CTkLabel(
            info,
            text="Цифровий підпис: DSA + SHA-256 | Розмір ключа: 1024, 2048 або 3072 біт",
            font=("Segoe UI", 12, "italic"),
            text_color="#64748B",
        ).pack(pady=6)

        # ── Вибір розміру ключа ────────────────────────────────────────────────
        key_row = ctk.CTkFrame(self, fg_color="transparent")
        key_row.pack(pady=4)
        ctk.CTkLabel(key_row, text="Розмір ключа:", text_color=TEXT_COLOR,
                     font=("Segoe UI", 13)).pack(side="left", padx=(0, 8))
        self.key_size_var = ctk.StringVar(value="2048")
        for size in ("1024", "2048", "3072"):
            ctk.CTkRadioButton(
                key_row, text=f"{size} біт",
                variable=self.key_size_var, value=size,
                text_color=TEXT_COLOR,
            ).pack(side="left", padx=6)

        # ── Кнопки управління ключами ──────────────────────────────────────────
        key_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        key_btn_row.pack(pady=6)

        ctk.CTkButton(key_btn_row, text="🔑 Генерувати ключі",
                      fg_color=BUTTON_COLOR, command=self._generate_keys,
                      width=170).pack(side="left", padx=6)

        ctk.CTkButton(key_btn_row, text="💾 Зберегти ключі",
                      fg_color="#6366F1", command=self._save_keys,
                      width=150).pack(side="left", padx=6)

        ctk.CTkButton(key_btn_row, text="📂 Завантажити ключі",
                      fg_color=PURPLE, command=self._load_keys,
                      width=170).pack(side="left", padx=6)

        self.key_status = ctk.CTkLabel(
            self, text="⚠ Ключі не завантажено",
            font=("Segoe UI", 12), text_color=AMBER,
        )
        self.key_status.pack(pady=2)

        ctk.CTkFrame(self, height=1, fg_color="#CBD5E1").pack(fill="x", padx=20, pady=8)

        # ── Підпис рядка ───────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Підпис рядка:", font=("Segoe UI", 13, "bold"),
                     text_color=TEXT_COLOR).pack(anchor="w", padx=22)

        self.message_entry = ctk.CTkEntry(
            self, placeholder_text="Введіть повідомлення для підпису…",
            font=("Segoe UI", 13), height=38,
        )
        self.message_entry.pack(padx=20, pady=(4, 6), fill="x")

        msg_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        msg_btn_row.pack(pady=4)

        ctk.CTkButton(msg_btn_row, text="✍ Підписати рядок",
                      fg_color=BUTTON_COLOR, command=self._sign_message,
                      width=180).pack(side="left", padx=8)

        ctk.CTkButton(msg_btn_row, text="✅ Перевірити підпис рядка",
                      fg_color=GREEN, command=self._verify_message,
                      width=200).pack(side="left", padx=8)

        ctk.CTkFrame(self, height=1, fg_color="#CBD5E1").pack(fill="x", padx=20, pady=8)

        # ── Підпис / перевірка файлу ───────────────────────────────────────────
        file_btn_row = ctk.CTkFrame(self, fg_color="transparent")
        file_btn_row.pack(pady=4)

        ctk.CTkButton(file_btn_row, text="📄 Підписати файл",
                      fg_color=BUTTON_COLOR, command=self._sign_file,
                      width=180).pack(side="left", padx=8)

        ctk.CTkButton(file_btn_row, text="🔍 Перевірити підпис файлу",
                      fg_color=GREEN, command=self._verify_file,
                      width=210).pack(side="left", padx=8)

        ctk.CTkFrame(self, height=1, fg_color="#CBD5E1").pack(fill="x", padx=20, pady=8)

        # ── Лог ───────────────────────────────────────────────────────────────
        self.result_box = ctk.CTkTextbox(
            self, fg_color="white", corner_radius=12,
            font=("Consolas", 13),
        )
        self.result_box.pack(padx=20, pady=10, fill="both", expand=True)

    # ── Допоміжні ─────────────────────────────────────────────────────────────

    def log(self, text: str):
        self.result_box.insert("end", f"> {text}\n")
        self.result_box.see("end")

    def _no_keys_check(self, need_private: bool = False) -> bool:
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
                text=f"✅ Ключі готові  ({bits}-біт DSA)",
                text_color=GREEN,
            )
        elif self._public_key:
            self.key_status.configure(
                text="⚠ Тільки публічний ключ (перевірка доступна)",
                text_color=AMBER,
            )
        else:
            self.key_status.configure(
                text="⚠ Ключі не завантажено",
                text_color=AMBER,
            )

    # ── Генерація / збереження / завантаження ─────────────────────────────────

    def _generate_keys(self):
        key_size = int(self.key_size_var.get())
        self.log(f"⏳ Генерація {key_size}-бітних ключів DSA…")

        def worker():
            priv, pub = lab5.generate_keys(key_size)
            self._private_key = priv
            self._public_key  = pub
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
        priv_path = os.path.join(directory, "dsa_private.pem")
        pub_path  = os.path.join(directory, "dsa_public.pem")
        try:
            lab5.save_private_key(self._private_key, priv_path)
            lab5.save_public_key(self._public_key, pub_path)
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
                self._private_key = lab5.load_private_key(path)
                self._public_key  = self._private_key.public_key()
                self.log(f"✅ Приватний ключ завантажено: {os.path.basename(path)}")
            else:
                path = filedialog.askopenfilename(
                    title="Оберіть публічний ключ (PEM)",
                    filetypes=[("PEM", "*.pem"), ("Всі файли", "*.*")],
                )
                if not path:
                    return
                self._public_key  = lab5.load_public_key(path)
                self._private_key = None
                self.log(f"✅ Публічний ключ завантажено: {os.path.basename(path)}")
            self._update_key_status()
        except Exception as e:
            self.log(f"❌ Помилка завантаження ключа: {e}")

    # ── Підпис / перевірка рядка ───────────────────────────────────────────────

    def _sign_message(self):
        if self._no_keys_check(need_private=True):
            return
        message = self.message_entry.get().strip()
        if not message:
            self.log("❌ Введіть повідомлення")
            return

        try:
            self._last_signature = lab5.sign_message(self._private_key, message)
            hex_sig = self._last_signature.hex()
            self.log(f"✍ Повідомлення : {message}")
            self.log(f"   Підпис (hex) : {hex_sig[:64]}…")
            self.log(f"   Довжина підпису: {len(self._last_signature)} байт")

            # Зберегти результат у файл
            lab5.save_result(
                "lab5_string_result.txt",
                f"Повідомлення: {message}\nПідпис (hex): {hex_sig}\n",
            )
            self.log("   Результат збережено → lab5_string_result.txt")
        except Exception as e:
            self.log(f"❌ Помилка підпису: {e}")

    def _verify_message(self):
        if self._no_keys_check():
            return
        message = self.message_entry.get().strip()
        if not message:
            self.log("❌ Введіть повідомлення")
            return
        if self._last_signature is None:
            self.log("❌ Спочатку підпишіть повідомлення")
            return

        valid = lab5.verify_message(self._public_key, message, self._last_signature)
        if valid:
            self.log(f"✅ Підпис дійсний для: «{message}»")
        else:
            self.log(f"❌ Підпис НЕДІЙСНИЙ для: «{message}»")

    # ── Підпис / перевірка файлу ───────────────────────────────────────────────

    def _sign_file(self):
        if self._no_keys_check(need_private=True):
            return
        path = filedialog.askopenfilename(title="Оберіть файл для підпису")
        if not path:
            return

        sig_path = path + ".sig"
        self.log(f"⏳ Підписування: {os.path.basename(path)}…")

        def worker():
            try:
                lab5.sign_file(self._private_key, path, sig_path)
                size = os.path.getsize(sig_path)
                self.after(0, lambda: self.log(
                    f"✅ Підпис збережено → {os.path.basename(sig_path)}  ({size} байт)"
                ))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Помилка підпису файлу: {e}"))

        threading.Thread(target=worker, daemon=True).start()

    def _verify_file(self):
        if self._no_keys_check():
            return

        file_path = filedialog.askopenfilename(title="Оберіть файл для перевірки")
        if not file_path:
            return

        sig_path = filedialog.askopenfilename(
            title="Оберіть файл підпису (.sig)",
            filetypes=[("Signature", "*.sig"), ("Всі файли", "*.*")],
        )
        if not sig_path:
            return

        self.log(f"⏳ Перевірка підпису: {os.path.basename(file_path)}…")

        def worker():
            try:
                valid = lab5.verify_file(self._public_key, file_path, sig_path)
                if valid:
                    self.after(0, lambda: self.log(
                        f"✅ Підпис дійсний для файлу: {os.path.basename(file_path)}"
                    ))
                else:
                    self.after(0, lambda: (
                        self.log(f"❌ Підпис НЕДІЙСНИЙ для файлу: {os.path.basename(file_path)}"),
                        messagebox.showerror("Невірний підпис",
                                             "Файл було змінено або підпис не відповідає ключу!"),
                    ))
            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Помилка перевірки: {e}"))

        threading.Thread(target=worker, daemon=True).start()