import numpy as np

def produto_vetorial(v1, v2):
    """Calcula v1 x v2"""
    return np.cross(v1, v2)

def produto_escalar(v1, v2):
    """Calcula v1 . v2"""
    return np.dot(v1, v2)

def calcular_vetor_normal(P1, P2, P3):
    """
    Calcula vetor normal ao plano definido por 3 pontos.
    N = (P1-P2) x (P3-P2)
    """
    v1 = P1 - P2
    v2 = P3 - P2
    return produto_vetorial(v1, v2)

def normalizar(v):
    """Normaliza um vetor (opcional, pode ser útil)"""
    norma = np.linalg.norm(v)
    return v / norma if norma != 0 else v