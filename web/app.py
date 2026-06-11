from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
from time import time
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, jsonify, render_template, request

from questions import avaliar_resposta, fetch_questions
from study_plan import (
    carregar_progresso,
    calcular_blocos_por_hora,
    esta_concluido,
    formatar_plano,
    get_topic_content,
    gerar_plano_diario,
    RESOURCES,
    marcar_concluido,
    salvar_progresso,
)
from web.db import (
    add_quiz_attempt,
    get_or_create_default_user,
    get_proficiency,
    get_stats,
    init_db,
    load_settings,
    mark_day_complete,
    update_name,
    update_proficiency,
    upsert_settings,
)

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
PROGRESS_PATH = BASE_DIR / "progress.json"
DB_PATH = BASE_DIR / "app.sqlite3"
CACHE_TTL = 120
_cache: dict[str, tuple[float, dict]] = {}

init_db(DB_PATH)
DEFAULT_USER_ID = get_or_create_default_user(DB_PATH)


def _cache_get(key: str) -> dict | None:
    item = _cache.get(key)
    if not item:
        return None
    ts, payload = item
    if time() - ts > CACHE_TTL:
        _cache.pop(key, None)
        return None
    return payload


def _cache_set(key: str, payload: dict) -> None:
    _cache[key] = (time(), payload)


def _get_user_id() -> int:
    return DEFAULT_USER_ID


def _build_daily_plans(hours: float, days: int, start_day: date | None = None):
    return gerar_plano_diario(dias=days, horas=hours, inicio=start_day or date.today())


def _find_plan_for_date(hours: float, days: int, day: date):
    for plan in _build_daily_plans(hours, days):
        if plan.day == day:
            return plan
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/content")
def content_page():
    return render_template("content.html")


@app.route("/assunto-do-dia")
def subject_page():
    return render_template("assunto-do-dia.html")


@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")


@app.get("/api/profile")
def profile():
    user_id = _get_user_id()
    settings = load_settings(DB_PATH, user_id)
    if not settings:
        return jsonify(
            {"name": "Aluno", "hours": 2, "days": 7, "goal": "ENEM", "language": "pt"}
        )
    return jsonify(
        {
            "name": settings.name,
            "hours": settings.hours_per_day,
            "days": settings.days_planned,
            "goal": settings.goal,
            "language": settings.language,
        }
    )


@app.get("/api/stats")
def stats():
    user_id = _get_user_id()
    return jsonify(get_stats(DB_PATH, user_id))


@app.post("/api/onboarding")
def onboarding():
    payload = request.get_json(force=True)
    name = payload.get("name", "Aluno").strip() or "Aluno"
    hours = float(payload.get("hours", 2))
    days = int(payload.get("days", 7))
    goal = payload.get("goal", "ENEM")
    language = payload.get("language", "pt")

    user_id = _get_user_id()
    update_name(DB_PATH, user_id, name)
    upsert_settings(DB_PATH, user_id, hours, days, goal, language)
    return jsonify({"ok": True})


@app.get("/api/daily-plan")
def daily_plan():
    horas = float(request.args.get("hours", 2))
    dias = int(request.args.get("days", 7))
    cache_key = f"plan:{horas}:{dias}"
    cached = _cache_get(cache_key)
    if cached:
        return jsonify(cached)

    planos = _build_daily_plans(horas, dias)
    progresso = carregar_progresso(PROGRESS_PATH)
    response = []
    for plan in planos:
        response.append(
            {
                "date": plan.day.isoformat(),
                "label": plan.day.strftime("%d/%m"),
                "topic": plan.topic,
                "explanation": plan.explanation,
                "blocks": list(plan.blocks),
                "difficulty": plan.difficulty,
                "resources": list(plan.resources),
                "completed": esta_concluido(progresso, plan.day),
            }
        )
    payload = {
        "days": response,
        "summary": {
            "completed": len(progresso.completed_dates),
            "total": len(planos),
        },
    }
    _cache_set(cache_key, payload)
    return jsonify(payload)


@app.post("/api/complete-day")
def complete_day():
    payload = request.get_json(force=True)
    day_str = payload.get("date")
    if not day_str:
        return jsonify({"error": "date é obrigatório"}), 400

    try:
        day = date.fromisoformat(day_str)
    except ValueError:
        return jsonify({"error": "date inválido"}), 400

    progresso = carregar_progresso(PROGRESS_PATH)
    progresso = marcar_concluido(progresso, day)
    salvar_progresso(PROGRESS_PATH, progresso)

    user_id = _get_user_id()
    xp_gain, streak = mark_day_complete(DB_PATH, user_id, day, xp_gain=15)

    return jsonify(
        {
            "ok": True,
            "completed": list(progresso.completed_dates),
            "xp": xp_gain,
            "streak": streak,
        }
    )


@app.get("/api/quiz")
def quiz():
    hours = float(request.args.get("hours", 2))
    days = int(request.args.get("days", 7))
    topic = request.args.get("topic", "Cinemática")
    day_str = request.args.get("date")
    language = request.args.get("language", "pt")
    user_id = _get_user_id()
    if day_str:
        try:
            day = date.fromisoformat(day_str)
            plan = _find_plan_for_date(hours, days, day)
            if plan:
                topic = plan.topic
        except ValueError:
            pass
    proficiency = get_proficiency(DB_PATH, user_id, topic)
    base = calcular_blocos_por_hora(hours) * 2
    amount = max(4, min(12, int(base * (1.2 - proficiency))))
    questions, source = fetch_questions(amount=amount, lang=language)
    return jsonify(
        {
            "source": source,
            "topic": topic,
            "proficiency": proficiency,
            "language": language,
            "questions": [
                {
                    "prompt": q.prompt,
                    "options": list(q.options),
                    "correct": q.correct,
                }
                for q in questions
            ],
        }
    )


@app.post("/api/answer")
def answer():
    payload = request.get_json(force=True)
    prompt = payload.get("prompt")
    selected = payload.get("selected")
    correct = payload.get("correct")
    topic = payload.get("topic", "Cinemática")
    day_str = payload.get("day")

    if not all([prompt, selected, correct]):
        return jsonify({"error": "dados incompletos"}), 400

    correto, feedback = avaliar_resposta(
        question=type("Q", (), {"correct": correct})(),
        resposta=selected,
    )
    if day_str:
        try:
            day = date.fromisoformat(day_str)
        except ValueError:
            day = date.today()
    else:
        day = date.today()

    user_id = _get_user_id()
    add_quiz_attempt(DB_PATH, user_id, day, int(correto), 1, topic)
    score = get_proficiency(DB_PATH, user_id, topic)
    score = max(0.2, min(0.95, score + (0.05 if correto else -0.03)))
    update_proficiency(DB_PATH, user_id, topic, score)

    return jsonify({"correct": correto, "feedback": feedback, "score": score})


@app.get("/api/day-content")
def day_content():
    day_str = request.args.get("date")
    hours = float(request.args.get("hours", 2))
    days = int(request.args.get("days", 7))

    if not day_str:
        return jsonify({"error": "date é obrigatório"}), 400

    try:
        day = date.fromisoformat(day_str)
    except ValueError:
        return jsonify({"error": "date inválido"}), 400

    plan = _find_plan_for_date(hours, days, day)
    if plan:
        topic_content = get_topic_content(plan.topic)
        return jsonify(
            {
                "content": formatar_plano(plan),
                "topicContent": topic_content,
                "resources": list(RESOURCES.get(plan.base_topic, [])),
                "day": plan.day.isoformat(),
                "topic": plan.topic,
                "baseTopic": plan.base_topic,
            }
        )

    return jsonify({"error": "dia não encontrado"}), 404


if __name__ == "__main__":
    app.run(debug=True)
