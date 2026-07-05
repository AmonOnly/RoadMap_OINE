from __future__ import annotations

import html
import json
import random
import re
from dataclasses import dataclass
from typing import Iterable, Optional

import requests

# Mantido apenas como referência histórica / fallback secundário. O Open Trivia
# DB não garante perguntas em português nem específicas de cada tópico de
# Física (a API não possui parâmetro real de idioma e a categoria 17 é uma
# categoria genérica de "Ciência: Natureza"). Por isso ele agora só é usado
# como segunda tentativa, depois da IA e antes do banco local.
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

# Banco de perguntas local, organizado por tópico-base (o mesmo usado em
# study_plan.TOPIC_ALIASES). Usado como último fallback, garantindo que as
# perguntas sempre estejam em português e relacionadas ao assunto do dia,
# mesmo sem acesso à IA ou à internet.
FALLBACK_QUESTIONS_BY_TOPIC: dict[str, list[dict]] = {
    "Cinemática": [
        {
            "question": "Em um movimento retilíneo uniforme, a velocidade é:",
            "correct_answer": "Constante",
            "incorrect_answers": ["Nula", "Crescente", "Variável"],
        },
        {
            "question": "Qual é a fórmula da velocidade média?",
            "correct_answer": "Δs / Δt",
            "incorrect_answers": ["m × v", "a × t", "F / m"],
        },
        {
            "question": "A aceleração da gravidade na superfície da Terra é aproximadamente:",
            "correct_answer": "9,8 m/s²",
            "incorrect_answers": ["6,8 m/s²", "11,8 m/s²", "8,8 m/s²"],
        },
        {
            "question": "No MRUV, a velocidade varia:",
            "correct_answer": "De forma constante ao longo do tempo",
            "incorrect_answers": [
                "De forma aleatória",
                "Somente no início do movimento",
                "De forma decrescente sempre",
            ],
        },
        {
            "question": "Em um gráfico velocidade x tempo (v x t), a área sob a curva representa:",
            "correct_answer": "O deslocamento",
            "incorrect_answers": ["A aceleração", "A velocidade média", "O tempo total"],
        },
    ],
    "Dinâmica": [
        {
            "question": "Qual é a unidade de medida da força no SI?",
            "correct_answer": "Newton (N)",
            "incorrect_answers": ["Joule (J)", "Watt (W)", "Pascal (Pa)"],
        },
        {
            "question": "A segunda lei de Newton relaciona força com:",
            "correct_answer": "Massa e aceleração",
            "incorrect_answers": ["Massa e velocidade", "Energia e tempo", "Potência e trabalho"],
        },
        {
            "question": "Em qual situação a resultante de forças é zero?",
            "correct_answer": "Quando o corpo está em repouso ou em movimento uniforme",
            "incorrect_answers": [
                "Sempre que há movimento",
                "Quando há apenas uma força",
                "Quando a velocidade é máxima",
            ],
        },
        {
            "question": "A força de atrito estático, em geral, é ___ que a força de atrito cinético.",
            "correct_answer": "maior ou igual",
            "incorrect_answers": ["menor", "igual sempre", "inexistente"],
        },
        {
            "question": "A terceira lei de Newton afirma que:",
            "correct_answer": "toda ação gera uma reação de mesma intensidade e direção oposta",
            "incorrect_answers": [
                "a força é proporcional à massa",
                "a energia sempre se conserva",
                "o corpo tende a permanecer em repouso",
            ],
        },
    ],
    "Energia": [
        {
            "question": "O que é energia cinética?",
            "correct_answer": "A energia associada ao movimento",
            "incorrect_answers": [
                "A energia armazenada em uma mola",
                "A energia térmica",
                "A energia potencial",
            ],
        },
        {
            "question": "A unidade de energia no SI é:",
            "correct_answer": "Joule (J)",
            "incorrect_answers": ["Newton (N)", "Watt (W)", "Pascal (Pa)"],
        },
        {
            "question": "A energia potencial gravitacional depende de:",
            "correct_answer": "massa, gravidade e altura",
            "incorrect_answers": ["apenas da massa", "apenas da velocidade", "apenas do tempo"],
        },
        {
            "question": "Potência é definida como:",
            "correct_answer": "trabalho realizado por unidade de tempo",
            "incorrect_answers": [
                "força aplicada por unidade de área",
                "energia armazenada em um corpo",
                "velocidade de um objeto",
            ],
        },
        {
            "question": "Em um sistema sem atrito, a energia mecânica total:",
            "correct_answer": "se conserva",
            "incorrect_answers": ["aumenta sempre", "diminui sempre", "é sempre nula"],
        },
    ],
    "Termologia": [
        {
            "question": "A unidade de temperatura no Sistema Internacional é:",
            "correct_answer": "Kelvin (K)",
            "incorrect_answers": ["Celsius (°C)", "Fahrenheit (°F)", "Joule (J)"],
        },
        {
            "question": "Calor latente é a energia envolvida em:",
            "correct_answer": "uma mudança de estado físico, sem variação de temperatura",
            "incorrect_answers": [
                "um aumento de temperatura",
                "uma variação de pressão",
                "um deslocamento de massa",
            ],
        },
        {
            "question": "A propagação de calor por radiação ocorre:",
            "correct_answer": "mesmo no vácuo, sem necessidade de meio material",
            "incorrect_answers": ["apenas em sólidos", "apenas em líquidos", "apenas em gases"],
        },
        {
            "question": "0°C corresponde a quantos Kelvin?",
            "correct_answer": "273 K",
            "incorrect_answers": ["0 K", "100 K", "373 K"],
        },
        {
            "question": "A convecção térmica é a transferência de calor por meio de:",
            "correct_answer": "movimento de fluidos",
            "incorrect_answers": [
                "contato direto entre sólidos",
                "ondas eletromagnéticas",
                "radiação",
            ],
        },
    ],
    "Ondulatória": [
        {
            "question": "Em ondas sonoras, a frequência define o(a):",
            "correct_answer": "Tom (altura)",
            "incorrect_answers": ["Intensidade", "Timbre", "Velocidade"],
        },
        {
            "question": "A relação entre velocidade, frequência e comprimento de onda é:",
            "correct_answer": "v = λ × f",
            "incorrect_answers": ["v = λ / f", "v = λ + f", "v = λ − f"],
        },
        {
            "question": "O período de uma onda é o inverso de:",
            "correct_answer": "sua frequência",
            "incorrect_answers": ["sua velocidade", "sua amplitude", "seu comprimento"],
        },
        {
            "question": "O efeito Doppler explica a variação percebida:",
            "correct_answer": "da frequência de uma onda quando há movimento relativo entre fonte e observador",
            "incorrect_answers": [
                "da amplitude sempre que a onda se propaga",
                "do comprimento de onda em repouso",
                "da velocidade da luz no vácuo",
            ],
        },
        {
            "question": "Ondas mecânicas, ao contrário das eletromagnéticas, precisam de:",
            "correct_answer": "um meio material para se propagar",
            "incorrect_answers": ["vácuo para existir", "alta frequência", "alta temperatura"],
        },
    ],
    "Óptica": [
        {
            "question": "Qual é a velocidade da luz no vácuo?",
            "correct_answer": "3 × 10⁸ m/s",
            "incorrect_answers": ["3 × 10⁶ m/s", "3 × 10¹⁰ m/s", "3 × 10⁷ m/s"],
        },
        {
            "question": "Em espelhos planos, a imagem formada é:",
            "correct_answer": "virtual, direita e do mesmo tamanho do objeto",
            "incorrect_answers": ["real e invertida", "real e ampliada", "virtual e invertida"],
        },
        {
            "question": "A refração da luz ocorre quando ela:",
            "correct_answer": "passa de um meio para outro com índice de refração diferente",
            "incorrect_answers": [
                "reflete em uma superfície espelhada",
                "perde toda a sua energia",
                "muda de cor sozinha",
            ],
        },
        {
            "question": "Uma lente convergente também é chamada de lente:",
            "correct_answer": "positiva",
            "incorrect_answers": ["negativa", "plana", "difusora"],
        },
        {
            "question": "A lei de Snell relaciona:",
            "correct_answer": "os ângulos de incidência e refração com os índices de refração dos meios",
            "incorrect_answers": [
                "a intensidade luminosa com a distância",
                "a cor da luz com sua velocidade no vácuo",
                "o tamanho da imagem com o foco do espelho",
            ],
        },
    ],
    "Eletricidade": [
        {
            "question": "Qual grandeza está associada à resistência elétrica?",
            "correct_answer": "Ohm (Ω)",
            "incorrect_answers": ["Tesla (T)", "Coulomb (C)", "Volt (V)"],
        },
        {
            "question": "A Lei de Ohm é expressa por:",
            "correct_answer": "U = R × I",
            "incorrect_answers": ["P = U × I", "U = R + I", "P = R / I"],
        },
        {
            "question": "Em um circuito em série, a corrente elétrica:",
            "correct_answer": "é a mesma em todos os pontos do circuito",
            "incorrect_answers": [
                "se divide entre os resistores",
                "é maior no último resistor",
                "é nula",
            ],
        },
        {
            "question": "A potência elétrica dissipada em um resistor pode ser calculada por:",
            "correct_answer": "P = U × I",
            "incorrect_answers": ["P = U / I", "P = U + I", "P = U − I"],
        },
        {
            "question": "Em um circuito em paralelo, a tensão elétrica:",
            "correct_answer": "é a mesma em todos os ramos",
            "incorrect_answers": ["se divide entre os ramos", "aumenta em cada ramo", "é sempre nula"],
        },
    ],
    "Magnetismo": [
        {
            "question": "As linhas de campo magnético de um ímã, fora dele, saem do polo:",
            "correct_answer": "norte e entram no polo sul",
            "incorrect_answers": [
                "sul e entram no polo norte",
                "norte e nunca se fecham",
                "sul e se dispersam",
            ],
        },
        {
            "question": "A força magnética sobre uma carga em movimento é dada por:",
            "correct_answer": "F = q × v × B × sen(θ)",
            "incorrect_answers": ["F = m × a", "F = q × E", "F = m × v"],
        },
        {
            "question": "Um eletroímã é formado por:",
            "correct_answer": "uma bobina percorrida por corrente elétrica, geralmente enrolada em um núcleo de ferro",
            "incorrect_answers": [
                "dois ímãs permanentes unidos",
                "uma bateria conectada a um resistor",
                "um capacitor carregado",
            ],
        },
        {
            "question": "A unidade de campo magnético no SI é:",
            "correct_answer": "Tesla (T)",
            "incorrect_answers": ["Weber (Wb)", "Henry (H)", "Ohm (Ω)"],
        },
        {
            "question": "Cargas elétricas paradas (em repouso):",
            "correct_answer": "não sofrem força magnética",
            "incorrect_answers": [
                "sempre sofrem força magnética máxima",
                "geram campo magnético intenso",
                "são repelidas por qualquer ímã",
            ],
        },
    ],
}

# Lista "achatada" mantida por compatibilidade com quem importar o nome antigo.
FALLBACK_QUESTIONS = [item for bank in FALLBACK_QUESTIONS_BY_TOPIC.values() for item in bank]

INSTRUCAO_QUIZ = (
    "Você é um professor de Física que cria questões de múltipla escolha no "
    "estilo do ENEM, sempre em português do Brasil."
)


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


def _topic_base(topic: str) -> str:
    """Extrai o tópico-base (ex.: 'Cinemática') de um título de dia como
    'Cinemática: MRU e MRUV'. Faz fallback para correspondência por prefixo."""
    base = topic.split(":")[0].strip()
    if base in FALLBACK_QUESTIONS_BY_TOPIC:
        return base
    for key in FALLBACK_QUESTIONS_BY_TOPIC:
        if topic.startswith(key):
            return key
    return topic


def _local_fallback(topic: str, amount: int, rng: random.Random) -> list[Question]:
    base = _topic_base(topic)
    bank = FALLBACK_QUESTIONS_BY_TOPIC.get(base) or FALLBACK_QUESTIONS
    pool = list(bank)
    rng.shuffle(pool)
    if len(pool) < amount:
        # repete o banco embaralhado até atingir a quantidade pedida
        repeats = (amount // len(pool)) + 1
        pool = pool * repeats
    selected = pool[:amount]
    return [_build_question(item, rng) for item in selected]


def _extract_json_array(text: str) -> Optional[list]:
    """Remove blocos de markdown (```json ... ```) que a IA às vezes adiciona
    e tenta extrair apenas o array JSON da resposta."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        match = re.search(r"\[.*\]", cleaned, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


def _generate_ai_questions(
    ai_client,
    topic: str,
    amount: int,
    rng: random.Random,
) -> Optional[list[Question]]:
    """Gera perguntas de Física específicas do tópico usando o Gemini, sempre
    em português. Retorna None se a IA não estiver disponível ou a resposta
    não puder ser interpretada (o chamador deve usar outro fallback)."""
    if ai_client is None:
        return None

    prompt = (
        f"Crie exatamente {amount} perguntas de múltipla escolha sobre o tema "
        f'"{topic}" (Física, nível ENEM), em português do Brasil. Cada pergunta '
        "deve ter exatamente 4 alternativas, sendo apenas uma correta, e não "
        "pode repetir o enunciado de outra pergunta da lista.\n\n"
        "Responda SOMENTE com um array JSON válido, sem markdown, sem texto "
        "adicional, no formato exato:\n"
        '[{"question": "...", "options": ["...", "...", "...", "..."], '
        '"correct_index": 0}]'
    )

    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"system_instruction": INSTRUCAO_QUIZ},
        )
        data = _extract_json_array(response.text or "")
        if not data:
            return None

        questions: list[Question] = []
        for item in data:
            options = [str(opt) for opt in item.get("options", [])]
            idx = item.get("correct_index")
            if len(options) < 2 or not isinstance(idx, int) or not (0 <= idx < len(options)):
                continue
            correct = options[idx]
            shuffled = list(options)
            rng.shuffle(shuffled)
            questions.append(
                Question(prompt=str(item["question"]), options=tuple(shuffled), correct=correct)
            )

        return questions[:amount] if questions else None
    except Exception:
        # Qualquer falha de rede, parsing ou da API cai para o próximo fallback
        return None


def fetch_questions(
    amount: int = 5,
    category: int = 17,
    lang: str = "pt",
    topic: str = "Cinemática",
    rng: Optional[random.Random] = None,
    timeout: int = 6,
    ai_client=None,
) -> tuple[list[Question], str]:
    """
    Busca perguntas de Física para o quiz, tentando nesta ordem:

    1. IA (Gemini): perguntas geradas na hora, específicas do tópico do dia e
       sempre em português (fonte "ia").
    2. Open Trivia DB: mantido como fallback secundário, mas não garante nem
       o idioma nem o tópico corretos (fonte "online").
    3. Banco local por tópico: sempre em português e relacionado ao assunto
       do dia (fonte "offline").

    Args:
        amount: Número de perguntas desejado
        category: Categoria do Open Trivia DB (fallback secundário)
        lang: Mantido por compatibilidade; o Open Trivia DB não possui suporte
            real a idioma, então isso não afeta mais o resultado
        topic: Nome do tópico do dia (usado pela IA e pelo banco local)
        rng: Gerador de números aleatórios (para testes determinísticos)
        timeout: Tempo limite da chamada ao Open Trivia DB, em segundos

    Returns:
        Tupla (lista de perguntas, fonte: "ia" | "online" | "offline")
    """
    sorteador = rng or random.Random()

    ai_questions = _generate_ai_questions(ai_client, topic, amount, sorteador)
    if ai_questions:
        return ai_questions, "ia"

    category = TOPIC_CATEGORIES.get(topic, category)
    url = "https://opentdb.com/api.php"
    params = {
        "amount": amount,
        "category": category,
        "type": "multiple",
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

    fallback = _local_fallback(topic, amount, sorteador)
    return fallback, "offline"


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

    feedback = "❌ Incorreto.\n\n"
    feedback += f"Sua resposta: {resposta}\n"
    feedback += f"Resposta correta: {question.correct}\n\n"
    feedback += "Dica: Revise o conceito e tente novamente na próxima questão."

    return False, feedback


def formatar_gabarito(questions: Iterable[Question]) -> str:
    linhas = ["GABARITO:\n"]
    for index, question in enumerate(questions, start=1):
        linhas.append(f"{index}. {question.correct}\n")
    return "".join(linhas)
