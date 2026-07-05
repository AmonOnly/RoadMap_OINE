import random
from typing import Optional

TOPICOS = [
    {
        "titulo": "Mecânica",
        "descricao": "Movimento, força e leis de Newton",
    },
    {
        "titulo": "Termologia",
        "descricao": "Calor, temperatura e calorimetria",
    },
    {
        "titulo": "Eletricidade e Magnetismo",
        "descricao": "Circuitos, corrente e campo magnético",
    },
    {
        "titulo": "Ondas, Óptica e Acústica",
        "descricao": "Fenômenos ondulatórios e ópticos",
    },
    {
        "titulo": "Energia, Trabalho e Potência",
        "descricao": "Energia, trabalho e potência",
    },
]

RECOMENDACOES = {
    "iniciante": [
        "Utilize mapas mentais e resumos.",
        "Resolva exercícios básicos antes de avançar.",
        "Assista videoaulas introdutórias.",
        "Foque em compreender os conceitos fundamentais.",
    ],
    "intermediário": [
        "Faça exercícios contextualizados.",
        "Treine interpretação física dos problemas.",
        "Utilize revisões ativas semanalmente.",
        "Resolva listas com tempo controlado.",
    ],
    "avançado": [
        "Resolva problemas olímpicos complexos.",
        "Treine estratégias próprias de resolução.",
        "Faça simulados completos da OINE.",
        "Estude questões discursivas avançadas.",
    ],
}


def gerar_recomendacao(nivel: str, rng: Optional[random.Random] = None) -> str:
    if nivel not in RECOMENDACOES:
        raise ValueError("Nível inválido")

    sorteador = rng or random
    return sorteador.choice(RECOMENDACOES[nivel])


def gerar_texto_roadmap(
    nome: str,
    nivel: str,
    horas: str,
    objetivo: str,
    rng: Optional[random.Random] = None,
) -> str:
    if not nome.strip():
        raise ValueError("Nome não pode estar vazio")

    if nivel not in RECOMENDACOES:
        raise ValueError("Nível inválido")

    texto = []
    texto.append("=== ROADMAP PERSONALIZADO ===\n")
    texto.append(f"Aluno: {nome}\n")
    texto.append(f"Nível: {nivel}\n")
    texto.append(f"Horas por dia: {horas}\n")
    texto.append(f"Objetivo: {objetivo}\n\n")
    texto.append("==============================\n\n")

    for semana, topico in enumerate(TOPICOS, start=1):
        recomendacao = gerar_recomendacao(nivel, rng=rng)
        texto.append(f"SEMANA {semana}\n")
        texto.append(f"Tópico: {topico['titulo']}\n")
        texto.append(f"Descrição: {topico['descricao']}\n")
        texto.append(f"Sugestão IA: {recomendacao}\n")
        texto.append(
            f"Plano diário: {horas}h focando teoria + exercícios + revisão.\n"
        )
        texto.append("\n-----------------------------\n\n")

    texto.append(
        "\nIA aplicada: cada aluno recebe sugestões diferentes automaticamente.\n"
    )

    return "".join(texto)
