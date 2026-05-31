import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from study_plan import (
    calcular_blocos_por_hora,
    carregar_progresso,
    esta_concluido,
    gerar_plano_diario,
    marcar_concluido,
    salvar_progresso,
)


class StudyPlanTests(unittest.TestCase):
    def test_calcular_blocos_por_hora(self) -> None:
        self.assertEqual(calcular_blocos_por_hora(1), 2)
        self.assertEqual(calcular_blocos_por_hora(2.5), 3)
        self.assertEqual(calcular_blocos_por_hora(4), 4)
        self.assertEqual(calcular_blocos_por_hora(6), 5)

    def test_gerar_plano_diario(self) -> None:
        inicio = date(2026, 5, 12)
        planos = gerar_plano_diario(dias=3, horas=2, inicio=inicio)
        self.assertEqual(len(planos), 3)
        self.assertEqual(planos[0].day, inicio)
        self.assertEqual(len(planos[0].blocks), 3)

    def test_progresso_persistente(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "progress.json"
            progresso = carregar_progresso(path)
            self.assertFalse(esta_concluido(progresso, date(2026, 5, 12)))

            progresso = marcar_concluido(progresso, date(2026, 5, 12))
            salvar_progresso(path, progresso)

            progresso_lido = carregar_progresso(path)
            self.assertTrue(esta_concluido(progresso_lido, date(2026, 5, 12)))


if __name__ == "__main__":
    unittest.main()
