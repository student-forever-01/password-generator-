import customtkinter as ctk
import secrets
import string
import math
import platform

# ── Global configuration ───────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

SPECIAL_CHARACTERS = '!@#$%^&*()_+[]{}|;:,.<>?'
AMBIGUOS = set('O0Il')

# ── Translations ───────────────────────────────────────────────────
TRANSLATIONS = {
    'en': {
        'window_title': "🔐 Password Generator",
        'title': "🔐 Password Generator",
        'length': "Length:",
        'tooltip_length': "Length (4‑64)",
        'Lowercase': "🔡 Lowercase",
        'tooltip_lowercase': "Letters a‑z",
        'Uppercase': "🔠 Uppercase",
        'tooltip_uppercase': "Letters A‑Z",
        'Numbers': "🔢 Numbers",
        'tooltip_numbers': "Digits 0‑9",
        'Special': "❗ Special",
        'tooltip_special': SPECIAL_CHARACTERS,
        'Ambiguous': "🚫 Ambiguous",
        'tooltip_ambiguous': "O, 0, I, l",
        'tooltip_strength': "Level and entropy bits",
        'show_password': "👁 Show password",
        'tooltip_show_password': "Hide/show text",
        'generate': "🔄 Generate",
        'tooltip_generate': "Generate — Ctrl+R (always new)",
        'copied': "Copied!",
        'nothing_to_copy': "Nothing to copy",
        'level_weak': "Weak",
        'level_medium': "Medium",
        'level_strong': "Strong",
    },
    'es': {
        'window_title': "🔐 Generador de Contraseñas",
        'title': "🔐 Generador de Contraseñas",
        'length': "Longitud:",
        'tooltip_length': "Longitud (4‑64)",
        'Lowercase': "🔡 Minúsculas",
        'tooltip_lowercase': "Letras a‑z",
        'Uppercase': "🔠 Mayúsculas",
        'tooltip_uppercase': "Letras A‑Z",
        'Numbers': "🔢 Números",
        'tooltip_numbers': "Dígitos 0‑9",
        'Special': "❗ Especiales",
        'tooltip_special': SPECIAL_CHARACTERS,
        'Ambiguous': "🚫 Ambiguos",
        'tooltip_ambiguous': "O, 0, I, l",
        'tooltip_strength': "Nivel y bits de entropía",
        'show_password': "👁 Mostrar contraseña",
        'tooltip_show_password': "Ocultar/mostrar texto",
        'generate': "🔄 Generar",
        'tooltip_generate': "Generar — Ctrl+R (siempre nuevo)",
        'copied': "¡Copiado!",
        'nothing_to_copy': "Nada que copiar",
        'level_weak': "Débil",
        'level_medium': "Medio",
        'level_strong': "Fuerte",
    }
}

# ── Tooltip ────────────────────────────────────────────────────────
class Tooltip:
    """Create a small tooltip window that appears after a short delay when the mouse hovers over a widget."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tipwindow = self._id = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)

    def _schedule(self, _=None):
        self._id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self._tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        tw = ctk.CTkToplevel(self.widget)
        tw.overrideredirect(True)
        tw.attributes("-topmost", True)
        ctk.CTkLabel(
            tw,
            text=self.text,
            fg_color="#333333",
            text_color="#ffffff",
            corner_radius=4,
            wraplength=200,
            font=ctk.CTkFont(size=12),
        ).pack(ipadx=5, ipady=3)
        tw.geometry(f"+{x}+{y}")
        self._tipwindow = tw

    def _hide(self, _=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self._tipwindow:
            self._tipwindow.destroy()
            self._tipwindow = None

# ── Application ───────────────────────────────────────────────────
class GeneradorApp(ctk.CTk):
    """Main application window for the password generator with language switch feature."""

    def __init__(self):
        super().__init__()
        self.translations = TRANSLATIONS
        self.lang = 'en'
        self.title(self._t('window_title'))

        # Window geometry
        w0, h0 = 400, 480
        sx, sy = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w0}x{h0}+{(sx - w0) // 2}+{(sy - h0) // 2}")
        self.minsize(350, 450)
        self.resizable(False, False)

        # Variables
        self.length_var = ctk.IntVar(value=12)
        self.include_lower = ctk.BooleanVar(value=True)
        self.include_upper = ctk.BooleanVar(value=True)
        self.include_digits = ctk.BooleanVar(value=True)
        self.include_specials = ctk.BooleanVar(value=True)
        self.exclude_ambiguous = ctk.BooleanVar(value=False)
        self.password_var = ctk.StringVar()
        self.show_pwd_var = ctk.BooleanVar(value=True)
        self._last_pwd = ""

        # UI state tracking
        self.switches = {}
        self.tooltips = []

        # Container frame
        container = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)

        # Language selector
        self.lang_selector = ctk.CTkSegmentedButton(
            container, values=["EN", "ES"], command=self.change_language
        )
        self.lang_selector.set("EN")
        self.lang_selector.grid(row=0, column=1, sticky="e", padx=(0,10), pady=(0,10))

        # Title label
        self.title_label = ctk.CTkLabel(
            container,
            text=self._t('title'),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2c3e50",
        )
        self.title_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        # Length slider
        frame_len = ctk.CTkFrame(container, fg_color="#f7f9fa", corner_radius=6)
        frame_len.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        frame_len.grid_columnconfigure(1, weight=1)

        self.len_lbl = ctk.CTkLabel(
            frame_len,
            text=self._t('length'),
            font=ctk.CTkFont(size=14)
        )
        self.len_lbl.grid(row=0, column=0, padx=(10, 5))
        self.tooltips.append((Tooltip(self.len_lbl, self._t('tooltip_length')), 'tooltip_length'))

        self.slider = ctk.CTkSlider(
            frame_len,
            from_=4,
            to=64,
            number_of_steps=60,
            variable=self.length_var,
            command=self.actualizar,
        )
        self.slider.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            frame_len,
            textvariable=self.length_var,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#ecf0f1",
            corner_radius=6,
            width=40,
        ).grid(row=0, column=2, padx=(5, 10))

        # Options
        opts = [
            ('Lowercase', self.include_lower, 'tooltip_lowercase'),
            ('Uppercase', self.include_upper, 'tooltip_uppercase'),
            ('Numbers', self.include_digits, 'tooltip_numbers'),
            ('Special', self.include_specials, 'tooltip_special'),
            ('Ambiguous', self.exclude_ambiguous, 'tooltip_ambiguous'),
        ]
        opt_frame = ctk.CTkFrame(container, fg_color="#f7f9fa", corner_radius=6)
        opt_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        for i in range(2): opt_frame.grid_columnconfigure(i, weight=1)

        for idx, (key, var, tip_key) in enumerate(opts):
            r, c = divmod(idx, 2)
            sw = ctk.CTkSwitch(opt_frame, text=self._t(key), variable=var,
                                font=ctk.CTkFont(size=14), button_color="#1abc9c",
                                progress_color="#1abc9c", switch_width=50,
                                switch_height=24, command=self.actualizar)
            sw.grid(row=r, column=c, sticky="w", padx=15, pady=6)
            self.switches[key] = sw
            self.tooltips.append((Tooltip(sw, self._t(tip_key)), tip_key))

        # Strength meter
        st_frame = ctk.CTkFrame(container, fg_color="#f7f9fa", corner_radius=6)
        st_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        self.strength_bar = ctk.CTkProgressBar(st_frame, width=300)
        self.strength_bar.pack(fill="x", expand=True, padx=15, pady=(10, 5))
        self.strength_label = ctk.CTkLabel(st_frame, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.strength_label.pack(pady=(0, 10))
        self.tooltips.append((Tooltip(self.strength_label, self._t('tooltip_strength')), 'tooltip_strength'))

        # Password entry
        self.pwd_entry = ctk.CTkEntry(container, textvariable=self.password_var,
                                       font=ctk.CTkFont(family="Courier New", size=14),
                                       fg_color="#ffffff", text_color="#2c3e50",
                                       state="readonly")
        self.pwd_entry.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.pwd_entry.bind("<Button-1>", lambda e: self.copy_on_click())
        self.tooltips.append((Tooltip(self.pwd_entry, self._t('tooltip_show_password')), 'tooltip_show_password'))

        # Show/hide switch
        show_frame = ctk.CTkFrame(container, fg_color="#ffffff", corner_radius=6)
        show_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)
        show_frame.grid_columnconfigure(0, weight=1)
        self.show_sw = ctk.CTkSwitch(show_frame, text=self._t('show_password'),
                                     variable=self.show_pwd_var, font=ctk.CTkFont(size=14),
                                     button_color="#95a5a6", progress_color="#95a5a6",
                                     command=self.toggle_show)
        self.show_sw.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.tooltips.append((Tooltip(self.show_sw, self._t('tooltip_show_password')), 'tooltip_show_password'))

        # Generate button
        btn_frame = ctk.CTkFrame(container, fg_color="#ffffff", corner_radius=6)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)
        btn_frame.grid_columnconfigure(0, weight=1)
        self.generate_btn = ctk.CTkButton(btn_frame, text=self._t('generate'), height=40,
                                          fg_color="#3498db", hover_color="#2980b9",
                                          command=self.actualizar)
        self.generate_btn.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.tooltips.append((Tooltip(self.generate_btn, self._t('tooltip_generate')), 'tooltip_generate'))

        # Shortcuts
        accel = "Command" if platform.system() == "Darwin" else "Control"
        for key in ['r', 'R']: self.bind_all(f"<{accel}-{key}>", lambda e: self.actualizar())
        for key in ['c', 'C']: self.bind_all(f"<{accel}-{key}>", lambda e: self.copy_on_click())

        # First run
        self.actualizar()
        self.toggle_show()

    def _t(self, key):
        return self.translations[self.lang][key]

    def change_language(self, value):
        self.lang = 'en' if value == 'EN' else 'es'
        self.title(self._t('window_title'))
        self._update_texts()
        self.actualizar()  # Refresh password and strength after language change

    def _update_texts(self):
        self.title(self._t('window_title'))
        self.title_label.configure(text=self._t('title'))
        self.len_lbl.configure(text=self._t('length'))
        for key, sw in self.switches.items(): sw.configure(text=self._t(key))
        for tip, k in self.tooltips: tip.text = self._t(k)
        self.show_sw.configure(text=self._t('show_password'))
        self.generate_btn.configure(text=self._t('generate'))

    def generar_contrasena(self):
        length = self.length_var.get()
        minus, mayus = string.ascii_lowercase, string.ascii_uppercase
        nums, especs = string.digits, SPECIAL_CHARACTERS
        if self.exclude_ambiguous.get():
            minus = "".join(c for c in minus if c not in AMBIGUOS)
            mayus = "".join(c for c in mayus if c not in AMBIGUOS)
            nums = "".join(c for c in nums if c not in AMBIGUOS)

        disp, aseg = "", []
        if self.include_lower.get():
            disp += minus; aseg.append(secrets.choice(minus))
        if self.include_upper.get():
            disp += mayus; aseg.append(secrets.choice(mayus))
        if self.include_digits.get():
            disp += nums; aseg.append(secrets.choice(nums))
        if self.include_specials.get():
            disp += especs; aseg.append(secrets.choice(especs))

        if not disp:
            self.password_var.set(self._t('nothing_to_copy'))
            return
        if length < len(aseg):
            length = len(aseg)
            self.length_var.set(length)

        for _ in range(10):
            pwd_chars = aseg + [secrets.choice(disp) for _ in range(length - len(aseg))]
            secrets.SystemRandom().shuffle(pwd_chars)
            new_pwd = "".join(pwd_chars)
            if new_pwd != self._last_pwd:
                break
        else:
            idx = secrets.randbelow(length)
            alt_chars = [c for c in disp if c != new_pwd[idx]]
            if alt_chars:
                alt_char = secrets.choice(alt_chars)
                new_pwd = new_pwd[:idx] + alt_char + new_pwd[idx+1:]

        self.password_var.set(new_pwd)
        self._last_pwd = new_pwd

    def calcular_fuerza(self):
        total = 0
        if self.include_lower.get():
            total += len(string.ascii_lowercase) - (4 if self.exclude_ambiguous.get() else 0)
        if self.include_upper.get():
            total += len(string.ascii_uppercase) - (2 if self.exclude_ambiguous.get() else 0)
        if self.include_digits.get():
            total += len(string.digits) - (2 if self.exclude_ambiguous.get() else 0)
        if self.include_specials.get():
            total += len(SPECIAL_CHARACTERS)
        bits = self.length_var.get() * (math.log2(total) if total else 0)
        pct = min(bits / 60, 1.0)
        self.strength_bar.set(pct)
        if bits < 28:
            nivel = self._t('level_weak')
            color = "#e74c3c"
        elif bits < 36:
            nivel = self._t('level_medium')
            color = "#f1c40f"
        else:
            nivel = self._t('level_strong')
            color = "#2ecc71"
        self.strength_label.configure(text=f"{nivel} — {bits:.0f} bits")
        self.strength_bar.configure(progress_color=color)

    def actualizar(self, *_):
        self.generar_contrasena()
        self.calcular_fuerza()

    # ── Show / hide ───────────────────────────────────────────────
    def toggle_show(self):
        self.pwd_entry.configure(show="" if self.show_pwd_var.get() else "•")

    # ── Copy and toast ────────────────────────────────────────────
    def copy_on_click(self):
        pwd = self.password_var.get()
        if pwd and pwd not in (self._t('nothing_to_copy'),):
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.show_toast(self._t('copied'))
        else:
            self.show_toast(self._t('nothing_to_copy'))

    def show_toast(self, text):
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        w, h = 150, 40
        toast.geometry(
            f"{w}x{h}+{self.winfo_x() + (self.winfo_width() - w)//2}+{self.winfo_y() + self.winfo_height() - 80}"
        )
        ctk.CTkLabel(
            toast,
            text=text,
            fg_color="#2c3e50",
            text_color="#ffffff",
            corner_radius=8,
        ).pack(fill="both", expand=True)
        def fade(a=1.0):
            a -= 0.05
            if a <= 0:
                toast.destroy()
            else:
                toast.attributes("-alpha", a)
                toast.after(50, fade, a)
        toast.after(1000, fade)

# ── Main ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    GeneradorApp().mainloop()
