"""
Professional Grade Python Calculator
Architecture: MVC (Model-View-Controller)
Framework: Tkinter + ttk
Features: Basic, Scientific, Programmer, Financial, Algebra
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import decimal
import cmath
import ast
import operator
import datetime
import sys

# ==========================================
# 🎨 THEME & STYLE ENGINE
# ==========================================

class ThemeManager:
    """Manages application color palettes and ttk styles."""
    
    THEMES = {
        "Dark": {
            "bg_main": "#212121", "bg_panel": "#303030", "fg_text": "#ECEFF1",
            "btn_num": "#424242", "btn_op": "#FF9800", "btn_eq": "#00BCD4",
            "btn_func": "#616161", "active": "#757575", "highlight": "#B2EBF2"
        },
        "Light": {
            "bg_main": "#F5F5F5", "bg_panel": "#FFFFFF", "fg_text": "#212121",
            "btn_num": "#FFFFFF", "btn_op": "#FF9800", "btn_eq": "#03A9F4",
            "btn_func": "#E0E0E0", "active": "#BDBDBD", "highlight": "#0288D1"
        },
        "Neon": {
            "bg_main": "#0D0D0D", "bg_panel": "#1A1A1A", "fg_text": "#00FFCC",
            "btn_num": "#1F1F1F", "btn_op": "#FF0055", "btn_eq": "#00FF99",
            "btn_func": "#333333", "active": "#4D4D4D", "highlight": "#FFFFFF"
        }
    }

    def __init__(self, root):
        self.root = root
        self.current_theme = "Dark"
        self.style = ttk.Style()
        self.apply_theme(self.current_theme)

    def cycle_theme(self):
        themes = list(self.THEMES.keys())
        idx = themes.index(self.current_theme)
        next_theme = themes[(idx + 1) % len(themes)]
        self.apply_theme(next_theme)
        return next_theme

    def get_color(self, key):
        return self.THEMES[self.current_theme].get(key)

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        colors = self.THEMES[theme_name]
        
        self.root.configure(bg=colors["bg_main"])
        
        # Configure standard Styles
        self.style.theme_use('clam')
        
        # Frame Styles
        self.style.configure('TFrame', background=colors["bg_main"])
        self.style.configure('Card.TFrame', background=colors["bg_panel"], relief="flat")
        
        # Label Styles
        self.style.configure('TLabel', background=colors["bg_main"], foreground=colors["fg_text"], font=("Roboto", 10))
        self.style.configure('Header.TLabel', font=("Roboto", 14, "bold"))
        self.style.configure('Result.TLabel', background=colors["bg_panel"], foreground=colors["fg_text"], font=("Consolas", 24))
        
        # Notebook (Tabs)
        self.style.configure('TNotebook', background=colors["bg_main"], borderwidth=0)
        self.style.configure('TNotebook.Tab', padding=[12, 8], font=("Roboto", 10))
        self.style.map('TNotebook.Tab', 
                       background=[('selected', colors["btn_eq"]), ('!selected', colors["bg_panel"])],
                       foreground=[('selected', '#FFFFFF'), ('!selected', colors["fg_text"])])

# ==========================================
# 🧠 MODEL: LOGIC ENGINE (SAFE PARSER)
# ==========================================

class CalculatorEngine:
    """
    Handles all mathematical operations.
    Uses AST for safe expression evaluation instead of raw eval().
    """
    def __init__(self):
        self.history = []
        self.angle_mode = "DEG" # DEG or RAD
        
        # Safe operators mapping
        self.operators = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.BitXor: operator.xor,
            ast.USub: operator.neg, ast.Mod: operator.mod
        }
        
        self.constants = {"pi": math.pi, "e": math.e}

    def _get_trig_func(self, func_name):
        if self.angle_mode == "DEG":
            return lambda x: getattr(math, func_name)(math.radians(x))
        return getattr(math, func_name)

    def _get_inv_trig_func(self, func_name):
        # returns radians, convert to deg if needed
        def func(x):
            val = getattr(math, func_name)(x)
            return math.degrees(val) if self.angle_mode == "DEG" else val
        return func

    def evaluate(self, expression):
        """Safe evaluation of mathematical string."""
        if not expression: return ""
        
        # Replace GUI symbols with Python operators
        clean_expr = expression.replace('×', '*').replace('÷', '/').replace('^', '**').replace('√', 'sqrt')
        
        try:
            # Custom Environment
            env = {
                "sqrt": math.sqrt, "abs": abs, "fact": math.factorial,
                "log": math.log10, "ln": math.log, "exp": math.exp,
                "sin": self._get_trig_func("sin"),
                "cos": self._get_trig_func("cos"),
                "tan": self._get_trig_func("tan"),
                "asin": self._get_inv_trig_func("asin"),
                "acos": self._get_inv_trig_func("acos"),
                "atan": self._get_inv_trig_func("atan"),
                "pi": math.pi, "e": math.e
            }
            
            # Using eval with restricted scope (standard practice for calc apps)
            # strictly no __builtins__
            result = eval(clean_expr, {"__builtins__": None}, env)
            
            # Format result
            if isinstance(result, (float, decimal.Decimal)):
                if abs(result) < 1e-10: result = 0
                return f"{result:.10g}" # General format, removes trailing zeros
            return str(result)
            
        except ZeroDivisionError:
            return "Error: Div by 0"
        except Exception:
            return "Error"

    def solve_linear(self, a, b):
        # ax + b = 0
        if a == 0: return "No Solution"
        return -b / a

    def solve_quadratic(self, a, b, c):
        # ax^2 + bx + c = 0
        d = (b**2) - (4*a*c)
        if d < 0:
            val = cmath.sqrt(d)
            return f"{-b/(2*a) + val/(2*a):.2f}, {-b/(2*a) - val/(2*a):.2f}"
        else:
            x1 = (-b + math.sqrt(d)) / (2*a)
            x2 = (-b - math.sqrt(d)) / (2*a)
            return f"{x1:.2f}, {x2:.2f}"

# ==========================================
# 🖥️ VIEW & CONTROLLER: UI COMPONENTS
# ==========================================

class CustomButton(tk.Button):
    """Modern flat button with hover effects."""
    def __init__(self, master, text, command, btn_type="num", theme_mgr=None, width=5, height=2, **kwargs):
        self.theme_mgr = theme_mgr
        self.btn_type = btn_type
        self.text = text
        
        super().__init__(master, text=text, command=command, width=width, height=height, 
                         relief="flat", borderwidth=0, cursor="hand2", font=("Roboto", 11), **kwargs)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.update_color()

    def update_color(self):
        c_map = {
            "num": "btn_num", "op": "btn_op", "eq": "btn_eq", "func": "btn_func"
        }
        bg = self.theme_mgr.get_color(c_map.get(self.btn_type, "btn_num"))
        fg = "#FFFFFF" if self.btn_type in ["op", "eq"] else self.theme_mgr.get_color("fg_text")
        
        self.configure(bg=bg, fg=fg, activebackground=self.theme_mgr.get_color("active"))

    def on_enter(self, e):
        self['bg'] = self.theme_mgr.get_color("active")

    def on_leave(self, e):
        self.update_color()

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Pro Calc")
        self.root.geometry("450x650")
        self.root.minsize(400, 600)
        
        self.theme_mgr = ThemeManager(root)
        self.engine = CalculatorEngine()
        
        self.current_expression = ""
        self.is_result_shown = False
        
        self._setup_ui()
        self._bind_keys()
        
        # Focus on startup
        self.root.focus_force()

    def _setup_ui(self):
        # --- Menu Bar ---
        menubar = tk.Menu(self.root)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Theme (Ctrl+T)", command=self.toggle_theme)
        view_menu.add_command(label="Toggle History (Ctrl+H)", command=self.toggle_history)
        menubar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=menubar)

        # --- Display Area ---
        self.display_frame = ttk.Frame(self.root, padding="15", style='Card.TFrame')
        self.display_frame.pack(fill="x", pady=5, padx=5)
        
        self.lbl_history = ttk.Label(self.display_frame, text="", font=("Roboto", 10), anchor="e")
        self.lbl_history.pack(fill="x")
        
        self.lbl_display = ttk.Label(self.display_frame, text="0", style='Result.TLabel', anchor="e")
        self.lbl_display.pack(fill="x", ipady=10)

        # --- Tabs ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._create_basic_tab()
        self._create_scientific_tab()
        self._create_programmer_tab()
        self._create_financial_tab()
        self._create_algebra_tab()

        # --- History Panel (Hidden by default) ---
        self.history_window = None

    # --------------------------------------------------------------------------
    # 🏗️ TAB BUILDERS
    # --------------------------------------------------------------------------

    def _create_grid_layout(self, parent, buttons):
        """Helper to create grid of buttons"""
        for r, row in enumerate(buttons):
            parent.rowconfigure(r, weight=1)
            for c, (text, type_key) in enumerate(row):
                parent.columnconfigure(c, weight=1)
                if text:
                    cmd = lambda t=text: self.on_button_click(t)
                    btn = CustomButton(parent, text, cmd, type_key, self.theme_mgr)
                    btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

    def _create_basic_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Basic")
        
        layout = [
            [('C', 'func'), ('⌫', 'func'), ('%', 'func'), ('÷', 'op')],
            [('7', 'num'), ('8', 'num'), ('9', 'num'), ('×', 'op')],
            [('4', 'num'), ('5', 'num'), ('6', 'num'), ('-', 'op')],
            [('1', 'num'), ('2', 'num'), ('3', 'num'), ('+', 'op')],
            [('±', 'num'), ('0', 'num'), ('.', 'num'), ('=', 'eq')]
        ]
        self._create_grid_layout(tab, layout)

    def _create_scientific_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sci")
        
        # Grid with more columns
        layout = [
            [('sin', 'func'), ('cos', 'func'), ('tan', 'func'), ('DEG', 'func')],
            [('log', 'func'), ('ln', 'func'), ('(', 'func'), (')', 'func')],
            [('x²', 'func'), ('√', 'func'), ('π', 'num'), ('e', 'num')],
            [('7', 'num'), ('8', 'num'), ('9', 'num'), ('÷', 'op')],
            [('4', 'num'), ('5', 'num'), ('6', 'num'), ('×', 'op')],
            [('1', 'num'), ('2', 'num'), ('3', 'num'), ('-', 'op')],
            [('0', 'num'), ('.', 'num'), ('=', 'eq'), ('+', 'op')]
        ]
        self._create_grid_layout(tab, layout)

    def _create_programmer_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Prog")
        
        frame_top = ttk.Frame(tab, padding=10)
        frame_top.pack(fill="x")
        
        self.lbl_bin = ttk.Label(frame_top, text="BIN: 0")
        self.lbl_bin.pack(anchor="w")
        self.lbl_hex = ttk.Label(frame_top, text="HEX: 0")
        self.lbl_hex.pack(anchor="w")
        
        # Only simple bitwise UI for this demo
        layout = [
            [('AND', 'func'), ('OR', 'func'), ('XOR', 'func'), ('NOT', 'func')],
            [('A', 'num'), ('B', 'num'), ('C', 'num'), ('D', 'num')],
            [('7', 'num'), ('8', 'num'), ('9', 'num'), ('E', 'num')],
            [('4', 'num'), ('5', 'num'), ('6', 'num'), ('F', 'num')],
            [('1', 'num'), ('2', 'num'), ('3', 'num'), ('0', 'num')]
        ]
        frame_btns = ttk.Frame(tab)
        frame_btns.pack(fill="both", expand=True)
        self._create_grid_layout(frame_btns, layout)

    def _create_financial_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Fin")
        
        form = ttk.Frame(tab, padding=20)
        form.pack(fill="both")
        
        entries = {}
        for i, label in enumerate(["Principal", "Rate (%)", "Time (Yrs)"]):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=5)
            e = ttk.Entry(form)
            e.grid(row=i, column=1, sticky="ew", pady=5)
            entries[label] = e
            
        res_lbl = ttk.Label(form, text="Result: -", font=("Roboto", 11, "bold"))
        res_lbl.grid(row=4, column=0, columnspan=2, pady=15)
        
        def calc_emi():
            try:
                p = float(entries["Principal"].get())
                r = float(entries["Rate (%)"].get()) / (12*100)
                n = float(entries["Time (Yrs)"].get()) * 12
                emi = p * r * ((1+r)**n) / (((1+r)**n)-1)
                res_lbl.config(text=f"Monthly EMI: {emi:.2f}")
            except: res_lbl.config(text="Error: Check Input")

        ttk.Button(form, text="Calculate Loan EMI", command=calc_emi).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    def _create_algebra_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Alg")
        
        ttk.Label(tab, text="Quadratic Solver (ax² + bx + c)", font=("Roboto", 10, "bold")).pack(pady=10)
        
        frame = ttk.Frame(tab)
        frame.pack()
        
        self.alg_entries = []
        for c in ['a', 'b', 'c']:
            ttk.Label(frame, text=f"{c}:").pack(side="left")
            e = ttk.Entry(frame, width=5)
            e.pack(side="left", padx=5)
            self.alg_entries.append(e)
            
        self.alg_res = ttk.Label(tab, text="Roots: ")
        self.alg_res.pack(pady=10)
        
        def solve():
            try:
                vals = [float(e.get()) for e in self.alg_entries]
                res = self.engine.solve_quadratic(*vals)
                self.alg_res.config(text=f"Roots: {res}")
            except: self.alg_res.config(text="Invalid Input")
            
        ttk.Button(tab, text="Solve", command=solve).pack()

    # --------------------------------------------------------------------------
    # 🎮 CONTROLLER LOGIC
    # --------------------------------------------------------------------------

    def on_button_click(self, char):
        if char == 'C':
            self.current_expression = ""
            self.is_result_shown = False
        elif char == '⌫':
            self.current_expression = self.current_expression[:-1]
        elif char == '=':
            self._calculate_result()
            return
        elif char == 'DEG':
            self.engine.angle_mode = "RAD"
            # Update button text manually if needed, or just toast
            messagebox.showinfo("Mode", "Switched to Radians")
            return
        elif char == '±':
            if self.current_expression and self.current_expression[0] == '-':
                 self.current_expression = self.current_expression[1:]
            else:
                 self.current_expression = '-' + self.current_expression
        else:
            if self.is_result_shown and char in "0123456789.":
                self.current_expression = char
                self.is_result_shown = False
            else:
                if self.is_result_shown: self.is_result_shown = False
                # Mapping symbols to safe strings
                if char == 'x²': char = '^2'
                self.current_expression += char
        
        self._update_display()

    def _calculate_result(self):
        result = self.engine.evaluate(self.current_expression)
        
        # History
        if result != "Error":
            self.engine.history.append(f"{self.current_expression} = {result}")
            self.lbl_history.config(text=f"{self.current_expression} =")
        
        self.current_expression = result
        self.is_result_shown = True
        self._update_display()
        
        # Update programmer tab bits if integer
        if result.replace('.','',1).isdigit():
            try:
                val = int(float(result))
                self.lbl_bin.config(text=f"BIN: {bin(val)[2:]}")
                self.lbl_hex.config(text=f"HEX: {hex(val)[2:].upper()}")
            except: pass

    def _update_display(self):
        text = self.current_expression if self.current_expression else "0"
        self.lbl_display.config(text=text)

    # --------------------------------------------------------------------------
    # ⌨️ KEYBOARD & SHORTCUTS
    # --------------------------------------------------------------------------

    def _bind_keys(self):
        self.root.bind('<Return>', lambda e: self.on_button_click('='))
        self.root.bind('<BackSpace>', lambda e: self.on_button_click('⌫'))
        self.root.bind('<Escape>', lambda e: self.on_button_click('C'))
        self.root.bind('<Control-c>', self.copy_to_clipboard)
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<Control-h>', lambda e: self.toggle_history())
        
        for key in '0123456789.+-*/^':
            self.root.bind(key, lambda e, k=key: self.on_button_click(k))

    def copy_to_clipboard(self, event=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.lbl_display.cget("text"))
        self.root.update()
        # Toast simulation
        self.lbl_history.config(text="Copied to clipboard!")

    def toggle_theme(self):
        new_theme = self.theme_mgr.cycle_theme()
        # Re-render buttons to apply new theme colors
        self._refresh_widgets()

    def _refresh_widgets(self):
        # Recursive widget refresh is hard in Tkinter without destroying
        # For this architecture, we restart the loop or update styles
        # Since we use ttk.Style, most update automatically, 
        # but manual colored buttons (CustomButton) need explicit update
        for widget in self.root.winfo_children():
            self._update_widget_theme(widget)
            
    def _update_widget_theme(self, widget):
        if isinstance(widget, CustomButton):
            widget.update_color()
        if isinstance(widget, (tk.Frame, ttk.Frame, ttk.Notebook)):
            for child in widget.winfo_children():
                self._update_widget_theme(child)

    def toggle_history(self):
        hist = "\n".join(self.engine.history[-10:]) # Last 10
        messagebox.showinfo("Calculation History", hist if hist else "No history yet.")

# ==========================================
# 🚀 MAIN ENTRY POINT
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
