"""
KALKULATOR PROFESIONAL - Kivy App
Fitur:
- Mode Dasar (+ - * / % )
- Mode Ilmiah (sqrt, pangkat, sin, cos, tan, log, ln, pi, e, 1/x, +/-)
- Toggle Dark Mode / Light Mode
- Bisa di-build ke APK Android lewat Buildozer
"""

import math
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import BooleanProperty, StringProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang import Builder

Window.clearcolor = (0.07, 0.07, 0.09, 1)

# =====================================================
# TEMA WARNA
# =====================================================
THEMES = {
    "dark": {
        "bg": (0.07, 0.07, 0.09, 1),
        "display_bg": (0.12, 0.12, 0.15, 1),
        "text": (1, 1, 1, 1),
        "sub_text": (0.6, 0.6, 0.65, 1),
        "num_btn": (0.18, 0.18, 0.22, 1),
        "num_btn_text": (1, 1, 1, 1),
        "op_btn": (1, 0.55, 0.1, 1),
        "op_btn_text": (1, 1, 1, 1),
        "func_btn": (0.25, 0.25, 0.3, 1),
        "func_btn_text": (1, 1, 1, 1),
        "equal_btn": (0.2, 0.75, 0.45, 1),
        "equal_btn_text": (1, 1, 1, 1),
        "panel": (0.1, 0.1, 0.13, 1),
    },
    "light": {
        "bg": (0.95, 0.95, 0.97, 1),
        "display_bg": (1, 1, 1, 1),
        "text": (0.1, 0.1, 0.1, 1),
        "sub_text": (0.45, 0.45, 0.5, 1),
        "num_btn": (0.92, 0.92, 0.94, 1),
        "num_btn_text": (0.1, 0.1, 0.1, 1),
        "op_btn": (1, 0.55, 0.1, 1),
        "op_btn_text": (1, 1, 1, 1),
        "func_btn": (0.85, 0.85, 0.88, 1),
        "func_btn_text": (0.1, 0.1, 0.1, 1),
        "equal_btn": (0.2, 0.7, 0.45, 1),
        "equal_btn_text": (1, 1, 1, 1),
        "panel": (0.98, 0.98, 1, 1),
    },
}


class RoundedButton(Button):
    """Tombol berbentuk bar/pill (ujung membulat penuh mengikuti tinggi tombol)."""
    bg_color = None

    def __init__(self, bg_color=(0.2, 0.2, 0.2, 1), text_color=(1, 1, 1, 1), radius=18, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = text_color
        self._bg_color_value = bg_color
        with self.canvas.before:
            self._color_instr = Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        # Bentuk bar/pill: radius = setengah tinggi, biar ujung kiri-kanan bulat penuh
        pill_radius = self.height / 2
        self._rect.radius = [pill_radius]

    def set_bg_color(self, color):
        self._color_instr.rgba = color


class ModeToggleButton(Button):
    """Tombol segmented untuk pilih mode, tanpa dialog popup bawaan OS."""

    def __init__(self, bg_color=(0.2, 0.2, 0.2, 1), text_color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ""
        self.background_down = ""
        self.color = text_color
        with self.canvas.before:
            self._color_instr = Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.height / 2]

    def set_bg_color(self, color):
        self._color_instr.rgba = color


class CalculatorLayout(BoxLayout):
    pass


class CalcScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dark_mode = True
        self.current_mode = "Dasar"
        self.expression = ""
        self.is_finalized = False
        self.all_buttons = []  # simpan referensi tombol untuk update tema

        self.root_layout = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        self.add_widget(self.root_layout)

        self._build_top_bar()
        self._build_display()
        self._build_keypad_container()
        self._build_footer()

        self.apply_theme()
        self.build_keypad()

        Clock.schedule_interval(self._update_clock, 1)
        self._update_clock(0)

    # ---------------- TOP BAR ----------------
    def _build_top_bar(self):
        top_bar = BoxLayout(size_hint=(1, 0.08), spacing=dp(10))

        # --- Segmented toggle mode (custom, tanpa dialog popup Android) ---
        self.mode_toggle_box = BoxLayout(size_hint=(0.55, 1), padding=dp(3), spacing=dp(3))
        with self.mode_toggle_box.canvas.before:
            self._mode_box_color = Color(0.1, 0.1, 0.13, 1)
            self._mode_box_rect = RoundedRectangle(pos=self.mode_toggle_box.pos, size=self.mode_toggle_box.size, radius=[18])
        self.mode_toggle_box.bind(pos=self._update_mode_box_rect, size=self._update_mode_box_rect)

        self.btn_mode_dasar = ModeToggleButton(text="Dasar", font_size=dp(14))
        self.btn_mode_ilmiah = ModeToggleButton(text="Ilmiah", font_size=dp(14))
        self.btn_mode_dasar.bind(on_release=lambda inst: self.set_mode("Dasar"))
        self.btn_mode_ilmiah.bind(on_release=lambda inst: self.set_mode("Ilmiah"))
        self.mode_toggle_box.add_widget(self.btn_mode_dasar)
        self.mode_toggle_box.add_widget(self.btn_mode_ilmiah)

        theme_box = BoxLayout(size_hint=(0.45, 1), spacing=dp(8))
        self.theme_label = Label(text="🌙", size_hint=(0.3, 1))
        self.theme_switch = Switch(active=True, size_hint=(0.7, 1))
        self.theme_switch.bind(active=self.on_theme_switch)
        theme_box.add_widget(self.theme_label)
        theme_box.add_widget(self.theme_switch)

        top_bar.add_widget(self.mode_toggle_box)
        top_bar.add_widget(theme_box)
        self.root_layout.add_widget(top_bar)

    def _update_mode_box_rect(self, *args):
        self._mode_box_rect.pos = self.mode_toggle_box.pos
        self._mode_box_rect.size = self.mode_toggle_box.size

    def set_mode(self, mode_name):
        self.current_mode = mode_name
        self.clear_all()
        self.build_keypad()
        self.update_mode_toggle_visual()

    def update_mode_toggle_visual(self):
        theme = THEMES["dark" if self.dark_mode else "light"]
        active_color = theme["op_btn"]
        inactive_color = (0, 0, 0, 0)
        if self.current_mode == "Dasar":
            self.btn_mode_dasar.set_bg_color(active_color)
            self.btn_mode_ilmiah.set_bg_color(inactive_color)
            self.btn_mode_dasar.color = (1, 1, 1, 1)
            self.btn_mode_ilmiah.color = theme["sub_text"]
        else:
            self.btn_mode_ilmiah.set_bg_color(active_color)
            self.btn_mode_dasar.set_bg_color(inactive_color)
            self.btn_mode_ilmiah.color = (1, 1, 1, 1)
            self.btn_mode_dasar.color = theme["sub_text"]

    # ---------------- DISPLAY ----------------
    def _build_display(self):
        self.display_panel = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.28),
            padding=dp(18),
        )
        with self.display_panel.canvas.before:
            self._display_color = Color(0.12, 0.12, 0.15, 1)
            self._display_rect = RoundedRectangle(radius=[20])
        self.display_panel.bind(pos=self._update_display_rect, size=self._update_display_rect)

        self.expr_label = Label(
            text="",
            font_size=dp(20),
            halign="right",
            valign="middle",
            size_hint=(1, 0.4),
            color=(0.6, 0.6, 0.65, 1),
        )
        self.expr_label.bind(size=self._update_label_text_size)

        self.result_label = Label(
            text="0",
            font_size=dp(48),
            halign="right",
            valign="middle",
            size_hint=(1, 0.6),
            bold=True,
        )
        self.result_label.bind(size=self._update_label_text_size)

        self.display_panel.add_widget(self.expr_label)
        self.display_panel.add_widget(self.result_label)
        self.root_layout.add_widget(self.display_panel)

    def _update_display_rect(self, *args):
        self._display_rect.pos = self.display_panel.pos
        self._display_rect.size = self.display_panel.size

    def _update_label_text_size(self, instance, value):
        instance.text_size = (value[0] - dp(10), None)

    # ---------------- FOOTER (lokasi + jam) ----------------
    def _build_footer(self):
        footer = BoxLayout(size_hint=(1, 0.045), padding=(dp(4), 0))

        self.location_label = Label(
            text="📍 Indonesia",
            font_size=dp(11),
            halign="left",
            valign="middle",
            size_hint=(0.5, 1),
        )
        self.location_label.bind(size=self._update_label_text_size)

        self.clock_label = Label(
            text="00:00:00",
            font_size=dp(12),
            bold=True,
            halign="right",
            valign="middle",
            size_hint=(0.5, 1),
        )
        self.clock_label.bind(size=self._update_label_text_size)

        footer.add_widget(self.location_label)
        footer.add_widget(self.clock_label)
        self.root_layout.add_widget(footer)

    def _update_clock(self, dt):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.text = now

    # ---------------- KEYPAD CONTAINER ----------------
    def _build_keypad_container(self):
        self.keypad_container = BoxLayout(size_hint=(1, 0.64))
        self.root_layout.add_widget(self.keypad_container)

    # ---------------- BANGUN KEYPAD SESUAI MODE ----------------
    def build_keypad(self):
        self.keypad_container.clear_widgets()
        self.all_buttons = []

        if self.current_mode == "Dasar":
            grid = self._build_basic_keypad()
        else:
            grid = self._build_scientific_keypad()

        self.keypad_container.add_widget(grid)
        self.apply_theme()

    def _make_btn(self, text, kind="num", callback=None, font_size=dp(22)):
        theme = THEMES["dark" if self.dark_mode else "light"]
        color_map = {
            "num": (theme["num_btn"], theme["num_btn_text"]),
            "op": (theme["op_btn"], theme["op_btn_text"]),
            "func": (theme["func_btn"], theme["func_btn_text"]),
            "equal": (theme["equal_btn"], theme["equal_btn_text"]),
        }
        bg, fg = color_map.get(kind, color_map["num"])
        btn = RoundedButton(text=text, bg_color=bg, text_color=fg, font_size=font_size)
        btn.kind = kind
        if callback:
            btn.bind(on_release=callback)
        else:
            btn.bind(on_release=lambda inst: self.on_key_press(text))
        self.all_buttons.append(btn)
        return btn

    def _build_basic_keypad(self):
        grid = GridLayout(cols=4, spacing=dp(10), padding=dp(4))
        layout = [
            ("C", "func"), ("⌫", "func"), ("%", "func"), ("÷", "op"),
            ("7", "num"), ("8", "num"), ("9", "num"), ("×", "op"),
            ("4", "num"), ("5", "num"), ("6", "num"), ("-", "op"),
            ("1", "num"), ("2", "num"), ("3", "num"), ("+", "op"),
            ("+/-", "func"), ("0", "num"), (".", "num"), ("=", "equal"),
        ]
        for text, kind in layout:
            if text == "=":
                grid.add_widget(self._make_btn(text, kind, callback=self.calculate))
            elif text == "C":
                grid.add_widget(self._make_btn(text, kind, callback=self.clear_all))
            elif text == "⌫":
                grid.add_widget(self._make_btn(text, kind, callback=self.backspace))
            elif text == "+/-":
                grid.add_widget(self._make_btn(text, kind, callback=self.toggle_sign))
            else:
                grid.add_widget(self._make_btn(text, kind))
        return grid

    def _build_scientific_keypad(self):
        grid = GridLayout(cols=5, spacing=dp(8), padding=dp(4))
        layout = [
            ("C", "func"), ("⌫", "func"), ("(", "func"), (")", "func"), ("%", "func"),
            ("sin", "func"), ("cos", "func"), ("tan", "func"), ("log", "func"), ("ln", "func"),
            ("√", "func"), ("x²", "func"), ("^", "func"), ("π", "func"), ("e", "func"),
            ("7", "num"), ("8", "num"), ("9", "num"), ("÷", "op"), ("1/x", "func"),
            ("4", "num"), ("5", "num"), ("6", "num"), ("×", "op"), ("+/-", "func"),
            ("1", "num"), ("2", "num"), ("3", "num"), ("-", "op"), ("0", "num"),
            (".", "num"), ("=", "equal"), ("+", "op"), ("", "hidden"), ("", "hidden"),
        ]
        for text, kind in layout:
            if kind == "hidden":
                grid.add_widget(Label(text=""))
                continue
            if text == "=":
                grid.add_widget(self._make_btn(text, kind, callback=self.calculate, font_size=dp(20)))
            elif text == "C":
                grid.add_widget(self._make_btn(text, kind, callback=self.clear_all, font_size=dp(18)))
            elif text == "⌫":
                grid.add_widget(self._make_btn(text, kind, callback=self.backspace, font_size=dp(18)))
            elif text == "+/-":
                grid.add_widget(self._make_btn(text, kind, callback=self.toggle_sign, font_size=dp(16)))
            elif text in ("sin", "cos", "tan", "log", "ln", "√", "x²", "1/x", "π", "e", "^"):
                grid.add_widget(self._make_btn(text, kind, callback=self.on_sci_func, font_size=dp(17)))
            else:
                grid.add_widget(self._make_btn(text, kind, font_size=dp(19)))
        return grid

    # ---------------- LOGIKA TOMBOL ----------------
    def on_key_press(self, key):
        self.is_finalized = False
        self.expression += key
        self.update_display()

    def on_sci_func(self, instance):
        key = instance.text
        mapping = {
            "sin": "sin(", "cos": "cos(", "tan": "tan(",
            "log": "log(", "ln": "ln(",
            "√": "sqrt(", "x²": "**2", "^": "**",
            "π": "pi", "e": "e", "1/x": "1/(",
        }
        self.is_finalized = False
        self.expression += mapping.get(key, key)
        self.update_display()

    def clear_all(self, instance=None):
        self.expression = ""
        self.is_finalized = False
        self.result_label.text = "0"
        self.expr_label.text = ""

    def backspace(self, instance=None):
        self.expression = self.expression[:-1]
        self.is_finalized = False
        self.update_display()

    def toggle_sign(self, instance=None):
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression
        self.is_finalized = False
        self.update_display()

    def _expr_complete(self, expr):
        """Cek apakah ekspresi sudah 'lengkap' (bukan sedang menunggu angka lanjutan)."""
        if not expr:
            return False
        return expr[-1] not in "+-×÷^(."

    def _to_eval_expr(self, expr):
        e = expr.replace("×", "*").replace("÷", "/")
        e = e.replace("sqrt(", "math.sqrt(")
        e = e.replace("log(", "math.log10(")
        e = e.replace("ln(", "math.log(")
        e = e.replace("sin(", "math.sin(math.radians(")
        e = e.replace("cos(", "math.cos(math.radians(")
        e = e.replace("tan(", "math.tan(math.radians(")
        e = e.replace("pi", "math.pi")
        e = e.replace("e", "math.e")
        close_needed = e.count("(") - e.count(")")
        e += ")" * max(0, close_needed)
        return e

    def _try_live_result(self, expr):
        """Hitung diam-diam kalau ekspresi sudah lengkap & ada operator. None kalau belum bisa."""
        if not self._expr_complete(expr):
            return None
        if not any(op in expr[1:] for op in "+-×÷^"):
            return None
        try:
            hasil = eval(self._to_eval_expr(expr), {"math": math, "__builtins__": {}})
            if isinstance(hasil, float):
                hasil = round(hasil, 8)
                if hasil == int(hasil):
                    hasil = int(hasil)
            return str(hasil)
        except Exception:
            return None

    def _font_size_for(self, text, max_size):
        """Ukuran font mengecil hampir tanpa batas bawah, supaya teks sepanjang apapun tetap muat."""
        length = max(len(text), 1)
        # perkiraan lebar karakter rata-rata (dilebihkan dikit + margin aman biar gak kepotong)
        available_width = self.result_label.width if self.result_label.width > 0 else dp(320)
        available_width *= 0.92  # margin aman
        size = available_width / (length * 0.62)
        size = min(max_size, size)
        size = max(dp(6), size)  # hampir tanpa batas bawah, asal masih kebaca
        return size

    def update_display(self):
        expr_text = self.expression if self.expression else ""
        self.expr_label.text = expr_text
        self.expr_label.font_size = self._font_size_for(expr_text, dp(20))

        live = self._try_live_result(self.expression)
        shown = live if live is not None else (self.expression if self.expression else "0")
        self.result_label.text = shown
        self.result_label.font_size = self._font_size_for(shown, dp(48))

    def calculate(self, instance=None):
        if not self.expression:
            return
        try:
            hasil = self._try_live_result(self.expression)
            if hasil is None:
                # coba hitung penuh meski ekspresi dianggap "belum lengkap" oleh live-check
                hasil_raw = eval(self._to_eval_expr(self.expression), {"math": math, "__builtins__": {}})
                if isinstance(hasil_raw, float):
                    hasil_raw = round(hasil_raw, 8)
                    if hasil_raw == int(hasil_raw):
                        hasil_raw = int(hasil_raw)
                hasil = str(hasil_raw)

            expr_final = self.expression + " ="
            self.expr_label.text = expr_final
            self.expr_label.font_size = self._font_size_for(expr_final, dp(20))

            self.is_finalized = True
            self.result_label.text = hasil
            self.result_label.font_size = self._font_size_for(hasil, dp(48))
            self.expression = hasil
        except ZeroDivisionError:
            self.is_finalized = True
            self.result_label.text = "Error: ÷0"
            self.expression = ""
        except Exception:
            self.is_finalized = True
            self.result_label.text = "Error"
            self.expression = ""

    # ---------------- MODE & TEMA ----------------
    def on_theme_switch(self, switch, value):
        self.dark_mode = value
        self.theme_label.text = "🌙" if value else "☀️"
        self.apply_theme()

    def apply_theme(self, *args):
        theme = THEMES["dark" if self.dark_mode else "light"]
        Window.clearcolor = theme["bg"]
        self._display_color.rgba = theme["display_bg"]
        self._mode_box_color.rgba = theme["panel"]
        self.result_label.color = theme["text"]
        self.expr_label.color = theme["sub_text"]
        self.location_label.color = theme["sub_text"]
        self.clock_label.color = theme["sub_text"]
        self.update_mode_toggle_visual()

        color_map = {
            "num": (theme["num_btn"], theme["num_btn_text"]),
            "op": (theme["op_btn"], theme["op_btn_text"]),
            "func": (theme["func_btn"], theme["func_btn_text"]),
            "equal": (theme["equal_btn"], theme["equal_btn_text"]),
        }
        for btn in self.all_buttons:
            bg, fg = color_map.get(btn.kind, color_map["num"])
            btn.set_bg_color(bg)
            btn.color = fg


class KalkulatorApp(App):
    def build(self):
        self.title = "Kalkulator Pro"
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(CalcScreen(name="calc"))
        return sm


if __name__ == "__main__":
    KalkulatorApp().run()
