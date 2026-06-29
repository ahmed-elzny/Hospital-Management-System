"""
Hospital Database Management System
====================================
Requirements: Python 3.x (tkinter + sqlite3 are built-in, no pip needed)
Run: python hospital_gui.py
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import os

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────
DB_FILE = "hospital.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS DOCTORS (
        doctor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name  TEXT NOT NULL,
        last_name   TEXT NOT NULL,
        specialty   TEXT,
        phone       TEXT,
        email       TEXT
    );
    CREATE TABLE IF NOT EXISTS PATIENTS (
        patient_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name    TEXT NOT NULL,
        last_name     TEXT NOT NULL,
        date_of_birth TEXT,
        gender        TEXT CHECK(gender IN ('Male','Female')),
        phone         TEXT
    );
    CREATE TABLE IF NOT EXISTS APPOINTMENTS (
        appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id        INTEGER NOT NULL,
        patient_id       INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        status           TEXT DEFAULT 'Pending'
                         CHECK(status IN ('Pending','Confirmed','Completed','Cancelled')),
        notes            TEXT,
        FOREIGN KEY (doctor_id)  REFERENCES DOCTORS(doctor_id),
        FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id)
    );
    CREATE TABLE IF NOT EXISTS PRESCRIPTIONS (
        prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id  INTEGER NOT NULL,
        issue_date      TEXT NOT NULL,
        diagnosis       TEXT,
        FOREIGN KEY (appointment_id) REFERENCES APPOINTMENTS(appointment_id)
    );
    CREATE TABLE IF NOT EXISTS MEDICATIONS (
        medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        category      TEXT,
        unit          TEXT,
        price         REAL CHECK(price >= 0)
    );
    """)

    # Sample data only if tables are empty
    if c.execute("SELECT COUNT(*) FROM DOCTORS").fetchone()[0] == 0:
        c.executescript("""
        INSERT INTO DOCTORS (first_name,last_name,specialty,phone,email) VALUES
            ('Ahmed','Mahmoud','Cardiology','01012345678','ahmed@hospital.com'),
            ('Sara','Ali','Pediatrics','01098765432','sara@hospital.com'),
            ('Mohamed','Hassan','General Surgery','01155544433','mo@hospital.com'),
            ('Nadia','Kamal','Neurology','01223344556','nadia@hospital.com');

        INSERT INTO PATIENTS (first_name,last_name,date_of_birth,gender,phone) VALUES
            ('Karim','Abdullah','1990-05-15','Male','01234567890'),
            ('Nour','Ibrahim','1985-11-20','Female','01987654321'),
            ('Tarek','Saeed','2000-03-08','Male','01112223344'),
            ('Hana','Mostafa','1995-07-25','Female','01556677889');

        INSERT INTO APPOINTMENTS (doctor_id,patient_id,appointment_date,status,notes) VALUES
            (1,1,'2026-05-12','Confirmed','Routine checkup'),
            (2,2,'2026-05-13','Pending','First visit'),
            (3,3,'2026-05-14','Completed','Post-op follow up'),
            (4,1,'2026-05-16','Confirmed','MRI results review');

        INSERT INTO PRESCRIPTIONS (appointment_id,issue_date,diagnosis) VALUES
            (3,'2026-05-14','Acute appendicitis - post surgery'),
            (1,'2026-05-12','Hypertension - stage 1');

        INSERT INTO MEDICATIONS (name,category,unit,price) VALUES
            ('Amoxicillin','Antibiotic','Tablet',15.50),
            ('Paracetamol','Analgesic','Tablet',5.00),
            ('Omeprazole','Antacid','Capsule',22.75),
            ('Metformin','Antidiabetic','Tablet',18.00),
            ('Amlodipine','Antihypert.','Tablet',30.00);
        """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# COLORS & FONTS
# ─────────────────────────────────────────────
BG         = "#0F172A"   # dark navy
SIDEBAR_BG = "#1E293B"
CARD_BG    = "#1E293B"
HEADER_BG  = "#0EA5E9"   # sky blue
BTN_INSERT = "#10B981"   # green
BTN_SELECT = "#0EA5E9"   # blue
BTN_UPDATE = "#F59E0B"   # amber
BTN_DELETE = "#EF4444"   # red
BTN_ALTER  = "#8B5CF6"   # violet
BTN_SEARCH = "#EC4899"   # pink
TEXT_LIGHT = "#F1F5F9"
TEXT_MUTED = "#94A3B8"
ACCENT     = "#38BDF8"
INPUT_BG   = "#0F172A"
TABLE_HEAD = "#0EA5E9"
TABLE_ALT  = "#162032"
SUCCESS_BG = "#064E3B"
ERROR_BG   = "#7F1D1D"

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_NORMAL = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 9)

# ─────────────────────────────────────────────
# TABLE CONFIGURATIONS
# ─────────────────────────────────────────────
TABLES = {
    "Doctors": {
        "table": "DOCTORS",
        "pk": "doctor_id",
        "icon": "🩺",
        "color": "#10B981",
        "fields": [
            ("first_name",  "First Name",    "entry",  True),
            ("last_name",   "Last Name",     "entry",  True),
            ("specialty",   "Specialty",     "entry",  False),
            ("phone",       "Phone",         "entry",  False),
            ("email",       "Email",         "entry",  False),
        ],
        "select_sql": "SELECT * FROM DOCTORS",
        "cols": ["ID","First Name","Last Name","Specialty","Phone","Email"],
    },
    "Patients": {
        "table": "PATIENTS",
        "pk": "patient_id",
        "icon": "👤",
        "color": "#0EA5E9",
        "fields": [
            ("first_name",    "First Name",    "entry",  True),
            ("last_name",     "Last Name",     "entry",  True),
            ("date_of_birth", "Date of Birth", "entry",  False),
            ("gender",        "Gender",        "combo",  False, ["Male","Female"]),
            ("phone",         "Phone",         "entry",  False),
        ],
        "select_sql": "SELECT * FROM PATIENTS",
        "cols": ["ID","First Name","Last Name","DOB","Gender","Phone"],
    },
    "Appointments": {
        "table": "APPOINTMENTS",
        "pk": "appointment_id",
        "icon": "📅",
        "color": "#F59E0B",
        "fields": [
            ("doctor_id",        "Doctor ID",   "entry", True),
            ("patient_id",       "Patient ID",  "entry", True),
            ("appointment_date", "Date",        "entry", True),
            ("status",           "Status",      "combo", False,
             ["Pending","Confirmed","Completed","Cancelled"]),
            ("notes",            "Notes",       "entry", False),
        ],
        "select_sql": """
            SELECT a.appointment_id,
                   d.first_name||' '||d.last_name,
                   p.first_name||' '||p.last_name,
                   a.appointment_date, a.status, a.notes
            FROM APPOINTMENTS a
            JOIN DOCTORS  d ON a.doctor_id  = d.doctor_id
            JOIN PATIENTS p ON a.patient_id = p.patient_id
        """,
        "cols": ["ID","Doctor","Patient","Date","Status","Notes"],
    },
    "Prescriptions": {
        "table": "PRESCRIPTIONS",
        "pk": "prescription_id",
        "icon": "📝",
        "color": "#EF4444",
        "fields": [
            ("appointment_id", "Appointment ID", "entry", True),
            ("issue_date",     "Issue Date",     "entry", True),
            ("diagnosis",      "Diagnosis",      "entry", False),
        ],
        "select_sql": """
            SELECT pr.prescription_id, pr.appointment_id,
                   pr.issue_date, pr.diagnosis,
                   d.first_name||' '||d.last_name,
                   p.first_name||' '||p.last_name
            FROM PRESCRIPTIONS pr
            JOIN APPOINTMENTS a ON pr.appointment_id = a.appointment_id
            JOIN DOCTORS      d ON a.doctor_id       = d.doctor_id
            JOIN PATIENTS     p ON a.patient_id      = p.patient_id
        """,
        "cols": ["ID","Appt ID","Date","Diagnosis","Doctor","Patient"],
    },
    "Medications": {
        "table": "MEDICATIONS",
        "pk": "medication_id",
        "icon": "💊",
        "color": "#8B5CF6",
        "fields": [
            ("name",     "Name",     "entry", True),
            ("category", "Category", "entry", False),
            ("unit",     "Unit",     "entry", False),
            ("price",    "Price",    "entry", False),
        ],
        "select_sql": "SELECT * FROM MEDICATIONS",
        "cols": ["ID","Name","Category","Unit","Price"],
    },
}


# ─────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────
class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🏥  Hospital Database Management System")
        self.geometry("1200x750")
        self.minsize(950, 600)
        self.configure(bg=BG)

        init_db()
        self._current_table = "Doctors"
        self._field_vars = {}

        self._build_ui()
        self._switch_table("Doctors")

    # ── UI BUILD ─────────────────────────────
    def _build_ui(self):
        # Left sidebar
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🏥 HospitalDB",
                 bg=SIDEBAR_BG, fg=ACCENT,
                 font=("Segoe UI", 13, "bold"),
                 pady=18).pack(fill=tk.X)

        tk.Frame(sidebar, bg="#334155", height=1).pack(fill=tk.X, padx=12)

        tk.Label(sidebar, text="TABLES",
                 bg=SIDEBAR_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 8, "bold"),
                 pady=8).pack(fill=tk.X, padx=14, anchor="w")

        self._nav_btns = {}
        for name, cfg in TABLES.items():
            btn = tk.Button(sidebar,
                            text=f"  {cfg['icon']}  {name}",
                            bg=SIDEBAR_BG, fg=TEXT_LIGHT,
                            font=FONT_NORMAL,
                            relief="flat", anchor="w",
                            cursor="hand2", bd=0,
                            activebackground="#334155",
                            activeforeground=TEXT_LIGHT,
                            command=lambda n=name: self._switch_table(n))
            btn.pack(fill=tk.X, padx=8, pady=2, ipady=8)
            self._nav_btns[name] = btn

        # Bottom info
        tk.Label(sidebar, text="SQLite3  •  Python tkinter",
                 bg=SIDEBAR_BG, fg=TEXT_MUTED,
                 font=FONT_SMALL).pack(side=tk.BOTTOM, pady=10)

        # Right main area
        main = tk.Frame(self, bg=BG)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header bar
        self._header_frame = tk.Frame(main, bg=HEADER_BG, height=52)
        self._header_frame.pack(fill=tk.X)
        self._header_frame.pack_propagate(False)
        self._header_lbl = tk.Label(self._header_frame,
                                     bg=HEADER_BG, fg="white",
                                     font=FONT_TITLE)
        self._header_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Status bar
        self._status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(main, textvariable=self._status_var,
                               bg="#020617", fg=ACCENT,
                               font=FONT_SMALL, anchor="w", pady=4)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

        # SQL preview
        sql_frame = tk.Frame(main, bg=BG)
        sql_frame.pack(fill=tk.X, padx=14, pady=(6,0))
        tk.Label(sql_frame, text="Last SQL:", bg=BG,
                 fg=TEXT_MUTED, font=FONT_SMALL).pack(side=tk.LEFT)
        self._sql_var = tk.StringVar()
        tk.Label(sql_frame, textvariable=self._sql_var,
                 bg=BG, fg="#7DD3FC",
                 font=FONT_MONO, wraplength=700, anchor="w").pack(side=tk.LEFT, padx=6)

        # Operation buttons row
        ops_frame = tk.Frame(main, bg=BG)
        ops_frame.pack(fill=tk.X, padx=14, pady=8)

        ops = [
            ("➕ INSERT", BTN_INSERT, self._op_insert),
            ("📋 SELECT", BTN_SELECT, self._op_select),
            ("✏️ UPDATE", BTN_UPDATE, self._op_update),
            ("🗑 DELETE",  BTN_DELETE, self._op_delete),
            ("🔧 ALTER",  BTN_ALTER,  self._op_alter),
            ("🔍 SEARCH", BTN_SEARCH, self._op_search),
        ]
        for label, color, cmd in ops:
            tk.Button(ops_frame, text=label,
                      bg=color, fg="white",
                      font=("Segoe UI", 10, "bold"),
                      relief="flat", cursor="hand2",
                      activebackground=color,
                      padx=14, pady=7,
                      command=cmd).pack(side=tk.LEFT, padx=4)

        # Form area (collapsible card)
        self._form_outer = tk.Frame(main, bg=BG)
        self._form_outer.pack(fill=tk.X, padx=14, pady=2)

        self._form_card = tk.Frame(self._form_outer, bg=CARD_BG,
                                    bd=0, relief="flat")
        self._form_card.pack(fill=tk.X)
        self._form_title_lbl = tk.Label(self._form_card,
                                         text="", bg=CARD_BG,
                                         fg=ACCENT, font=FONT_HEADER,
                                         pady=8, padx=12, anchor="w")
        self._form_title_lbl.pack(fill=tk.X)

        self._fields_frame = tk.Frame(self._form_card, bg=CARD_BG)
        self._fields_frame.pack(fill=tk.X, padx=12, pady=(0,8))

        self._action_frame = tk.Frame(self._form_card, bg=CARD_BG)
        self._action_frame.pack(fill=tk.X, padx=12, pady=(0,10))

        # Table / results
        tbl_outer = tk.Frame(main, bg=BG)
        tbl_outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)

        cols_bar = tk.Frame(tbl_outer, bg=BG)
        cols_bar.pack(fill=tk.X)
        self._row_count_lbl = tk.Label(cols_bar, text="",
                                        bg=BG, fg=TEXT_MUTED, font=FONT_SMALL)
        self._row_count_lbl.pack(side=tk.RIGHT)

        # Treeview
        tree_frame = tk.Frame(tbl_outer, bg=BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Hospital.Treeview",
                         background=CARD_BG,
                         foreground=TEXT_LIGHT,
                         fieldbackground=CARD_BG,
                         rowheight=26,
                         font=FONT_NORMAL)
        style.configure("Hospital.Treeview.Heading",
                         background=TABLE_HEAD,
                         foreground="white",
                         font=("Segoe UI", 10, "bold"),
                         relief="flat")
        style.map("Hospital.Treeview",
                  background=[("selected","#1D4ED8")])

        self._tree = ttk.Treeview(tree_frame, style="Hospital.Treeview",
                                   show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                             command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,
                              xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

    # ── NAVIGATION ───────────────────────────
    def _switch_table(self, name):
        self._current_table = name
        cfg = TABLES[name]
        for n, btn in self._nav_btns.items():
            btn.configure(bg=cfg["color"] if n == name else SIDEBAR_BG,
                          fg="white" if n == name else TEXT_LIGHT,
                          font=("Segoe UI", 10, "bold") if n == name
                               else FONT_NORMAL)
        self._header_frame.configure(bg=cfg["color"])
        self._header_lbl.configure(
            text=f"{cfg['icon']}  {name}",
            bg=cfg["color"])
        self._clear_form()
        self._op_select()

    # ── FORM HELPERS ─────────────────────────
    def _clear_form(self):
        for w in self._fields_frame.winfo_children():
            w.destroy()
        for w in self._action_frame.winfo_children():
            w.destroy()
        self._field_vars = {}
        self._form_title_lbl.configure(text="")
        self._sql_var.set("")

    def _build_fields(self, fields, prefix=""):
        """Render label+widget pairs in a responsive grid."""
        for i, fdef in enumerate(fields):
            name, label = fdef[0], fdef[1]
            kind = fdef[2] if len(fdef) > 2 else "entry"
            required = fdef[3] if len(fdef) > 3 else False
            options  = fdef[4] if len(fdef) > 4 else []

            col = (i % 3) * 2
            row = i // 3

            lbl_text = f"{label}{'  *' if required else ''}"
            tk.Label(self._fields_frame, text=lbl_text,
                     bg=CARD_BG, fg=TEXT_MUTED,
                     font=FONT_SMALL, anchor="w").grid(
                row=row*2, column=col, sticky="w",
                padx=(0,8), pady=(6,1))

            key = prefix + name
            if kind == "combo":
                var = tk.StringVar()
                w = ttk.Combobox(self._fields_frame, textvariable=var,
                                  values=options, state="readonly", width=18,
                                  font=FONT_NORMAL)
                if options:
                    w.current(0)
            else:
                var = tk.StringVar()
                w = tk.Entry(self._fields_frame, textvariable=var,
                              bg=INPUT_BG, fg=TEXT_LIGHT,
                              insertbackground=TEXT_LIGHT,
                              font=FONT_NORMAL, relief="flat",
                              width=20,
                              highlightthickness=1,
                              highlightcolor=ACCENT,
                              highlightbackground="#334155")
            w.grid(row=row*2+1, column=col, sticky="ew",
                   padx=(0,14), pady=(0,4))
            self._fields_frame.columnconfigure(col, weight=1)
            self._field_vars[key] = var

    def _get_vals(self, fields, prefix=""):
        return {f[0]: self._field_vars.get(prefix+f[0],
                tk.StringVar()).get().strip()
                for f in fields}

    def _add_btn(self, text, color, cmd):
        tk.Button(self._action_frame, text=text,
                  bg=color, fg="white",
                  font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2",
                  activebackground=color,
                  padx=12, pady=5,
                  command=cmd).pack(side=tk.LEFT, padx=4)

    # ── STATUS / SQL ─────────────────────────
    def _show_status(self, msg, ok=True):
        self._status_var.set(msg)
        self.configure(bg=SUCCESS_BG if ok else ERROR_BG)
        self.after(2500, lambda: self.configure(bg=BG))

    def _show_sql(self, sql):
        single = " ".join(sql.split())
        self._sql_var.set(single[:130] + ("…" if len(single) > 130 else ""))

    # ── RENDER TABLE ─────────────────────────
    def _render_rows(self, rows, cols):
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._tree["columns"] = cols
        for col in cols:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=max(90, len(col)*11),
                               anchor="center", stretch=True)
        for i, row in enumerate(rows):
            tag = "alt" if i % 2 else "norm"
            self._tree.insert("", "end", values=row, tags=(tag,))
        self._tree.tag_configure("alt",  background=TABLE_ALT)
        self._tree.tag_configure("norm", background=CARD_BG)
        self._row_count_lbl.configure(
            text=f"{len(rows)} row{'s' if len(rows) != 1 else ''}")

    # ─────────────────────────────────────────
    # OPERATIONS
    # ─────────────────────────────────────────

    def _op_select(self):
        cfg = TABLES[self._current_table]
        sql = cfg["select_sql"]
        self._show_sql(sql)
        try:
            conn = get_conn()
            rows = conn.execute(sql).fetchall()
            conn.close()
            self._render_rows(rows, cfg["cols"])
            self._show_status(f"✅ SELECT: {len(rows)} rows returned")
        except Exception as e:
            self._show_status(f"❌ Error: {e}", ok=False)
        self._clear_form()
        self._form_title_lbl.configure(text="📋  SELECT — All Records")

    def _op_insert(self):
        cfg = TABLES[self._current_table]
        self._clear_form()
        self._form_title_lbl.configure(text="➕  INSERT — Add New Record")

        self._build_fields(cfg["fields"], prefix="ins_")

        def do_insert():
            vals = self._get_vals(cfg["fields"], prefix="ins_")
            required = [f[0] for f in cfg["fields"] if len(f) > 3 and f[3]]
            if any(not vals[k] for k in required):
                messagebox.showwarning("Missing", "Please fill required (*) fields.")
                return
            col_names = [f[0] for f in cfg["fields"]]
            placeholders = ",".join(["?"] * len(col_names))
            sql = (f"INSERT INTO {cfg['table']} "
                   f"({','.join(col_names)}) VALUES ({placeholders})")
            self._show_sql(sql)
            try:
                conn = get_conn()
                conn.execute(sql, [vals[c] for c in col_names])
                conn.commit()
                conn.close()
                self._show_status("✅ INSERT successful!")
                self._op_select()
            except Exception as e:
                self._show_status(f"❌ Error: {e}", ok=False)
                messagebox.showerror("DB Error", str(e))

        self._add_btn("✅  Save", BTN_INSERT, do_insert)
        self._add_btn("↩  Clear", "#475569",
                      lambda: [v.set("") for v in self._field_vars.values()])

    def _op_update(self):
        cfg = TABLES[self._current_table]
        self._clear_form()
        self._form_title_lbl.configure(
            text=f"✏️  UPDATE — Modify a Record  "
                 f"(enter {cfg['pk']} to identify the row)")

        # ID field
        tk.Label(self._fields_frame,
                 text=f"🔑  {cfg['pk']}  (required)",
                 bg=CARD_BG, fg="#FCD34D",
                 font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0,8), pady=(6,1))
        id_var = tk.StringVar()
        tk.Entry(self._fields_frame, textvariable=id_var,
                 bg=INPUT_BG, fg="#FCD34D",
                 insertbackground=TEXT_LIGHT,
                 font=FONT_NORMAL, relief="flat", width=12,
                 highlightthickness=1,
                 highlightcolor="#FCD34D",
                 highlightbackground="#334155").grid(
            row=1, column=0, sticky="w", padx=(0,14))

        self._build_fields(cfg["fields"], prefix="upd_")

        def do_update():
            pk_val = id_var.get().strip()
            if not pk_val:
                messagebox.showwarning("Missing", f"Enter the {cfg['pk']}.")
                return
            vals = self._get_vals(cfg["fields"], prefix="upd_")
            sets = [(f[0], v) for f, v in
                    zip(cfg["fields"], vals.values()) if v]
            if not sets:
                messagebox.showwarning("Nothing to update",
                                       "Fill at least one field to change.")
                return
            set_clause = ", ".join(f"{k}=?" for k, _ in sets)
            sql = (f"UPDATE {cfg['table']} SET {set_clause} "
                   f"WHERE {cfg['pk']}=?")
            params = [v for _, v in sets] + [pk_val]
            self._show_sql(sql)
            try:
                conn = get_conn()
                cur = conn.execute(sql, params)
                conn.commit()
                conn.close()
                if cur.rowcount == 0:
                    messagebox.showinfo("Not found",
                                        f"No record with {cfg['pk']} = {pk_val}")
                else:
                    self._show_status(f"✅ UPDATE: {cur.rowcount} row(s) updated")
                    self._op_select()
            except Exception as e:
                self._show_status(f"❌ Error: {e}", ok=False)
                messagebox.showerror("DB Error", str(e))

        self._add_btn("💾  Update", BTN_UPDATE, do_update)

    def _op_delete(self):
        cfg = TABLES[self._current_table]
        self._clear_form()
        self._form_title_lbl.configure(
            text=f"🗑  DELETE — Remove a Record by {cfg['pk']}")

        tk.Label(self._fields_frame,
                 text=f"{cfg['pk']}  (required)",
                 bg=CARD_BG, fg=TEXT_MUTED, font=FONT_SMALL).grid(
            row=0, column=0, sticky="w", pady=(6,1))
        id_var = tk.StringVar()
        tk.Entry(self._fields_frame, textvariable=id_var,
                 bg=INPUT_BG, fg=BTN_DELETE,
                 insertbackground=TEXT_LIGHT,
                 font=FONT_NORMAL, relief="flat", width=14,
                 highlightthickness=1,
                 highlightcolor=BTN_DELETE,
                 highlightbackground="#334155").grid(
            row=1, column=0, sticky="w")

        def do_delete():
            pk_val = id_var.get().strip()
            if not pk_val:
                messagebox.showwarning("Missing", f"Enter {cfg['pk']}.")
                return
            if not messagebox.askyesno("Confirm Delete",
                                        f"Delete record where {cfg['pk']} = {pk_val}?\n"
                                        "This cannot be undone!"):
                return
            sql = f"DELETE FROM {cfg['table']} WHERE {cfg['pk']}=?"
            self._show_sql(sql)
            try:
                conn = get_conn()
                cur = conn.execute(sql, [pk_val])
                conn.commit()
                conn.close()
                if cur.rowcount == 0:
                    messagebox.showinfo("Not found",
                                        f"No record with {cfg['pk']} = {pk_val}")
                else:
                    self._show_status(f"🗑 DELETE: {cur.rowcount} row(s) deleted")
                    self._op_select()
            except Exception as e:
                self._show_status(f"❌ Error: {e}", ok=False)
                messagebox.showerror("DB Error", str(e))

        self._add_btn("🗑  Delete", BTN_DELETE, do_delete)

    def _op_alter(self):
        cfg = TABLES[self._current_table]
        self._clear_form()
        self._form_title_lbl.configure(
            text=f"🔧  ALTER TABLE — Add a New Column to {cfg['table']}")

        labels = ["New Column Name", "Data Type"]
        keys   = ["col_name", "col_type"]
        types  = ["TEXT", "INTEGER", "REAL", "BLOB"]

        tk.Label(self._fields_frame, text="New Column Name",
                 bg=CARD_BG, fg=TEXT_MUTED, font=FONT_SMALL).grid(
            row=0, column=0, sticky="w", padx=(0,10), pady=(6,1))
        col_name_var = tk.StringVar()
        tk.Entry(self._fields_frame, textvariable=col_name_var,
                 bg=INPUT_BG, fg=TEXT_LIGHT,
                 insertbackground=TEXT_LIGHT,
                 font=FONT_NORMAL, relief="flat", width=18,
                 highlightthickness=1, highlightcolor=BTN_ALTER,
                 highlightbackground="#334155").grid(
            row=1, column=0, sticky="w", padx=(0,10))

        tk.Label(self._fields_frame, text="Data Type",
                 bg=CARD_BG, fg=TEXT_MUTED, font=FONT_SMALL).grid(
            row=0, column=2, sticky="w", pady=(6,1))
        col_type_var = tk.StringVar(value="TEXT")
        ttk.Combobox(self._fields_frame, textvariable=col_type_var,
                      values=types, state="readonly",
                      width=12, font=FONT_NORMAL).grid(
            row=1, column=2, sticky="w")

        def do_alter():
            col = col_name_var.get().strip()
            typ = col_type_var.get().strip()
            if not col:
                messagebox.showwarning("Missing", "Enter column name.")
                return
            sql = f"ALTER TABLE {cfg['table']} ADD COLUMN {col} {typ}"
            self._show_sql(sql)
            try:
                conn = get_conn()
                conn.execute(sql)
                conn.commit()
                conn.close()
                self._show_status(
                    f"✅ ALTER: column '{col}' ({typ}) added to {cfg['table']}")
                self._op_select()
            except Exception as e:
                self._show_status(f"❌ Error: {e}", ok=False)
                messagebox.showerror("DB Error", str(e))

        self._add_btn("🔧  Add Column", BTN_ALTER, do_alter)

    def _op_search(self):
        cfg = TABLES[self._current_table]
        self._clear_form()
        self._form_title_lbl.configure(
            text="🔍  SEARCH — Filter Records")

        field_names = [f[0] for f in cfg["fields"]]
        field_labels= [f[1] for f in cfg["fields"]]

        tk.Label(self._fields_frame, text="Search in column",
                 bg=CARD_BG, fg=TEXT_MUTED, font=FONT_SMALL).grid(
            row=0, column=0, sticky="w", padx=(0,10), pady=(6,1))
        col_var = tk.StringVar(value=field_names[0])
        ttk.Combobox(self._fields_frame, textvariable=col_var,
                      values=field_names, state="readonly",
                      width=18, font=FONT_NORMAL).grid(
            row=1, column=0, sticky="w", padx=(0,14))

        tk.Label(self._fields_frame, text="Search keyword",
                 bg=CARD_BG, fg=TEXT_MUTED, font=FONT_SMALL).grid(
            row=0, column=2, sticky="w", pady=(6,1))
        kw_var = tk.StringVar()
        tk.Entry(self._fields_frame, textvariable=kw_var,
                 bg=INPUT_BG, fg=TEXT_LIGHT,
                 insertbackground=TEXT_LIGHT,
                 font=FONT_NORMAL, relief="flat", width=20,
                 highlightthickness=1, highlightcolor=BTN_SEARCH,
                 highlightbackground="#334155").grid(
            row=1, column=2, sticky="w")

        def do_search():
            col = col_var.get()
            kw  = kw_var.get().strip()
            if not kw:
                messagebox.showwarning("Missing", "Enter a search keyword.")
                return
            sql = (f"SELECT * FROM {cfg['table']} "
                   f"WHERE {col} LIKE ?")
            self._show_sql(sql + f"  [{kw}]")
            try:
                conn = get_conn()
                rows = conn.execute(sql, [f"%{kw}%"]).fetchall()
                conn.close()
                # Use raw cols from schema
                raw_cols = [f[0] for f in cfg["fields"]]
                all_cols = [cfg["pk"]] + raw_cols
                self._render_rows(rows, all_cols)
                self._show_status(
                    f"🔍 SEARCH: {len(rows)} match(es) for '{kw}' in {col}")
            except Exception as e:
                self._show_status(f"❌ Error: {e}", ok=False)
                messagebox.showerror("DB Error", str(e))

        self._add_btn("🔍  Search", BTN_SEARCH, do_search)
        # Enter key triggers search
        self.bind("<Return>", lambda e: do_search())


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
