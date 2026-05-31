from __future__ import annotations

import html
import random
from dataclasses import dataclass
from typing import Iterable, Optional

import requests

FALLBACK_QUESTIONS = [
    {
        "question": "Qual é a unidade de medida da força no SI?",
        "correct_answer": "Newton (N)",
        "incorrect_answers": ["Joule (J)", "Watt (W)", "Pascal (Pa)"],
    },
    {
        "question": "Em um movimento retilíneo uniforme, a velocidade é:",
        "correct_answer": "Constante",
        "incorrect_answers": ["Nula", "Crescente", "Variável"],
    },
    {
        "question": "Qual grandeza está associada à resistência elétrica?",
        "correct_answer": "Ohm (Ω)",
        "incorrect_answers": ["Tesla (T)", "Coulomb (C)", "Volt (V)"],
    },
    {
        "question": "A segunda lei de Newton relaciona força com:",
        "correct_answer": "Massa e aceleração",
        "incorrect_answers": ["Massa e velocidade", "Energia e tempo", "Potência e trabalho"],
    },
    {
        "question": "Em ondas sonoras, a frequência define o(a):",
        "correct_answer": "Tom (altura)",
        "incorrect_answers": ["Intensidade", "Timbre", "Velocidade"],
    },
]


@dataclass(frozen=True)
class Question:
    prompt: str
    options: tuple[str, ...]
    correct: str


def _build_question(raw: dict, rng: random.Random) -> Question:
    prompt = html.unescape(raw["question"])
    correct = html.unescape(raw["correct_answer"])
    options = [correct] + [html.unescape(opt) for opt in raw["incorrect_answers"]]
    rng.shuffle(options)
    return Question(prompt=prompt, options=tuple(options), correct=correct)


def _parse_questions(data: dict, rng: random.Random) -> list[Question]:
    results = data.get("results") or []
    return [_build_question(item, rng) for item in results]


def fetch_questions(
    amount: int = 5,
    category: int = 17,
    lang: str = "pt",
    rng: Optional[random.Random] = None,
    timeout: int = 6,
) -> tuple[list[Question], str]:
    sorteador = rng or random.Random()
    url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "category": category,
        "type": "multiple",
        "lang": lang,
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        questions = _parse_questions(payload, sorteador)
        if questions:
            return questions, "online"
    except (requests.RequestException, ValueError, KeyError):
        pass

    fallback = [_build_question(item, sorteador) for item in FALLBACK_QUESTIONS]
    return fallback[:amount], "offline"


def avaliar_resposta(question: Question, resposta: str) -> tuple[bool, str]:
    correto = resposta == question.correct
    if correto:
        return True, "✅ Correto!"
    return False, f"❌ Incorreto. Resposta correta: {question.correct}"


def formatar_gabarito(questions: Iterable[Question]) -> str:
    linhas = ["GABARITO:\n"]
    for index, question in enumerate(questions, start=1):
        linhas.append(f"{index}. {question.correct}\n")
    return "".join(linhas)
