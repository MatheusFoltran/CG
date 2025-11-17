"""Suite de testes automatizados para o sistema de projeção perspectiva."""

import os
import tempfile
import textwrap
import unittest

import numpy as np

from file_parser import ler_objeto_3d
from math_utils import calcular_vetor_normal, produto_vetorial, produto_escalar
from projection import (
    calcular_parametros_d,
    criar_matriz_perspectiva,
    projetar_ponto,
    projetar_objeto,
    janela_para_viewport,
    calcular_pontos_de_fuga
)


class MathUtilsTest(unittest.TestCase):
    def test_produto_vetorial(self):
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        esperado = np.array([0, 0, 1])
        np.testing.assert_array_equal(produto_vetorial(v1, v2), esperado)

    def test_produto_escalar(self):
        v1 = np.array([2, 3, 4])
        v2 = np.array([1, 2, 3])
        self.assertEqual(produto_escalar(v1, v2), 20)

    def test_calcular_vetor_normal(self):
        P1 = np.array([0, 0, 0])
        P2 = np.array([1, 0, 0])
        P3 = np.array([0, 1, 0])
        N = calcular_vetor_normal(P1, P2, P3)
        condicoes = [
            np.allclose(N, np.array([0, 0, 1])),
            np.allclose(N, np.array([0, 0, -1]))
        ]
        self.assertTrue(any(condicoes))


class ProjectionMathTest(unittest.TestCase):
    def setUp(self):
        self.C = np.array([0.0, 0.0, 5.0])
        self.R0 = np.array([0.0, 0.0, 2.0])
        self.P1 = np.array([0.0, 0.0, 2.0])
        self.P2 = np.array([1.0, 0.0, 2.0])
        self.P3 = np.array([0.0, 1.0, 2.0])
        self.N = calcular_vetor_normal(self.P1, self.P2, self.P3)

    def test_parametros_d(self):
        d0, d1, d = calcular_parametros_d(self.C, self.R0, self.N)
        self.assertAlmostEqual(abs(d0), 2.0)
        self.assertAlmostEqual(abs(d1), 5.0)
        self.assertAlmostEqual(abs(d), 3.0)

    def test_matriz_perspectiva_forma(self):
        d0, _, d = calcular_parametros_d(self.C, self.R0, self.N)
        M = criar_matriz_perspectiva(self.C, self.N, d0, d)
        self.assertEqual(M.shape, (4, 4))
        np.testing.assert_allclose(M[3], np.array([*self.N, d]))

    def test_projetar_ponto(self):
        d0, _, d = calcular_parametros_d(self.C, self.R0, self.N)
        M = criar_matriz_perspectiva(self.C, self.N, d0, d)
        ponto_3d = np.array([1.0, 1.0, 0.0])
        ponto_2d = projetar_ponto(ponto_3d, M)
        self.assertEqual(ponto_2d.shape, (2,))
        self.assertTrue(np.all(np.isfinite(ponto_2d)))

    def test_pontos_de_fuga(self):
        resultados = calcular_pontos_de_fuga(self.C, self.N, self.R0)
        # Plano paralelo aos eixos X e Y → pontos de fuga no infinito
        self.assertIsNone(resultados['X'])
        self.assertIsNone(resultados['Y'])
        self.assertIsNotNone(resultados['Z'])


class ViewportTest(unittest.TestCase):
    def test_transformacao_mantem_limites(self):
        pontos = np.array([[0, 0], [1, 0], [1, 1], [0, 1]])
        tela = janela_para_viewport(pontos, 0, 800, 0, 600)
        self.assertTrue(np.all(tela[:, 0] >= 0))
        self.assertTrue(np.all(tela[:, 0] <= 800))
        self.assertTrue(np.all(tela[:, 1] >= 0))
        self.assertTrue(np.all(tela[:, 1] <= 600))


class PipelineTest(unittest.TestCase):
    def test_pipeline_sem_arquivo(self):
        # Cubo mínimo definido inline
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [1, 1, 1],
            [0, 1, 1],
        ])
        C = np.array([1, 1, 5])
        P1 = np.array([0, 0, 2])
        P2 = np.array([1, 0, 2])
        P3 = np.array([0, 1, 2])
        N = calcular_vetor_normal(P1, P2, P3)
        d0, _, d = calcular_parametros_d(C, P1, N)
        M = criar_matriz_perspectiva(C, N, d0, d)
        proj = projetar_objeto(vertices, M)
        tela = janela_para_viewport(proj, 0, 800, 0, 600)
        self.assertEqual(proj.shape, (len(vertices), 2))
        self.assertTrue(np.all(np.isfinite(tela)))


class FileParserTest(unittest.TestCase):
    def test_ler_objeto_temporario(self):
        conteudo = textwrap.dedent(
            """
            NV 2
            0 0 0
            1 0 0

            NS 1
            2 0 1
            """
        ).strip()

        with tempfile.NamedTemporaryFile('w+', suffix='.txt', delete=False) as tmp:
            tmp.write(conteudo)
            tmp_path = tmp.name

        try:
            vertices, superficies, nome = ler_objeto_3d(tmp_path)
        finally:
            os.remove(tmp_path)

        self.assertEqual(vertices.shape, (2, 3))
        self.assertEqual(len(superficies), 1)
        self.assertEqual(nome.lower(), os.path.splitext(os.path.basename(tmp_path))[0].lower())


if __name__ == "__main__":
    unittest.main()