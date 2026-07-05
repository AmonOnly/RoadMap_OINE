from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

CURRICULO_DIARIO = [
    {
        "titulo": "Cinemática: leitura de gráficos",
        "base": "Cinemática",
        "explicacao": "Interpretar gráficos de posição, velocidade e tempo em questões do ENEM.",
        "peso": 1.0,
    },
    {
        "titulo": "Cinemática: MRU e MRUV",
        "base": "Cinemática",
        "explicacao": "Aplicar MRU e MRUV para resolver movimentos com aceleração constante.",
        "peso": 1.05,
    },
    {
        "titulo": "Dinâmica: leis de Newton",
        "base": "Dinâmica",
        "explicacao": "Relacionar força, massa e aceleração em situações cotidianas.",
        "peso": 1.1,
    },
    {
        "titulo": "Dinâmica: atrito e plano inclinado",
        "base": "Dinâmica",
        "explicacao": "Analisar atrito, decomposição de forças e equilíbrio em rampas.",
        "peso": 1.15,
    },
    {
        "titulo": "Energia: trabalho e potência",
        "base": "Energia",
        "explicacao": "Calcular trabalho, potência e rendimento em situações práticas.",
        "peso": 1.0,
    },
    {
        "titulo": "Energia: conservação e rendimento",
        "base": "Energia",
        "explicacao": "Usar conservação da energia e perdas para resolver problemas do ENEM.",
        "peso": 1.05,
    },
    {
        "titulo": "Termologia: calor e temperatura",
        "base": "Termologia",
        "explicacao": "Diferenciar calor e temperatura e interpretar equilíbrio térmico.",
        "peso": 0.95,
    },
    {
        "titulo": "Termologia: mudanças de estado",
        "base": "Termologia",
        "explicacao": "Entender calor latente, fusão, vaporização e curvas de aquecimento.",
        "peso": 0.95,
    },
    {
        "titulo": "Ondulatória: frequência e período",
        "base": "Ondulatória",
        "explicacao": "Relacionar frequência, período, comprimento de onda e velocidade.",
        "peso": 0.95,
    },
    {
        "titulo": "Ondulatória: som e efeito Doppler",
        "base": "Ondulatória",
        "explicacao": "Aplicar conceitos de som, intensidade e efeito Doppler em contexto real.",
        "peso": 1.0,
    },
    {
        "titulo": "Óptica: espelhos",
        "base": "Óptica",
        "explicacao": "Analisar reflexão, imagem em espelhos planos e esféricos.",
        "peso": 0.95,
    },
    {
        "titulo": "Óptica: lentes e refração",
        "base": "Óptica",
        "explicacao": "Estudar refração, lentes convergentes e divergentes e formação de imagens.",
        "peso": 1.0,
    },
    {
        "titulo": "Eletricidade: lei de Ohm",
        "base": "Eletricidade",
        "explicacao": "Relacionar tensão, corrente e resistência em circuitos simples.",
        "peso": 1.2,
    },
    {
        "titulo": "Eletricidade: circuitos e potência",
        "base": "Eletricidade",
        "explicacao": "Calcular potência, consumo e associações de resistores.",
        "peso": 1.15,
    },
    {
        "titulo": "Magnetismo: campo e força",
        "base": "Magnetismo",
        "explicacao": "Estudar linhas de campo, força magnética e aplicações tecnológicas.",
        "peso": 0.9,
    },
    {
        "titulo": "Magnetismo: aplicações tecnológicas",
        "base": "Magnetismo",
        "explicacao": "Reconhecer motores, geradores, bússolas e eletroímãs em uso cotidiano.",
        "peso": 0.85,
    },
]

TOPIC_ALIASES = {item["titulo"]: item["base"] for item in CURRICULO_DIARIO}

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
        "overview": "Estude movimentos com foco em velocidade e aceleração, usando gráficos e leitura de enunciados típicos do ENEM.",
        "concepts": [
            "Posição, deslocamento e trajetória.",
            "Velocidade média e velocidade instantânea.",
            "Aceleração e interpretação de gráficos s x t e v x t.",
        ],
        "formulas": [
            "v = Δs / Δt",
            "a = Δv / Δt",
            "s = s0 + v * t (MRU)",
            "v = v0 + a * t (MRUV)",
        ],
        "example": "Um carro parte do repouso e acelera a 2 m/s^2 por 5 s. Calcule a velocidade final e a distância percorrida.",
        "demo": "Desenhe um gráfico v x t e destaque a área que representa o deslocamento.",
        "images": [
            {"src": "/static/img/motion.svg", "caption": "Gráfico velocidade x tempo"},
        ],
        "practice": [
            "Leia o gráfico antes de calcular qualquer valor.",
            "Identifique unidade, sentido e intervalo de tempo.",
            "Compare distância percorrida com deslocamento.",
        ],
        "common_mistakes": [
            "Confundir velocidade média com velocidade instantânea.",
            "Ignorar unidades no resultado final.",
            "Misturar deslocamento com distância percorrida.",
        ],
        "exam_tips": [
            "Em gráfico s x t, a inclinação indica velocidade.",
            "Em gráfico v x t, a área representa deslocamento.",
        ],
    },
    "Dinâmica": {
        "overview": "Relacione forças e movimento com as Leis de Newton e interprete esquemas de forças em blocos, planos inclinados e tração.",
        "concepts": [
            "Primeira, segunda e terceira leis de Newton.",
            "Força resultante e diagrama de corpo livre.",
            "Atrito estático e cinético em situações reais.",
        ],
        "formulas": [
            "F = m * a",
            "P = m * g",
            "F_at = μ * N",
        ],
        "example": "Um bloco de 4 kg sofre uma força horizontal de 12 N. Calcule a aceleração assumindo atrito desprezível.",
        "demo": "Monte o diagrama de forças e identifique a força resultante.",
        "images": [
            {"src": "/static/img/forces.svg", "caption": "Diagrama de forças"},
        ],
        "practice": [
            "Desenhe o diagrama de corpo livre antes de usar as contas.",
            "Some apenas as forças na mesma direção do movimento.",
            "Separe peso, normal, atrito e força aplicada.",
        ],
        "common_mistakes": [
            "Esquecer de decompor a força no plano inclinado.",
            "Somar vetores em direções diferentes sem projetar.",
            "Confundir massa com peso.",
        ],
        "exam_tips": [
            "O ENEM cobra leitura visual das forças antes da fórmula.",
            "Se houver equilíbrio, a resultante é zero.",
        ],
    },
    "Energia": {
        "overview": "Use conservação de energia e trabalho para resolver problemas com potência e variação de altura.",
        "concepts": [
            "Trabalho de uma força constante.",
            "Energia cinética e potencial gravitacional.",
            "Potência média e rendimento.",
        ],
        "formulas": [
            "W = F * d * cos(θ)",
            "E_c = (1/2) * m * v^2",
            "E_p = m * g * h",
            "P = W / Δt",
        ],
        "example": "Uma pessoa eleva um objeto de 2 kg a 3 m em 4 s. Calcule o trabalho e a potência média.",
        "demo": "Compare energia potencial antes e depois e descreva a conversão em energia cinética.",
        "images": [
            {"src": "/static/img/energy.svg", "caption": "Conversão de energia"},
        ],
        "practice": [
            "Sempre compare energia inicial e final do sistema.",
            "Verifique se há perdas por atrito ou dissipação.",
            "Use potência para relacionar energia e tempo.",
        ],
        "common_mistakes": [
            "Esquecer que trabalho é variação de energia.",
            "Misturar energia com potência.",
            "Ignorar a altura no cálculo de energia potencial.",
        ],
        "exam_tips": [
            "Problemas de rampas geralmente misturam energia e forças.",
            "Leia se o enunciado quer energia, trabalho ou potência.",
        ],
    },
    "Termologia": {
        "overview": "Concentre-se em calor, temperatura e escalas, e aplique calorimetria simples para mudanças de estado.",
        "concepts": [
            "Calor sensível e calor latente.",
            "Escalas termométricas e equilíbrio térmico.",
            "Transferência de calor: condução, convecção e radiação.",
        ],
        "formulas": [
            "Q = m * c * ΔT",
            "Q = m * L",
        ],
        "example": "Qual o calor necessário para aquecer 0,5 kg de água de 20°C para 80°C? Use c = 4,2 kJ/kg°C.",
        "demo": "Explique como a convecção aparece em panelas no fogão.",
        "images": [
            {"src": "/static/img/heat.svg", "caption": "Transferência de calor"},
        ],
        "practice": [
            "Diferencie calor sensível de calor latente.",
            "Associe o tipo de transferência de calor ao contexto.",
            "Converta unidades quando necessário.",
        ],
        "common_mistakes": [
            "Tratar calor e temperatura como a mesma coisa.",
            "Esquecer o sinal da troca térmica.",
            "Confundir mudança de temperatura com mudança de estado.",
        ],
        "exam_tips": [
            "A curva de aquecimento costuma separar trechos com e sem variação de temperatura.",
            "Questões de cotidiano costumam citar geladeira, panela e isolamento térmico.",
        ],
    },
    "Ondulatória": {
        "overview": "Analise ondas mecânicas e sonoras, interpretando frequência, comprimento de onda e velocidade.",
        "concepts": [
            "Elementos de uma onda: crista, vale, amplitude.",
            "Frequência, período e comprimento de onda.",
            "Efeito Doppler e aplicações no cotidiano.",
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
        "practice": [
            "Use v = lambda * f com unidades coerentes.",
            "Leia frequência e período como inversos.",
            "Desenhe a onda para localizar amplitude e comprimento de onda.",
        ],
        "common_mistakes": [
            "Trocar frequência por período.",
            "Esquecer que a velocidade depende do meio.",
            "Usar unidade errada para comprimento de onda.",
        ],
        "exam_tips": [
            "Som e luz aparecem em contextos de tecnologia e comunicação.",
            "Efeito Doppler exige observar se a fonte se aproxima ou se afasta.",
        ],
    },
    "Óptica": {
        "overview": "Estude reflexão e refração, com foco em espelhos, lentes e formação de imagens.",
        "concepts": [
            "Leis da reflexão e refração.",
            "Formação de imagens em espelhos planos e esféricos.",
            "Lentes convergentes e divergentes.",
        ],
        "formulas": [
            "1/f = 1/p + 1/p'",
            "n1 * sin(θ1) = n2 * sin(θ2)",
        ],
        "example": "Uma lente convergente de 20 cm forma imagem a 40 cm. Encontre a distância do objeto.",
        "demo": "Descreva como um raio se comporta ao atravessar uma lente convergente.",
        "images": [
            {"src": "/static/img/optics.svg", "caption": "Reflexão e refração"},
        ],
        "practice": [
            "Identifique se a lente é convergente ou divergente.",
            "Desenhe os raios principais para formar a imagem.",
            "Compare objeto, imagem e foco antes de concluir.",
        ],
        "common_mistakes": [
            "Trocar reflexão por refração.",
            "Erra o sinal da imagem em espelhos e lentes.",
            "Esquecer o papel do índice de refração.",
        ],
        "exam_tips": [
            "Leitura de figuras ajuda muito nas questões de óptica.",
            "Em lentes, o tipo de imagem depende da posição do objeto.",
        ],
    },
    "Eletricidade": {
        "overview": "Resolva circuitos simples com Lei de Ohm e analise potência e consumo de energia.",
        "concepts": [
            "Corrente elétrica, tensão e resistência.",
            "Associação de resistores em série e paralelo.",
            "Potência elétrica e consumo em kWh.",
        ],
        "formulas": [
            "U = R * I",
            "P = U * I",
            "E = P * Δt",
        ],
        "example": "Um resistor de 10 Ω recebe 2 A. Calcule a tensão e a potência dissipada.",
        "demo": "Desenhe um circuito com fonte e resistor e identifique a corrente.",
        "images": [
            {"src": "/static/img/circuit.svg", "caption": "Circuito simples"},
        ],
        "practice": [
            "Use U = R * I antes de qualquer outra conta.",
            "Leia se os resistores estão em série ou paralelo.",
            "Verifique potência e consumo quando o enunciado pedir gasto de energia.",
        ],
        "common_mistakes": [
            "Confundir corrente com tensão.",
            "Somar resistências em paralelo como se fosse série.",
            "Esquecer a unidade de potência elétrica.",
        ],
        "exam_tips": [
            "O ENEM costuma contextualizar com contas de energia da casa.",
            "Leia a potência em kW quando o problema envolver consumo.",
        ],
    },
    "Magnetismo": {
        "overview": "Relacione campos magnéticos com cargas em movimento e aplicações tecnológicas.",
        "concepts": [
            "Campo magnético e linhas de campo.",
            "Força magnética sobre cargas em movimento.",
            "Aplicações: motores, alto-falantes e bússolas.",
        ],
        "formulas": [
            "F = q * v * B * sin(θ)",
        ],
        "example": "Uma carga entra em um campo magnético perpendicular. Descreva o tipo de movimento.",
        "demo": "Indique o sentido das linhas de campo ao redor de um imã.",
        "images": [
            {"src": "/static/img/magnet.svg", "caption": "Linhas de campo magnético"},
        ],
        "practice": [
            "Observe o sentido do campo antes de indicar a força.",
            "Associe o tema a motores, geradores e bússolas.",
            "Leia a regra da mão direita quando necessário.",
        ],
        "common_mistakes": [
            "Trocar o sentido do campo magnético.",
            "Esquecer que a força depende do movimento da carga.",
            "Confundir polo norte e sul em esquemas.",
        ],
        "exam_tips": [
            "Questões costumam cobrar aplicações tecnológicas.",
            "Desenhe o campo para não se perder no sentido das linhas.",
        ],
    },
}


@dataclass(frozen=True)
class DayPlan:
    day: date
    topic: str
    base_topic: str
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
        topico = CURRICULO_DIARIO[offset % len(CURRICULO_DIARIO)]
        peso = float(topico.get("peso", 1.0))
        dificuldade = "intermediário"
        if peso >= 1.15:
            dificuldade = "avançado"
        elif peso <= 0.9:
            dificuldade = "iniciante"
        blocks = tuple(CONTENT_BLOCKS[:blocos])
        recursos = tuple(RESOURCES.get(topico["base"], []))
        planos.append(
            DayPlan(
                day=base_date + timedelta(days=offset),
                topic=topico["titulo"],
                base_topic=topico["base"],
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
        f"Foco do dia: {plan.explanation}\n",
        f"Base do conteudo: {plan.base_topic}\n\n",
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
    base_topic = TOPIC_ALIASES.get(topic, topic)
    return TOPIC_CONTENT.get(base_topic, TOPIC_CONTENT["Cinemática"])


def formatar_resumo(progresso: Progress, planos: Iterable[DayPlan]) -> str:
    total = len(list(planos))
    concluidos = len(progresso.completed_dates)
    return f"Dias concluídos: {concluidos}/{total}\n"
