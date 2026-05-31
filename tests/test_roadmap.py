import random
import unittest

from roadmap import gerar_texto_roadmap


class RoadmapTests(unittest.TestCase):
    def test_texto_contém_campos_principais(self) -> None:
        rng = random.Random(1)
        texto = gerar_texto_roadmap(
            nome="Aline",
            nivel="iniciante",
            horas="2",
            objetivo="Preparação para OINE",
            rng=rng,
        )

        self.assertIn("Aluno: Aline", texto)
        self.assertIn("Nível: iniciante", texto)
        self.assertIn("SEMANA 1", texto)
        self.assertIn("Sugestão IA:", texto)

    def test_nivel_invalido(self) -> None:
        with self.assertRaises(ValueError):
            gerar_texto_roadmap(
                nome="Carlos",
                nivel="expert",
                horas="1",
                objetivo="Teste",
            )


if __name__ == "__main__":
    unittest.main()
