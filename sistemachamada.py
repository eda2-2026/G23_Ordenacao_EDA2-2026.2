import sqlite3
import smtplib
import ssl
import os
from email.message import EmailMessage
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

from ordenacao import quicksort, texto_normalizado

DB = "chamadaunb.db"

SEMESTRE_INICIO = date(2026, 8, 10)
SEMESTRE_FIM = date(2026, 12, 14)

FREQUENCIA_MINIMA = 75.0
LIMITE_ALERTA = 80.0

SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", ""),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "user": os.getenv("SMTP_USER", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "sender": os.getenv("SMTP_SENDER", os.getenv("SMTP_USER", "")),
}

FAKE_STUDENTS = [
    ("202612301", "Ana Beatriz Almeida", "ana.beatriz@example.com"),
    ("202612302", "Bruno Henrique Costa", "bruno.costa@example.com"),
    ("202612303", "Camila Rodrigues Lima", "camila.lima@example.com"),
    ("202612304", "Daniel Oliveira Santos", "daniel.santos@example.com"),
    ("202612305", "Eduarda Martins Silva", "eduarda.silva@example.com"),
    ("202612306", "Felipe Augusto Rocha", "felipe.rocha@example.com"),
    ("202612307", "Gabriela Ferreira Souza", "gabriela.souza@example.com"),
    ("202612308", "Henrique Mendes Alves", "henrique.alves@example.com"),
    ("202612309", "Isabela Castro Nunes", "isabela.nunes@example.com"),
    ("202612310", "João Pedro Moreira", "joao.moreira@example.com"),
    ("202612311", "Fernanda Vaz", "fern4ndavaz@gmail.com"),
]

def db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            aula_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Presente','Falta')),
            UNIQUE(student_id, aula_date),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)
    conn.commit()
    return conn

def seed_students():
    conn = db()
    for matricula, nome, email in FAKE_STUDENTS:
        conn.execute(
            "INSERT OR IGNORE INTO students (matricula,nome,email) VALUES (?,?,?)",
            (matricula, nome, email)
        )
    conn.commit()
    conn.close()

def is_class_day(d):
    return SEMESTRE_INICIO <= d <= SEMESTRE_FIM and d.weekday() < 5

def class_days_until(target=None):
    target = target or date.today()
    end = min(target, SEMESTRE_FIM)
    if end < SEMESTRE_INICIO:
        return []
    days = []
    d = SEMESTRE_INICIO
    while d <= end:
        if is_class_day(d):
            days.append(d)
        d += timedelta(days=1)
    return days

def get_stats(student_id):
    conn = db()
    total, faltas = conn.execute("""
        SELECT COUNT(*),
               COALESCE(SUM(CASE WHEN status='Falta' THEN 1 ELSE 0 END),0)
        FROM attendance
        WHERE student_id=?
    """, (student_id,)).fetchone()
    conn.close()
    total = total or 0
    faltas = faltas or 0
    presencas = total - faltas
    freq = (presencas / total * 100) if total else 100.0
    return total, presencas, faltas, freq

def send_email(student, freq, faltas):
    if not all([SMTP_CONFIG["host"], SMTP_CONFIG["user"],
                SMTP_CONFIG["password"], SMTP_CONFIG["sender"]]):
        return False, "SMTP não configurado. Use 'Configurar e-mail'."

    student_name = student[2]
    student_email = student[3]

    msg = EmailMessage()
    msg["Subject"] = "Alerta de frequência - Sistema de Chamada"
    msg["From"] = SMTP_CONFIG["sender"]
    msg["To"] = student_email
    msg.set_content(
        f"""Olá, {student_name}.

Este é um alerta automático do Sistema de Chamada.

Sua frequência atual é de {freq:.1f}% e você possui {faltas} falta(s).

Atenção: a frequência mínima considerada neste protótipo é de {FREQUENCIA_MINIMA:.0f}%.
Procure acompanhar sua frequência para evitar reprovação por falta.

Mensagem automática para fins acadêmicos/demonstração.
"""
    )
    try:
        context = ssl.create_default_context()
        if SMTP_CONFIG["port"] == 465:
            with smtplib.SMTP_SSL(SMTP_CONFIG["host"], SMTP_CONFIG["port"], context=context) as server:
                server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"], timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
                server.send_message(msg)
        return True, f"E-mail enviado para {student_email}."
    except smtplib.SMTPAuthenticationError:
        return False, "Erro de autenticação. No Gmail, use uma senha de aplicativo, não a senha normal da conta."
    except smtplib.SMTPRecipientsRefused:
        return False, f"O servidor recusou o destinatário: {student_email}."
    except TimeoutError:
        return False, "Tempo esgotado ao conectar no servidor SMTP. Confira servidor, porta e internet."
    except Exception as e:
        return False, f"Erro ao enviar: {e}"

def situacao_aluno(freq):
    if freq < FREQUENCIA_MINIMA:
        return "REPROVADO"
    if freq <= LIMITE_ALERTA:
        return "⚠ ALERTA"
    return "OK"

RANK_SITUACAO = {"REPROVADO": 0, "⚠ ALERTA": 1, "OK": 2}

CHAVES_ORDENACAO = {
    "matricula": lambda r: (r["matricula"], texto_normalizado(r["nome"])),
    "nome":      lambda r: (texto_normalizado(r["nome"]), r["matricula"]),
    "email":     lambda r: (texto_normalizado(r["email"]), texto_normalizado(r["nome"])),
    "faltas":    lambda r: (r["faltas"], texto_normalizado(r["nome"])),
    "freq":      lambda r: (r["freq"], texto_normalizado(r["nome"])),
    "situacao":  lambda r: (RANK_SITUACAO[r["situacao"]], texto_normalizado(r["nome"])),
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Chamada Inteligente - UnB")
        self.geometry("1080x700")
        self.minsize(950, 600)
        self.configure(bg="#edf2f7")

        self.conn = db()
        seed_students()

        self.selected_student = None
        self.students = []
        self.sort_col = "nome"
        self.sort_desc = False
        self.refreshing_ui = False
        self.colors = {
            "bg": "#edf2f7",
            "surface": "#ffffff",
            "surface_alt": "#f8fafc",
            "border": "#d8e0e8",
            "primary": "#0f5f6f",
            "primary_dark": "#0b4250",
            "text": "#172033",
            "muted": "#65758b",
            "ok": "#047857",
            "alert": "#b45309",
            "danger": "#b91c1c",
        }
        self.configure_styles()
        self.build_header()
        self.build_main()
        self.refresh_students()
        self.refresh_dates()
        self.update_dashboard()

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7),
            background="#e7eef6",
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            focusthickness=0,
        )
        style.map("TButton", background=[("active", "#d6e4f0"), ("pressed", "#c7d9e8")])
        style.configure(
            "Accent.TButton",
            background=self.colors["primary"],
            foreground="white",
            bordercolor=self.colors["primary"],
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.colors["primary_dark"]), ("pressed", self.colors["primary_dark"])],
            foreground=[("active", "white"), ("pressed", "white")],
        )
        style.configure(
            "Treeview",
            font=("Segoe UI", 9),
            rowheight=28,
            background="white",
            fieldbackground="white",
            bordercolor=self.colors["border"],
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#e8f0f5",
            foreground=self.colors["primary_dark"],
            padding=(6, 7),
        )
        style.map("Treeview", background=[("selected", "#cce9f0")], foreground=[("selected", self.colors["text"])])
        style.configure("TCombobox", padding=5)

    def build_header(self):
        header = tk.Frame(self, bg=self.colors["primary_dark"], height=96)
        header.pack(fill="x")
        tk.Label(
            header, text="Sistema de Chamada Inteligente",
            font=("Segoe UI", 23, "bold"), fg="white", bg=self.colors["primary_dark"]
        ).pack(anchor="w", padx=28, pady=(16, 0))
        tk.Label(
            header,
            text="UnB • 2026.2 • 10/08/2026 a 14/12/2026 • dados fictícios",
            font=("Segoe UI", 10), fg="#dbeafe", bg=self.colors["primary_dark"]
        ).pack(anchor="w", padx=30, pady=(4, 12))

    def build_main(self):
        root = tk.Frame(self, bg=self.colors["bg"])
        root.pack(fill="both", expand=True, padx=20, pady=16)

        left = tk.Frame(root, bg=self.colors["surface"], bd=1, relief="solid")
        left.pack(side="left", fill="both", padx=(0, 12))
        tk.Label(left, text="Alunos", font=("Segoe UI", 13, "bold"),
                 bg=self.colors["surface"], fg=self.colors["primary_dark"]).pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(left, text="Busque por nome, matrícula ou e-mail",
                 font=("Segoe UI", 9), bg=self.colors["surface"],
                 fg=self.colors["muted"]).pack(anchor="w", padx=14, pady=(0, 10))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(left, textvariable=self.search_var, width=34)
        search_entry.pack(fill="x", padx=12, pady=(0, 10))
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_students())

        student_frame = tk.Frame(left, bg=self.colors["surface"])
        student_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.student_tree = ttk.Treeview(
            student_frame,
            columns=("matricula", "nome"),
            show="headings",
            height=18,
            selectmode="browse",
        )
        self.student_tree.heading("matricula", text="Matrícula")
        self.student_tree.heading("nome", text="Aluno")
        self.student_tree.column("matricula", width=92, anchor="center", stretch=False)
        self.student_tree.column("nome", width=195, anchor="w")
        student_scroll = ttk.Scrollbar(student_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=student_scroll.set)
        self.student_tree.pack(side="left", fill="both", expand=True)
        student_scroll.pack(side="right", fill="y")
        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)

        center = tk.Frame(root, bg=self.colors["surface"], bd=1, relief="solid")
        center.pack(side="left", fill="both", expand=True)
        center.columnconfigure(0, weight=1)
        center.rowconfigure(3, weight=1)

        top = tk.Frame(center, bg=self.colors["surface"])
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))

        tk.Label(top, text="Data da aula:", bg=self.colors["surface"], fg=self.colors["text"],
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(top, textvariable=self.date_var,
                                       width=18, state="readonly")
        self.date_combo.pack(side="left", padx=8)
        self.date_combo.bind("<<ComboboxSelected>>", lambda e: self.update_dashboard())

        self.status_var = tk.StringVar(value="Selecione um aluno.")
        tk.Label(top, textvariable=self.status_var, bg=self.colors["surface"],
                 fg=self.colors["muted"], font=("Segoe UI", 10)).pack(side="left", padx=15)

        actions = tk.Frame(center, bg=self.colors["surface"])
        actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))

        ttk.Button(actions, text="✓ Marcar Presença",
                   style="Accent.TButton",
                   command=lambda: self.mark("Presente")).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="✕ Marcar Falta",
                   command=lambda: self.mark("Falta")).pack(side="left", padx=8)
        ttk.Button(actions, text="🔄 Atualizar",
                   command=self.update_dashboard).pack(side="left", padx=8)
        ttk.Button(actions, text="✉ Configurar e-mail",
                   command=self.email_config).pack(side="right")

        stats = tk.Frame(center, bg=self.colors["surface_alt"], bd=1, relief="solid")
        stats.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))

        self.lbl_freq = self.stat_card(stats, "FREQUÊNCIA", "100%")
        self.lbl_faltas = self.stat_card(stats, "FALTAS", "0")
        self.lbl_pres = self.stat_card(stats, "PRESENÇAS", "0")
        self.lbl_alert = self.stat_card(stats, "SITUAÇÃO", "OK")

        table_frame = tk.Frame(center, bg=self.colors["surface"])
        table_frame.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 10))

        columns = ("matricula", "nome", "email", "faltas", "freq", "situacao")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "matricula": "Matrícula", "nome": "Nome", "email": "E-mail",
            "faltas": "Faltas", "freq": "Freq.", "situacao": "Situação"
        }
        widths = {"matricula":95, "nome":190, "email":230, "faltas":65, "freq":70, "situacao":110}
        self.headings = headings
        for c in columns:
            self.tree.heading(c, text=headings[c],
                              command=lambda col=c: self.sort_by(col))
            self.tree.column(c, width=widths[c], anchor="center" if c != "nome" else "w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_table_select)

        bottom = tk.Frame(center, bg=self.colors["surface"])
        bottom.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 16))
        bottom.columnconfigure(2, weight=1)
        ttk.Button(bottom, text="Enviar alerta do aluno selecionado",
                   command=self.send_selected_alert).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Button(bottom, text="Popular demonstração de faltas",
                   command=self.demo_absences).grid(row=0, column=1, sticky="w")

        self.lbl_info = tk.Label(
            bottom,
            text="Regra: alerta <= 80%; reprovação por frequência < 75%.",
            bg=self.colors["surface"], fg=self.colors["muted"], font=("Segoe UI", 9)
        )
        self.lbl_info.grid(row=0, column=2, sticky="e", padx=(12, 0))

    def stat_card(self, parent, title, value):
        box = tk.Frame(parent, bg=self.colors["surface_alt"])
        box.pack(side="left", fill="x", expand=True, padx=12, pady=12)
        tk.Label(box, text=title, bg=self.colors["surface_alt"], fg=self.colors["muted"],
                 font=("Segoe UI", 8, "bold")).pack()
        label = tk.Label(box, text=value, bg=self.colors["surface_alt"], fg=self.colors["primary_dark"],
                         font=("Segoe UI", 17, "bold"))
        label.pack()
        return label

    def refresh_dates(self):
        dates = class_days_until(SEMESTRE_FIM)
        values = [d.strftime("%d/%m/%Y") for d in dates]
        self.date_combo["values"] = values
        today = date.today()
        chosen = today if is_class_day(today) else SEMESTRE_INICIO
        if chosen < SEMESTRE_INICIO:
            chosen = SEMESTRE_INICIO
        if chosen > SEMESTRE_FIM:
            chosen = SEMESTRE_FIM
        self.date_var.set(chosen.strftime("%d/%m/%Y"))

    def load_students(self):
        rows = self.conn.execute(
            "SELECT id, matricula, nome, email FROM students"
        ).fetchall()
        registros = []
        for student_id, matricula, nome, email in rows:
            total, pres, faltas, freq = get_stats(student_id)
            registros.append({
                "id": student_id, "matricula": matricula, "nome": nome,
                "email": email, "faltas": faltas, "freq": freq,
                "situacao": situacao_aluno(freq),
            })
        self.students = quicksort(
            registros, key=CHAVES_ORDENACAO[self.sort_col], reverse=self.sort_desc
        )

    def sort_by(self, col):
        if col == self.sort_col:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_col = col
            self.sort_desc = False
        self.refresh_students()

    def update_headings(self):
        seta = " ▼" if self.sort_desc else " ▲"
        for c, texto in self.headings.items():
            self.tree.heading(c, text=texto + (seta if c == self.sort_col else ""))

    def refresh_students(self):
        self.refreshing_ui = True
        self.load_students()
        self.student_tree.delete(*self.student_tree.get_children())
        self.tree.delete(*self.tree.get_children())
        selected_id = self.selected_student[0] if self.selected_student else None
        termo = texto_normalizado(self.search_var.get().strip()) if hasattr(self, "search_var") else ""
        for r in self.students:
            dados_busca = texto_normalizado(f"{r['matricula']} {r['nome']} {r['email']}")
            student_iid = f"student-{r['id']}"
            table_iid = f"table-{r['id']}"
            if not termo or termo in dados_busca:
                self.student_tree.insert("", "end", iid=student_iid, values=(r["matricula"], r["nome"]))
                if r["id"] == selected_id:
                    self.student_tree.selection_set(student_iid)
                    self.student_tree.see(student_iid)
            self.tree.insert("", "end", iid=table_iid, values=(
                r["matricula"], r["nome"], r["email"],
                r["faltas"], f"{r['freq']:.1f}%", r["situacao"]
            ))
            if r["id"] == selected_id:
                self.tree.selection_set(table_iid)
                self.tree.see(table_iid)
        self.update_headings()
        self.refreshing_ui = False

    def on_student_select(self, event=None):
        if self.refreshing_ui:
            return
        sel = self.student_tree.selection()
        if not sel:
            return
        student_id = int(sel[0].split("-", 1)[1])
        self.select_student_by_id(student_id)

    def on_table_select(self, event=None):
        if self.refreshing_ui:
            return
        sel = self.tree.selection()
        if not sel:
            return
        student_id = int(sel[0].split("-", 1)[1])
        self.select_student_by_id(student_id)

    def select_student_by_id(self, student_id):
        for r in self.students:
            if r["id"] == student_id:
                self.selected_student = (r["id"], r["matricula"], r["nome"], r["email"])
                self.update_dashboard()
                return

    def selected_date(self):
        try:
            return datetime.strptime(self.date_var.get(), "%d/%m/%Y").date()
        except ValueError:
            return None

    def mark(self, status):
        if not self.selected_student:
            messagebox.showwarning("Aluno", "Selecione um aluno.")
            return
        d = self.selected_date()
        if not d or not is_class_day(d):
            messagebox.showwarning("Data", "Escolha uma data de aula do semestre 2026.2.")
            return
        sid = self.selected_student[0]
        self.conn.execute("""
            INSERT INTO attendance(student_id,aula_date,status)
            VALUES(?,?,?)
            ON CONFLICT(student_id,aula_date)
            DO UPDATE SET status=excluded.status
        """, (sid, d.isoformat(), status))
        self.conn.commit()
        self.refresh_students()
        self.update_dashboard()

        total, pres, faltas, freq = get_stats(sid)
        if status == "Falta" and freq <= LIMITE_ALERTA:
            ans = messagebox.askyesno(
                "⚠ Alerta de frequência",
                f"{self.selected_student[2]} está com {freq:.1f}% de frequência.\n"
                f"Faltas: {faltas}.\n\nDeseja enviar o alerta por e-mail?"
            )
            if ans:
                ok, msg = send_email(self.selected_student, freq, faltas)
                messagebox.showinfo("E-mail", msg)

    def update_dashboard(self):
        if not self.selected_student:
            self.status_var.set("Selecione um aluno.")
            return
        sid = self.selected_student[0]
        total, pres, faltas, freq = get_stats(sid)
        self.lbl_freq.config(text=f"{freq:.1f}%")
        self.lbl_faltas.config(text=str(faltas))
        self.lbl_pres.config(text=str(pres))
        situacao = situacao_aluno(freq)
        alert_color = self.colors["ok"]
        if situacao == "REPROVADO":
            alert_color = self.colors["danger"]
        elif situacao == "⚠ ALERTA":
            alert_color = self.colors["alert"]
        self.lbl_alert.config(text=situacao, fg=alert_color)
        self.status_var.set(
            f"{self.selected_student[2]} • {total} aulas registradas"
        )

    def send_selected_alert(self):
        if not self.selected_student:
            messagebox.showwarning("Aluno", "Selecione um aluno.")
            return
        total, pres, faltas, freq = get_stats(self.selected_student[0])
        if freq > LIMITE_ALERTA:
            ans = messagebox.askyesno(
                "Enviar mesmo assim?",
                f"A frequência atual é {freq:.1f}%. "
                "O aluno ainda não entrou na faixa de alerta.\n\nDeseja enviar o e-mail mesmo assim?"
            )
            if not ans:
                return
        ok, msg = send_email(self.selected_student, freq, faltas)
        messagebox.showinfo("E-mail", msg)

    def demo_absences(self):
        days = class_days_until(date.today())
        if len(days) < 5:
            messagebox.showwarning("Demonstração", "Ainda há poucas datas de aula.")
            return
        rows = self.conn.execute("SELECT id FROM students ORDER BY nome").fetchall()
        for index, (sid,) in enumerate(rows[:2]):
            selected_days = days[-10:]
            for i, d in enumerate(selected_days):
                status = "Falta" if (i < (7 if index == 0 else 3)) else "Presente"
                self.conn.execute("""
                    INSERT INTO attendance(student_id,aula_date,status)
                    VALUES(?,?,?)
                    ON CONFLICT(student_id,aula_date)
                    DO UPDATE SET status=excluded.status
                """, (sid, d.isoformat(), status))
        self.conn.commit()
        self.refresh_students()
        self.update_dashboard()
        messagebox.showinfo(
            "Demonstração",
            "Foram inseridos registros fictícios de presença/falta nos primeiros alunos."
        )

    def email_config(self):
        win = tk.Toplevel(self)
        win.title("Configuração SMTP")
        win.geometry("520x420")
        win.configure(bg=self.colors["surface"])
        win.transient(self)

        fields = [
            ("Servidor SMTP", "host"),
            ("Porta", "port"),
            ("Usuário / e-mail", "user"),
            ("Senha", "password"),
            ("Remetente", "sender"),
        ]
        vars_ = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(
                win,
                text=label,
                bg=self.colors["surface"],
                fg=self.colors["text"],
                font=("Segoe UI", 10, "bold"),
            ).grid(row=i, column=0, padx=18, pady=10, sticky="w")
            var = tk.StringVar(value=str(SMTP_CONFIG[key]))
            vars_[key] = var
            entry = tk.Entry(win, textvariable=var, width=40,
                             show="*" if key == "password" else "")
            entry.grid(row=i, column=1, padx=18, pady=10)

        tk.Label(
            win,
            text="Para Gmail: use smtp.gmail.com, porta 587 e uma senha de aplicativo.\n"
                 "Também é possível iniciar o app com SMTP_HOST, SMTP_PORT,\n"
                 "SMTP_USER, SMTP_PASSWORD e SMTP_SENDER configurados no ambiente.",
            bg=self.colors["surface"],
            fg=self.colors["muted"],
            justify="left",
        ).grid(row=5, column=0, columnspan=2, padx=18, pady=8, sticky="w")

        def use_gmail():
            vars_["host"].set("smtp.gmail.com")
            vars_["port"].set("587")
            if vars_["user"].get().strip() and not vars_["sender"].get().strip():
                vars_["sender"].set(vars_["user"].get().strip())

        def save():
            try:
                SMTP_CONFIG["host"] = vars_["host"].get().strip()
                SMTP_CONFIG["port"] = int(vars_["port"].get())
                SMTP_CONFIG["user"] = vars_["user"].get().strip()
                SMTP_CONFIG["password"] = vars_["password"].get().replace(" ", "")
                SMTP_CONFIG["sender"] = vars_["sender"].get().strip() or SMTP_CONFIG["user"]
                messagebox.showinfo("Configuração", "Configuração SMTP carregada nesta execução.")
                win.destroy()
            except ValueError:
                messagebox.showerror("Erro", "A porta precisa ser um número.")

        buttons = tk.Frame(win, bg=self.colors["surface"])
        buttons.grid(row=6, column=0, columnspan=2, pady=18)
        ttk.Button(buttons, text="Usar Gmail", command=use_gmail).pack(side="left", padx=6)
        ttk.Button(buttons, text="Salvar", style="Accent.TButton", command=save).pack(side="left", padx=6)

if __name__ == "__main__":
    seed_students()
    app = App()
    app.mainloop()
