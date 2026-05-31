from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

BASE_TOPICS = [
    {
        "titulo": "Cinemática",
        "explicacao": "Conceitos de velocidade, aceleração e gráficos no ENEM.",
        "peso": 1.0,
    },
    {
        "titulo": "Dinâmica",
        "explicacao": "Leis de Newton e forças em situações do cotidiano.",
        "peso": 1.1,
    },
    {
        "titulo": "Energia",
        "explicacao": "Trabalho, potência e conservação de energia em problemas.",
        "peso": 1.0,
    },
    {
        "titulo": "Termologia",
        "explicacao": "Calor, temperatura e trocas térmicas em sistemas simples.",
        "peso": 0.9,
    },
    {
        "titulo": "Ondulatória",
        "explicacao": "Ondas, frequência e aplicações em som e luz.",
        "peso": 0.9,
    },
    {
        "titulo": "Óptica",
        "explicacao": "Reflexão, refração e espelhos/lentes no ENEM.",
        "peso": 0.95,
    },
    {
        "titulo": "Eletricidade",
        "explicacao": "Circuitos, Lei de Ohm e consumo de energia elétrica.",
        "peso": 1.2,
    },
    {
        "titulo": "Magnetismo",
        "explicacao": "Campos magnéticos e aplicações tecnológicas.",
        "peso": 0.85,
    },
]

RESOURCES = {
    "Cinemática": [
        {
            "title": "Khan Academy - Cinemática",
            "url": "https://pt.khanacademy.org/science/physics/one-dimensional-motion",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: MRU e MRUV (resumo)",
            "url": "https://www.youtube.com/results?search_query=cinem%C3%A1tica+mru+mruv+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Dinâmica": [
        {
            "title": "Khan Academy - Leis de Newton",
            "url": "https://pt.khanacademy.org/science/physics/forces-newtons-laws",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Leis de Newton ENEM",
            "url": "https://www.youtube.com/results?search_query=leis+de+newton+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Energia": [
        {
            "title": "Khan Academy - Trabalho e energia",
            "url": "https://pt.khanacademy.org/science/physics/work-and-energy",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Energia e potência ENEM",
            "url": "https://www.youtube.com/results?search_query=energia+potencia+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Termologia": [
        {
            "title": "Khan Academy - Calor e temperatura",
            "url": "https://pt.khanacademy.org/science/physics/thermal-physics",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Calorimetria ENEM",
            "url": "https://www.youtube.com/results?search_query=calorimetria+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Ondulatória": [
        {
            "title": "Khan Academy - Ondas e som",
            "url": "https://pt.khanacademy.org/science/physics/mechanical-waves-and-sound",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Ondas ENEM",
            "url": "https://www.youtube.com/results?search_query=ondas+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Óptica": [
        {
            "title": "Khan Academy - Óptica",
            "url": "https://pt.khanacademy.org/science/physics/geometric-optics",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Espelhos e lentes ENEM",
            "url": "https://www.youtube.com/results?search_query=espelhos+lentes+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Eletricidade": [
        {
            "title": "Khan Academy - Circuitos",
            "url": "https://pt.khanacademy.org/science/physics/circuits-topic",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Lei de Ohm ENEM",
            "url": "https://www.youtube.com/results?search_query=lei+de+ohm+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
    "Magnetismo": [
        {
            "title": "Khan Academy - Magnetismo",
            "url": "https://pt.khanacademy.org/science/physics/magnetic-forces-and-magnetic-fields",
            "type": "teoria",
            "source": "Khan Academy",
        },
        {
            "title": "YouTube: Campo magnético ENEM",
            "url": "https://www.youtube.com/results?search_query=campo+magn%C3%A9tico+enem",
            "type": "video",
            "source": "YouTube",
        },
    ],
}

CONTENT_BLOCKS = [
    "Teoria-base: defina conceitos, unidades e grandezas do tema.",
    "Leitura guiada: explique o fenômeno com um exemplo do cotidiano.",
    "Fórmulas-chave: liste e explique quando usar cada uma.",
    "Exemplo resolvido: passo a passo de um problema típico do ENEM.",
    "Exercícios rápidos: 3 questões para fixação imediata.",
    "Revisão ativa: escreva 3 pontos-chave sem consultar o material.",
]

TOPIC_CONTENT = {
    "Cinemática": {
        "overview": "Estude movimentos com foco em velocidade e aceleracao, usando graficos e leitura de enunciados tipicos do ENEM.",
        "concepts": [
            "Posicao, deslocamento e trajetoria.",
            "Velocidade media e velocidade instantanea.",
            "Aceleracao e interpretacao de graficos s x t e v x t.",
        ],
        "formulas": [
            "v = Δs / Δt",
            "a = Δv / Δt",
            "s = s0 + v * t (MRU)",
            "v = v0 + a * t (MRUV)",
        ],
        "example": "Um carro parte do repouso e acelera a 2 m/s^2 por 5 s. Calcule a velocidade final e a distancia percorrida.",
        "demo": "Desenhe um grafico v x t e destaque a area que representa o deslocamento.",
        "images": [
            {"src": "/static/img/motion.svg", "caption": "Grafico velocidade x tempo"},
        ],
    },
    "Dinâmica": {
        "overview": "Relacione forcas e movimento com as Leis de Newton e interprete esquemas de forcas em blocos, planos inclinados e tracao.",
        "concepts": [
            "Primeira, segunda e terceira leis de Newton.",
            "Forca resultante e diagrama de corpo livre.",
            "Atrito estatico e cinetico em situacoes reais.",
        ],
        "formulas": [
            "F = m * a",
            "P = m * g",
            "F_at = μ * N",
        ],
        "example": "Um bloco de 4 kg sofre uma forca horizontal de 12 N. Calcule a aceleracao assumindo atrito desprezivel.",
        "demo": "Monte o diagrama de forcas e identifique a forca resultante.",
        "images": [
            {"src": "/static/img/forces.svg", "caption": "Diagrama de forcas"},
        ],
    },
    "Energia": {
        "overview": "Use conservacao de energia e trabalho para resolver problemas com potencia e variacao de altura.",
        "concepts": [
            "Trabalho de uma forca constante.",
            "Energia cinetica e potencial gravitacional.",
            "Potencia media e rendimento.",
        ],
        "formulas": [
            "W = F * d * cos(θ)",
            "E_c = (1/2) * m * v^2",
            "E_p = m * g * h",
            "P = W / Δt",
        ],
        "example": "Uma pessoa eleva um objeto de 2 kg a 3 m em 4 s. Calcule o trabalho e a potencia media.",
        "demo": "Compare energia potencial antes e depois e descreva a conversao em energia cinetica.",
        "images": [
            {"src": "/static/img/energy.svg", "caption": "Conversao de energia"},
        ],
    },
    "Termologia": {
        "overview": "Concentre-se em calor, temperatura e escalas, e aplique calorimetria simples para mudancas de estado.",
        "concepts": [
            "Calor sensivel e calor latente.",
            "Escalas termometricas e equilibrio termico.",
            "Transferencia de calor: conducao, conveccao e radiacao.",
        ],
        "formulas": [
            "Q = m * c * ΔT",
            "Q = m * L",
        ],
        "example": "Qual o calor necessario para aquecer 0,5 kg de agua de 20°C para 80°C? Use c = 4,2 kJ/kg°C.",
        "demo": "Explique como a conveccao aparece em panelas no fogao.",
        "images": [
            {"src": "/static/img/heat.svg", "caption": "Transferencia de calor"},
        ],
    },
    "Ondulatória": {
        "overview": "Analise ondas mecanicas e sonoras, interpretando frequencia, comprimento de onda e velocidade.",
        "concepts": [
            "Elementos de uma onda: crista, vale, amplitude.",
            "Frequencia, periodo e comprimento de onda.",
            "Efeito Doppler e aplicacoes no cotidiano.",
        ],
        "formulas": [
            "v = λ * f",
            "T = 1 / f",
        ],
        "example": "Uma onda de 3 Hz tem comprimento de 2 m. Calcule sua velocidade.",
        "demo": "Desenhe uma onda e marque um comprimento de onda completo.",
        "images": [
            {"src": "/static/img/wave.svg", "caption": "Comprimento de onda"},
        ],
    },
    "Óptica": {
        "overview": "Estude reflexao e refracao, com foco em espelhos, lentes e formacao de imagens.",
        "concepts": [
            "Leis da reflexao e refracao.",
            "Formacao de imagens em espelhos planos e esfericos.",
            "Lentes convergentes e divergentes.",
        ],
        "formulas": [
            "1/f = 1/p + 1/p'",
            "n1 * sin(θ1) = n2 * sin(θ2)",
        ],
        "example": "Uma lente convergente de 20 cm forma imagem a 40 cm. Encontre a distancia do objeto.",
        "demo": "Descreva como um raio se comporta ao atravessar uma lente convergente.",
        "images": [
            {"src": "/static/img/optics.svg", "caption": "Reflexao e refracao"},
        ],
    },
    "Eletricidade": {
        "overview": "Resolva circuitos simples com Lei de Ohm e analise potencia e consumo de energia.",
        "concepts": [
            "Corrente eletrica, tensao e resistencia.",
            "Associacao de resistores em serie e paralelo.",
            "Potencia eletrica e consumo em kWh.",
        ],
        "formulas": [
            "U = R * I",
            "P = U * I",
            "E = P * Δt",
        ],
        "example": "Um resistor de 10 Ω recebe 2 A. Calcule a tensao e a potencia dissipada.",
        "demo": "Desenhe um circuito com fonte e resistor e identifique a corrente.",
        "images": [
            {"src": "/static/img/circuit.svg", "caption": "Circuito simples"},
        ],
    },
    "Magnetismo": {
        "overview": "Relacione campos magneticos com cargas em movimento e aplicacoes tecnologicas.",
        "concepts": [
            "Campo magnetico e linhas de campo.",
            "Forca magnetica sobre cargas em movimento.",
            "Aplicacoes: motores, alto-falantes e bussolas.",
        ],
        "formulas": [
            "F = q * v * B * sin(θ)",
        ],
        "example": "Uma carga entra em um campo magnetico perpendicular. Descreva o tipo de movimento.",
        "demo": "Indique o sentido das linhas de campo ao redor de um imã.",
        "images": [
            {"src": "/static/img/magnet.svg", "caption": "Linhas de campo magnetico"},
        ],
    },
}


@dataclass(frozen=True)
class DayPlan:
    day: date
    topic: str
    explanation: str
    blocks: tuple[str, ...]
    difficulty: str
    resources: tuple[dict, ...]


@dataclass(frozen=True)
class Progress:
    completed_dates: tuple[str, ...]


def calcular_blocos_por_hora(horas: float) -> int:
    if horas <= 1.5:
        return 2
    if horas <= 3:
        return 3
    if horas <= 5:
        return 4
    return 5


def gerar_plano_diario(
    dias: int,
    horas: float,
    inicio: date | None = None,
) -> list[DayPlan]:
    base_date = inicio or date.today()
    blocos = calcular_blocos_por_hora(horas)
    planos: list[DayPlan] = []

    for offset in range(dias):
        topico = BASE_TOPICS[offset % len(BASE_TOPICS)]
        peso = float(topico.get("peso", 1.0))
        dificuldade = "intermediario"
        if peso >= 1.15:
            dificuldade = "avancado"
        elif peso <= 0.9:
            dificuldade = "iniciante"
        blocks = tuple(CONTENT_BLOCKS[:blocos])
        recursos = tuple(RESOURCES.get(topico["titulo"], []))
        planos.append(
            DayPlan(
                day=base_date + timedelta(days=offset),
                topic=topico["titulo"],
                explanation=topico["explicacao"],
                blocks=blocks,
                difficulty=dificuldade,
                resources=recursos,
            )
        )

    return planos


def carregar_progresso(path: Path) -> Progress:
    if not path.exists():
        return Progress(completed_dates=tuple())

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        datas = tuple(raw.get("completed_dates", []))
        return Progress(completed_dates=datas)
    except (json.JSONDecodeError, OSError, TypeError):
        return Progress(completed_dates=tuple())


def salvar_progresso(path: Path, progress: Progress) -> None:
    payload = {"completed_dates": list(progress.completed_dates)}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def marcar_concluido(progress: Progress, day: date) -> Progress:
    day_str = day.isoformat()
    datas = set(progress.completed_dates)
    datas.add(day_str)
    return Progress(completed_dates=tuple(sorted(datas)))


def esta_concluido(progress: Progress, day: date) -> bool:
    return day.isoformat() in progress.completed_dates


def formatar_plano(plan: DayPlan) -> str:
    linhas = [
        f"Dia {plan.day.strftime('%d/%m/%Y')} - {plan.topic}\n",
        f"Objetivo do dia: {plan.explanation}\n\n",
        "Roteiro de estudo:\n",
    ]
    for index, bloco in enumerate(plan.blocks, start=1):
        linhas.append(f"{index}. {bloco}\n")
    if plan.resources:
        linhas.append("\nSugestoes de estudo:\n")
        for item in plan.resources:
            linhas.append(f"- {item['title']} ({item['source']})\n")
    return "".join(linhas)


def get_topic_content(topic: str) -> dict:
    return TOPIC_CONTENT.get(topic, TOPIC_CONTENT["Cinemática"])


def formatar_resumo(progresso: Progress, planos: Iterable[DayPlan]) -> str:
    total = len(list(planos))
    concluidos = len(progresso.completed_dates)
    return f"Dias concluídos: {concluidos}/{total}\n"
