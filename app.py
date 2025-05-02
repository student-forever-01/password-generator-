import customtkinter as ctk
import secrets
import string
import math
import platform

# ── Global configuration ───────────────────────────────────────────
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

CARACTERES_ESPECIALES = '!@#$%^&*()_+[]{}|;:,.<>?'
AMBIGUOS = set('O0Il')

# ── Tooltip ────────────────────────────────────────────────────────
class Tooltip:
    """Create a small tooltip window that appears after a short delay
    when the mouse hovers over a widget."""

    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._tipwindow = self._id = None
        widget.bind("<Enter>", self._schedule)  # Schedule display
        widget.bind("<Leave>", self._hide)      # Hide on leave

    def _schedule(self, _=None):
        self._id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self._tipwindow:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self._tipwindow = tw = ctk.CTkToplevel(self.widget)
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

    def _hide(self, _=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self._tipwindow:
            self._tipwindow.destroy()
            self._tipwindow = None


# ── Application ────────────────────────────────────────────────────
class GeneradorApp(ctk.CTk):
    """Main application window for the password generator."""

    def __init__(self):
        super().__init__()

        # Window
        self.title("🔐 Password Generator")
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

        self._last_pwd = ""  # Stores the last generated password

        # Container
        container = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            container,
            text="🔐 Password Generator",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2c3e50",
        ).grid(row=0, column=0, pady=(0, 10))

        # Length slider
        frame_len = ctk.CTkFrame(container, fg_color="#f7f9fa", corner_radius=6)
        frame_len.grid(row=1, column=0, sticky="ew", pady=5)
        frame_len.grid_columnconfigure(1, weight=1)
        len_lbl = ctk.CTkLabel(frame_len, text="Length:", font=ctk.CTkFont(size=14))
        len_lbl.grid(row=0, column=0, padx=(10, 5))
        Tooltip(len_lbl, "Length (4‑64)")
        ctk.CTkSlider(
            frame_len,
            from_=4,
            to=64,
            number_of_steps=60,
            variable=self.length_var,
            command=self.actualizar,
        ).grid(row=0, column=1, sticky="ew")
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
            ("🔡 Lowercase", self.include_lower, "Letters a‑z"),
            ("🔠 Uppercase", self.include_upper, "Letters A‑Z"),
            ("🔢 Numbers", self.include_digits, "Digits 0‑9"),
            ("❗ Special", self.include_specials, CARACTERES_ESPECIALES),
            ("🚫 Ambiguous", self.exclude_ambiguous, "O, 0, I, l"),
        ]
        opt_frame = ctk.CTkFrame(container, fg_color="#f7f9fa", corner_radius=6)
        opt_frame.grid(row=2, column=0, sticky="ew", pady=10)
        for i in range(2):
            opt_frame.grid_columnconfigure(i, weight=1)
        for idx, (text, var, tip) in enumerate(opts):
            r, c = divmod(idx, 2)
            sw = ctk.CTkSwitch(
                opt_frame,
                text=text,
                variable=var,
                font=ctk.CTkFont(size=14),
                button_color="#1abc9c",
                progress_color="#1abc9c",
                switch_width=50,
                switch_height=24,
                command=self.actualizar,
            )
            sw.grid(row=r, column=c, sticky="w", padx=15, pady=6)
            Tooltip(sw, tip)

        # Strength meter
        st_frame = ctk.CTkFrame(container, fg_color="#f7f9fa", corner_radius=6)
        st_frame.grid(row=3, column=0, sticky="ew", pady=5)
        self.strength_bar = ctk.CTkProgressBar(st_frame, width=300)
        self.strength_bar.pack(fill="x", expand=True, padx=15, pady=(10, 5))
        self.strength_label = ctk.CTkLabel(
            st_frame, text="", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.strength_label.pack(pady=(0, 10))
        Tooltip(self.strength_label, "Level and entropy bits")

        # Password field
        self.pwd_entry = ctk.CTkEntry(
            container,
            textvariable=self.password_var,
            font=ctk.CTkFont(family="Courier New", size=14),
            fg_color="#ffffff",
            text_color="#2c3e50",
            state="readonly",
        )
        self.pwd_entry.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        self.pwd_entry.bind("<Button-1>", lambda _e: self.copy_on_click())
        Tooltip(self.pwd_entry, "Click or Ctrl+C to copy")

        # Show / hide
        show_frame = ctk.CTkFrame(container, fg_color="#ffffff", corner_radius=6)
        show_frame.grid(row=5, column=0, sticky="ew", pady=5)
        show_frame.grid_columnconfigure(0, weight=1)
        show_sw = ctk.CTkSwitch(
            show_frame,
            text="👁 Show password",
            variable=self.show_pwd_var,
            font=ctk.CTkFont(size=14),
            button_color="#95a5a6",
            progress_color="#95a5a6",
            command=self.toggle_show,
        )
        show_sw.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        Tooltip(show_sw, "Hide/show text")

        # Generate button
        btn_frame = ctk.CTkFrame(container, fg_color="#ffffff", corner_radius=6)
        btn_frame.grid(row=6, column=0, sticky="ew", pady=5)
        btn_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            btn_frame,
            text="🔄 Generate",
            height=40,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=self.actualizar,
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        Tooltip(btn_frame, "Generate — Ctrl+R (always new)")

        # Keyboard shortcuts
        accel = "Command" if platform.system() == "Darwin" else "Control"
        self.bind_all(f"<{accel}-r>", lambda _e: self.actualizar())
        self.bind_all(f"<{accel}-R>", lambda _e: self.actualizar())
        self.bind_all(f"<{accel}-c>", lambda _e: self.copy_on_click())
        self.bind_all(f"<{accel}-C>", lambda _e: self.copy_on_click())

        # First generation
        self.actualizar()
        self.toggle_show()

    # ── Generation ───────────────────────────────────────────────
    def generar_contrasena(self):
        """Generate a cryptographically secure password respecting current settings."""
        length = self.length_var.get()
        minus, mayus = string.ascii_lowercase, string.ascii_uppercase
        nums, especs = string.digits, CARACTERES_ESPECIALES
        if self.exclude_ambiguous.get():
            minus = "".join(c for c in minus if c not in AMBIGUOS)
            mayus = "".join(c for c in mayus if c not in AMBIGUOS)
            nums = "".join(c for c in nums if c not in AMBIGUOS)

        disp, aseg = "", []
        if self.include_lower.get():
            disp += minus
            aseg.append(secrets.choice(minus))
        if self.include_upper.get():
            disp += mayus
            aseg.append(secrets.choice(mayus))
        if self.include_digits.get():
            disp += nums
            aseg.append(secrets.choice(nums))
        if self.include_specials.get():
            disp += especs
            aseg.append(secrets.choice(especs))

        if not disp:
            self.password_var.set("Select at least one character type")
            return
        if length < len(aseg):
            length = len(aseg)
            self.length_var.set(length)

        # Cryptographic generation
        for _ in range(10):
            pwd_chars = aseg + [secrets.choice(disp) for _ in range(length - len(aseg))]
            secrets.SystemRandom().shuffle(pwd_chars)  # Secure shuffle
            new_pwd = "".join(pwd_chars)
            if new_pwd != self._last_pwd:
                break
        else:
            idx = secrets.randbelow(length)
            alt_chars = [c for c in disp if c != new_pwd[idx]]
            if alt_chars:
                alt_char = secrets.choice(alt_chars)
                new_pwd = new_pwd[:idx] + alt_char + new_pwd[idx + 1 :]

        self.password_var.set(new_pwd)
        self._last_pwd = new_pwd

    def calcular_fuerza(self):
        """Calculate password strength (entropy) and update the UI."""
        total = 0
        if self.include_lower.get():
            total += len(string.ascii_lowercase) - (4 if self.exclude_ambiguous.get() else 0)
        if self.include_upper.get():
            total += len(string.ascii_uppercase) - (2 if self.exclude_ambiguous.get() else 0)
        if self.include_digits.get():
            total += len(string.digits) - (2 if self.exclude_ambiguous.get() else 0)
        if self.include_specials.get():
            total += len(CARACTERES_ESPECIALES)
        bits = self.length_var.get() * (math.log2(total) if total else 0)
        pct = min(bits / 60, 1.0)
        self.strength_bar.set(pct)
        if bits < 28:
            nivel, color = "Weak", "#e74c3c"
        elif bits < 36:
            nivel, color = "Medium", "#f1c40f"
        else:
            nivel, color = "Strong", "#2ecc71"
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
        if pwd and "Select" not in pwd:
            self.clipboard_clear()
            self.clipboard_append(pwd)
            self.show_toast("Copied!")
        else:
            self.show_toast("Nothing to copy")

    def show_toast(self, text):
        """Display a transient toast message at the bottom of the window."""
        toast = ctk.CTkToplevel(self)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        w, h = 150, 40
        toast.geometry(
            f"{w}x{h}+{self.winfo_x() + (self.winfo_width() - w) // 2}+{self.winfo_y() + self.winfo_height() - 80}"
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
