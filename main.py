import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import ttk, messagebox

from questions import avaliar_resposta, fetch_questions, formatar_gabarito
from roadmap import gerar_texto_roadmap
from study_plan import (
    DayPlan,
    carregar_progresso,
    calcular_blocos_por_hora,
    esta_concluido,
    formatar_plano,
    gerar_plano_diario,
    marcar_concluido,
    salvar_progresso,
)
from web.db import get_or_create_default_user, get_stats, init_db


class OINERoadmapApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OINE AI Roadmap")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f2f2f2")

        titulo = tk.Label(
            root,
            text="OINE AI Roadmap",
            font=("Arial", 24, "bold"),
            bg="#f2f2f2",
        )
        titulo.pack(pady=10)

        subtitulo = tk.Label(
            root,
            text="Gerador Inteligente de Trilhas de Estudo para Física",
            font=("Arial", 12),
            bg="#f2f2f2",
        )
        subtitulo.pack(pady=5)

        frame = tk.Frame(root, bg="white", padx=20, pady=20)
        frame.pack(fill="x", padx=20, pady=10)

        tk.Label(frame, text="Nome do aluno:", bg="white").grid(
            row=0, column=0, sticky="w"
        )
        self.nome_entry = tk.Entry(frame, width=40)
        self.nome_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Nível:", bg="white").grid(
            row=1, column=0, sticky="w"
        )
        self.nivel_combo = ttk.Combobox(
            frame, values=["iniciante", "intermediário", "avançado"], state="readonly"
        )
        self.nivel_combo.current(0)
        self.nivel_combo.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Horas por dia:", bg="white").grid(
            row=2, column=0, sticky="w"
        )
        self.horas_entry = tk.Entry(frame)
        self.horas_entry.insert(0, "2")
        self.horas_entry.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="Objetivo:", bg="white").grid(
            row=3, column=0, sticky="w"
        )
        self.objetivo_entry = tk.Entry(frame, width=40)
        self.objetivo_entry.insert(0, "Preparação para OINE")
        self.objetivo_entry.grid(row=3, column=1, pady=5)

        gerar_btn = tk.Button(
            frame,
            text="Gerar Roadmap com IA",
            command=self.gerar_roadmap,
            bg="black",
            fg="white",
            padx=15,
            pady=10,
        )
        gerar_btn.grid(row=4, column=0, columnspan=2, pady=20)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_roadmap = tk.Frame(self.notebook, bg="#f2f2f2")
        self.tab_quiz = tk.Frame(self.notebook, bg="#f2f2f2")
        self.tab_daily = tk.Frame(self.notebook, bg="#f2f2f2")
        self.notebook.add(self.tab_roadmap, text="Roadmap")
        self.notebook.add(self.tab_quiz, text="Quiz OINE")
        self.notebook.add(self.tab_daily, text="Trilha diária")

        output_frame = tk.Frame(self.tab_roadmap, bg="#f2f2f2")
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output = tk.Text(output_frame, wrap="word", font=("Arial", 11))
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(output_frame, command=self.output.yview)
        scrollbar.pack(side="right", fill="y")
        self.output.config(yscrollcommand=scrollbar.set)

        self._build_quiz_tab()
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.answered_current = False
        self.current_source = "-"
        self.quiz_finished = False

        self.progress_path = Path("progress.json")
        self.progress = carregar_progresso(self.progress_path)
        self.daily_plans = []
        self.selected_day_index = None

        self.db_path = Path("web") / "app.sqlite3"
        init_db(self.db_path)
        self.user_id = get_or_create_default_user(self.db_path)
        self.stats_var = tk.StringVar(value="XP: 0 | Streak: 0 dias")

        self._build_daily_tab()
        self._carregar_trilha_diaria()

    def gerar_roadmap(self) -> None:
        nome = self.nome_entry.get()
        nivel = self.nivel_combo.get()
        horas = self.horas_entry.get()
        objetivo = self.objetivo_entry.get()

        if not nome.strip():
            messagebox.showwarning("Erro", "Digite o nome do aluno")
            return

        try:
            texto = gerar_texto_roadmap(
                nome=nome,
                nivel=nivel,
                horas=horas,
                objetivo=objetivo,
            )
        except ValueError as exc:
            messagebox.showwarning("Erro", str(exc))
            return

        self.output.delete(1.0, tk.END)
        self.output.insert(tk.END, texto)

    def _build_quiz_tab(self) -> None:
        control_frame = tk.Frame(self.tab_quiz, bg="#f2f2f2")
        control_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(control_frame, text="Quantidade de perguntas:", bg="#f2f2f2").grid(
            row=0, column=0, sticky="w"
        )
        self.amount_spin = tk.Spinbox(control_frame, from_=3, to=10, width=5)
        self.amount_spin.delete(0, tk.END)
        self.amount_spin.insert(0, "5")
        self.amount_spin.grid(row=0, column=1, padx=5, sticky="w")

        tk.Button(
            control_frame,
            text="Buscar perguntas online",
            command=self.carregar_perguntas,
            bg="black",
            fg="white",
        ).grid(row=0, column=2, padx=10)

        self.source_var = tk.StringVar(value="Fonte: -")
        tk.Label(control_frame, textvariable=self.source_var, bg="#f2f2f2").grid(
            row=0, column=3, sticky="w"
        )

        self.question_var = tk.StringVar(
            value="Clique em 'Buscar perguntas online' para começar."
        )
        tk.Label(
            self.tab_quiz,
            textvariable=self.question_var,
            bg="#f2f2f2",
            wraplength=900,
            justify="left",
            font=("Arial", 12, "bold"),
        ).pack(fill="x", padx=10, pady=(10, 5))

        self.selected_option = tk.StringVar(value="")
        self.option_buttons = []
        for _ in range(4):
            radio = tk.Radiobutton(
                self.tab_quiz,
                text="",
                variable=self.selected_option,
                value="",
                bg="#f2f2f2",
                anchor="w",
                justify="left",
                wraplength=880,
            )
            radio.pack(fill="x", padx=20, pady=2)
            self.option_buttons.append(radio)

        action_frame = tk.Frame(self.tab_quiz, bg="#f2f2f2")
        action_frame.pack(fill="x", padx=10, pady=10)

        tk.Button(
            action_frame,
            text="Responder",
            command=self.responder_quiz,
            bg="#1f6aa5",
            fg="white",
            padx=10,
        ).pack(side="left", padx=5)

        tk.Button(
            action_frame,
            text="Próxima",
            command=self.proxima_pergunta,
            bg="#444",
            fg="white",
            padx=10,
        ).pack(side="left", padx=5)

        self.feedback_var = tk.StringVar(value="")
        tk.Label(
            self.tab_quiz,
            textvariable=self.feedback_var,
            bg="#f2f2f2",
            font=("Arial", 11),
        ).pack(fill="x", padx=10)

        self.score_var = tk.StringVar(value="Pontuação: 0/0")
        tk.Label(
            self.tab_quiz,
            textvariable=self.score_var,
            bg="#f2f2f2",
            font=("Arial", 11, "bold"),
        ).pack(fill="x", padx=10, pady=(4, 10))

        self.quiz_log = tk.Text(self.tab_quiz, height=8, wrap="word")
        self.quiz_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_daily_tab(self) -> None:
        header_frame = tk.Frame(self.tab_daily, bg="#f2f2f2")
        header_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            header_frame,
            text="Trilha diária estilo Duolingo (Física ENEM)",
            bg="#f2f2f2",
            font=("Arial", 12, "bold"),
        ).pack(side="left")

        tk.Button(
            header_frame,
            text="Atualizar trilha",
            command=self._carregar_trilha_diaria,
            bg="#1f6aa5",
            fg="white",
        ).pack(side="right")

        content_frame = tk.Frame(self.tab_daily, bg="#f2f2f2")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.daily_left = tk.Frame(content_frame, bg="#f2f2f2")
        self.daily_left.pack(side="left", fill="y", padx=(0, 10))

        self.daily_right = tk.Frame(content_frame, bg="#f2f2f2")
        self.daily_right.pack(side="right", fill="both", expand=True)

        self.daily_summary_var = tk.StringVar(value="")
        tk.Label(
            self.daily_left,
            textvariable=self.daily_summary_var,
            bg="#f2f2f2",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        tk.Label(
            self.daily_left,
            textvariable=self.stats_var,
            bg="#f2f2f2",
            font=("Arial", 10),
        ).pack(anchor="w", pady=(0, 10))

        self.daily_buttons_frame = tk.Frame(self.daily_left, bg="#f2f2f2")
        self.daily_buttons_frame.pack(fill="y", expand=False)

        self.daily_day_var = tk.StringVar(value="Selecione um dia")
        tk.Label(
            self.daily_right,
            textvariable=self.daily_day_var,
            bg="#f2f2f2",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w")

        self.daily_text = tk.Text(self.daily_right, wrap="word", font=("Arial", 11))
        self.daily_text.pack(fill="both", expand=True, pady=10)

        actions_frame = tk.Frame(self.daily_right, bg="#f2f2f2")
        actions_frame.pack(fill="x")

        tk.Button(
            actions_frame,
            text="Marcar dia concluído",
            command=self._marcar_dia_concluido,
            bg="#2f7d32",
            fg="white",
        ).pack(side="left", padx=5)

        tk.Button(
            actions_frame,
            text="Abrir quiz do dia",
            command=self._abrir_quiz_dia,
            bg="#444",
            fg="white",
        ).pack(side="left", padx=5)

    def _carregar_trilha_diaria(self) -> None:
        horas = self._parse_horas()
        if horas is None:
            return

        self.daily_plans = gerar_plano_diario(dias=7, horas=horas, inicio=date.today())
        self._render_daily_buttons()
        self._update_daily_summary()

        if self.daily_plans:
            self._selecionar_dia(0)

    def _render_daily_buttons(self) -> None:
        for widget in self.daily_buttons_frame.winfo_children():
            widget.destroy()

        for index, plan in enumerate(self.daily_plans):
            concluido = esta_concluido(self.progress, plan.day)
            bolinha = "●" if concluido else "○"
            texto = f"{bolinha} {plan.day.strftime('%d/%m')}"
            button = tk.Button(
                self.daily_buttons_frame,
                text=texto,
                width=10,
                command=lambda idx=index: self._selecionar_dia(idx),
                bg="#e0f2f1" if concluido else "#f0f0f0",
            )
            button.pack(pady=2, anchor="w")

    def _selecionar_dia(self, index: int) -> None:
        if index < 0 or index >= len(self.daily_plans):
            return

        self.selected_day_index = index
        plan = self.daily_plans[index]
        self.daily_day_var.set(
            f"Dia {plan.day.strftime('%d/%m/%Y')} - {plan.topic}"
        )
        self.daily_text.delete(1.0, tk.END)
        self.daily_text.insert(tk.END, formatar_plano(plan))

    def _marcar_dia_concluido(self) -> None:
        if self.selected_day_index is None:
            messagebox.showwarning("Erro", "Selecione um dia da trilha")
            return

        plan = self.daily_plans[self.selected_day_index]
        self.progress = marcar_concluido(self.progress, plan.day)
        salvar_progresso(self.progress_path, self.progress)
        self._render_daily_buttons()
        self._update_daily_summary()

    def _abrir_quiz_dia(self) -> None:
        horas = self._parse_horas()
        if horas is None:
            return

        blocos = calcular_blocos_por_hora(horas)
        amount = max(4, min(10, blocos * 2))
        self.amount_spin.delete(0, tk.END)
        self.amount_spin.insert(0, str(amount))
        self.quiz_log.insert(
            tk.END,
            f"\nQuiz do dia ({amount} questões)\n",
        )
        self.carregar_perguntas()
        self.notebook.select(self.tab_quiz)

    def _update_daily_summary(self) -> None:
        total = len(self.daily_plans)
        concluidos = len(self.progress.completed_dates)
        self.daily_summary_var.set(f"Dias concluídos: {concluidos}/{total}")
        stats = get_stats(self.db_path, self.user_id)
        self.stats_var.set(f"XP: {stats['xp']} | Streak: {stats['streak']} dias")

    def _parse_horas(self) -> float | None:
        raw = self.horas_entry.get().strip().replace(",", ".")
        try:
            horas = float(raw)
        except ValueError:
            messagebox.showwarning("Erro", "Horas por dia inválidas")
            return None
        return max(0.5, horas)

    def carregar_perguntas(self) -> None:
        try:
            amount = int(self.amount_spin.get())
        except ValueError:
            messagebox.showwarning("Erro", "Quantidade inválida")
            return

        self.questions, source = fetch_questions(amount=amount)
        self.current_source = source
        self.source_var.set(f"Fonte: {source}")
        self.current_index = 0
        self.score = 0
        self.quiz_finished = False
        self.quiz_log.delete(1.0, tk.END)
        self.feedback_var.set("")
        self._update_score()
        self._mostrar_pergunta()

        if source == "offline":
            messagebox.showinfo(
                "Aviso",
                "Não foi possível buscar online. Usando perguntas offline.",
            )

    def _mostrar_pergunta(self) -> None:
        self.answered_current = False
        self.selected_option.set("")

        if not self.questions:
            self.question_var.set("Nenhuma pergunta disponível.")
            for radio in self.option_buttons:
                radio.config(text="", value="")
            return

        if self.current_index >= len(self.questions):
            self.question_var.set("Fim do quiz! Confira seu desempenho abaixo.")
            for radio in self.option_buttons:
                radio.config(text="", value="")
            self.feedback_var.set("")
            if not self.quiz_finished:
                self.quiz_log.insert(
                    tk.END, "\n" + formatar_gabarito(self.questions)
                )
                self.quiz_finished = True
            return

        question = self.questions[self.current_index]
        self.question_var.set(f"Pergunta {self.current_index + 1}: {question.prompt}")

        for radio in self.option_buttons:
            radio.config(text="", value="")

        for radio, option in zip(self.option_buttons, question.options, strict=False):
            radio.config(text=option, value=option)

    def responder_quiz(self) -> None:
        if not self.questions or self.current_index >= len(self.questions):
            return

        if self.answered_current:
            return

        resposta = self.selected_option.get()
        if not resposta:
            messagebox.showwarning("Erro", "Selecione uma alternativa")
            return

        question = self.questions[self.current_index]
        correto, feedback = avaliar_resposta(question, resposta)
        self.feedback_var.set(feedback)
        self.quiz_log.insert(
            tk.END,
            f"Q{self.current_index + 1}: {feedback}\n",
        )
        if correto:
            self.score += 1
        self.answered_current = True
        self._update_score()

    def proxima_pergunta(self) -> None:
        if not self.questions:
            return

        if not self.answered_current and self.current_index < len(self.questions):
            messagebox.showwarning("Atenção", "Responda antes de avançar")
            return

        self.current_index += 1
        self.feedback_var.set("")
        self._mostrar_pergunta()

    def _update_score(self) -> None:
        total = len(self.questions)
        self.score_var.set(f"Pontuação: {self.score}/{total}")


if __name__ == "__main__":
    root = tk.Tk()
    app = OINERoadmapApp(root)
    root.mainloop()
