from __future__ import annotations

import html
import random
from dataclasses import dataclass
from typing import Iterable, Optional

import requests

# Category mappings for Open Trivia DB
TOPIC_CATEGORIES = {
    "Cinemática": 17,
    "Dinâmica": 17,
    "Trabalho e Energia": 17,
    "Termologia": 17,
    "Ondas": 17,
    "Óptica": 17,
    "Eletrostática": 17,
    "Eletrodinâmica": 17,
    "Magnetismo": 17,
    "Física Moderna": 17,
    "Gravitação": 17,
    "Fluidos": 17,
}

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
    {
        "question": "A aceleração da gravidade na superfície da Terra é aproximadamente:",
        "correct_answer": "9,8 m/s²",
        "incorrect_answers": ["6,8 m/s²", "11,8 m/s²", "8,8 m/s²"],
    },
    {
        "question": "Qual é a fórmula da velocidade média?",
        "correct_answer": "Δs / Δt",
        "incorrect_answers": ["m × v", "a × t", "F / m"],
    },
    {
        "question": "O que é energia cinética?",
        "correct_answer": "A energia associada ao movimento",
        "incorrect_answers": ["A energia armazenada em uma mola", "A energia térmica", "A energia potencial"],
    },
    {
        "question": "Qual é a velocidade da luz no vácuo?",
        "correct_answer": "3 × 10⁸ m/s",
        "incorrect_answers": ["3 × 10⁶ m/s", "3 × 10¹⁰ m/s", "3 × 10⁷ m/s"],
    },
    {
        "question": "Em qual situação a resultante de forças é zero?",
        "correct_answer": "Quando o corpo está em repouso ou em movimento uniforme",
        "incorrect_answers": ["Sempre que há movimento", "Quando há apenas uma força", "Quando a velocidade é máxima"],
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
    topic: str = "Cinemática",
    rng: Optional[random.Random] = None,
    timeout: int = 6,
) -> tuple[list[Question], str]:
    """
    Fetch questions from Open Trivia DB with fallback to local questions.
    
    Args:
        amount: Number of questions to fetch
        category: Category ID (default 17 for Science)
        lang: Language code (default "pt" for Portuguese)
        topic: Topic name for better category mapping
        rng: Random number generator instance
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (questions list, source type: "online" or "offline")
    """
    sorteador = rng or random.Random()
    
    # Get category based on topic
    category = TOPIC_CATEGORIES.get(topic, 17)
    
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
    except (requests.RequestException, ValueError, KeyError) as e:
        pass

    # Use fallback questions if online fetch fails
    fallback = [_build_question(item, sorteador) for item in FALLBACK_QUESTIONS]
    return fallback[:amount], "offline"


def avaliar_resposta(question: Question, resposta: str) -> tuple[bool, str]:
    """
    Evaluate if the answer is correct and provide feedback.
    
    Args:
        question: The Question object
        resposta: The user's answer
    
    Returns:
        Tuple of (is_correct: bool, feedback: str)
    """
    correto = resposta == question.correct
    if correto:
        return True, "✅ Correto! Parabéns!"
    
    feedback = f"❌ Incorreto.\n\n"
    feedback += f"Sua resposta: {resposta}\n"
    feedback += f"Resposta correta: {question.correct}\n\n"
    feedback += "Dica: Revise o conceito e tente novamente na próxima questão."
    
    return False, feedback


def formatar_gabarito(questions: Iterable[Question]) -> str:
    linhas = ["GABARITO:\n"]
    for index, question in enumerate(questions, start=1):
        linhas.append(f"{index}. {question.correct}\n")
    return "".join(linhas)
