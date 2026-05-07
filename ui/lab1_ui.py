import customtkinter as ctk
import random
import math
import os
from labs import lab1

FRAME_COLOR = "#F0F4F8"
BUTTON_COLOR = "#3B82F6"
HOVER_COLOR = "#2563EB"
TEXT_COLOR = "#1E293B"


class Lab1Frame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(self, font=("Segoe UI", 24, "bold"), text_color=TEXT_COLOR)
        self.label.pack(pady=15)

        self.param_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        self.param_frame.pack(padx=20, pady=10, fill="x")

        ctk.CTkLabel(self.param_frame, text="Налаштування LCG:",
                     text_color=TEXT_COLOR, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

        self.entries = {}
        params = [("Multiplier (A)", "a_entry", lab1.a),
                  ("Increment (C)", "c_entry", lab1.c),
                  ("Modulus (M)", "m_entry", lab1.m),
                  ("Seed (X0)", "x0_entry", lab1.x0)]

        for i, (text, attr, default) in enumerate(params):
            ctk.CTkLabel(self.param_frame, text=text, text_color=TEXT_COLOR).grid(row=1, column=i, padx=15)
            entry = ctk.CTkEntry(self.param_frame, placeholder_text=str(default), width=140)
            entry.grid(row=2, column=i, padx=10, pady=(0, 15))
            self.entries[attr] = entry

        self.action_frame = ctk.CTkFrame(self, fg_color=FRAME_COLOR, corner_radius=12)
        self.action_frame.pack(padx=20, pady=10, fill="x")

        gen_inner = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        gen_inner.pack(fill="x", padx=20, pady=15)

        self.entry_n = ctk.CTkEntry(gen_inner, placeholder_text="Кількість чисел (N)", width=250)
        self.entry_n.pack(side="left", padx=(0, 10))

        btn_gen = ctk.CTkButton(gen_inner, text="ЗГЕНЕРУВАТИ", command=self.run_generation,
                                fg_color=BUTTON_COLOR, hover_color=HOVER_COLOR)
        btn_gen.pack(side="left", fill="x", expand=True)

        test_buttons_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        test_buttons_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_period = ctk.CTkButton(test_buttons_frame, text="ПЕРЕВІРИТИ ПЕРІОД",
                                        command=self.run_period, fg_color="#10B981", hover_color="#059669")
        self.btn_period.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_cesaro = ctk.CTkButton(test_buttons_frame, text="ТЕСТ ЧЕЗАРО (π)",
                                        command=self.run_cesaro, fg_color="#8B5CF6", hover_color="#7C3AED")
        self.btn_cesaro.pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.result_box = ctk.CTkTextbox(self, fg_color="white", text_color="#334155",
                                         corner_radius=12, font=("Consolas", 13))
        self.result_box.pack(padx=20, pady=10, fill="both", expand=True)

    def update_params(self):
        try:
            if self.entries["a_entry"].get(): lab1.a = int(self.entries["a_entry"].get())
            if self.entries["c_entry"].get(): lab1.c = int(self.entries["c_entry"].get())
            if self.entries["m_entry"].get(): lab1.m = int(self.entries["m_entry"].get())
            if self.entries["x0_entry"].get(): lab1.x0 = int(self.entries["x0_entry"].get())
        except ValueError:
            self.write_to_log("❌ Помилка: Всі параметри мають бути цілими числами!")

    def write_to_log(self, text):
        self.result_box.insert("end", f"> {text}\n")
        self.result_box.see("end")

    def run_generation(self):
        try:
            self.update_params()
            n = int(self.entry_n.get()) if self.entry_n.get() else 50
            sequence = lab1.generate_N_sequence(n, start=lab1.x0)
            if n >= 10 :
                self.write_to_log(f"Згенеровано {n} чисел. Перші 10:\n{sequence[:10]}...")
            else :
                self.write_to_log(f"Згенеровано {n} чисел. Перші {n}:\n{sequence[:n]}...")

            with open("lab1_results.txt", "w") as f:
                f.write(str(sequence))
            self.write_to_log("✅ Результати збережено в 'lab1_results.txt'")
        except Exception as e:
            self.write_to_log(f"❌ Помилка: {e}")

    def run_period(self):
        self.update_params()
        self.write_to_log("⏳ Йде розрахунок періоду...")
        self.update()
        p = lab1.period(start=lab1.x0)
        self.write_to_log(f"✨ Період генератора: {p}")

    def run_cesaro(self):
        try:
            self.update_params()
            n = int(self.entry_n.get()) if self.entry_n.get() else 1000
            seq = lab1.generate_N_sequence(n, start=lab1.x0)
            pi_approx = lab1.chesaro(seq)
            self.write_to_log(f"🎯 Тест Чезаро (N={n}): π ≈ {pi_approx:.6f}")
        except Exception as e:
            self.write_to_log(f"❌ Помилка: {e}")
