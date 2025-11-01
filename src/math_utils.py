"""
math_utils.py
Funções matemáticas fundamentais para operações vetoriais.
"""

import numpy as np


def produto_vetorial(v1, v2):
    """
    Calcula o produto vetorial (cross product) entre dois vetores.
    
    v1 × v2 = | i    j    k   |
              | v1x  v1y  v1z |
              | v2x  v2y  v2z |
    
    Args:
        v1: array [x, y, z]
        v2: array [x, y, z]
    
    Returns:
        array: vetor resultante [nx, ny, nz]
    """
    return np.cross(v1, v2)


def produto_escalar(v1, v2):
    """
    Calcula o produto escalar (dot product) entre dois vetores.
    
    v1 · v2 = v1x*v2x + v1y*v2y + v1z*v2z
    
    Args:
        v1: array [x, y, z]
        v2: array [x, y, z]
    
    Returns:
        float: resultado do produto escalar
    """
    return np.dot(v1, v2)


def calcular_vetor_normal(P1, P2, P3):
    """
    Calcula o vetor normal a um plano definido por 3 pontos distintos.
    
    Fórmula: N = (P1-P2) × (P3-P2)
    
    NOTA: O PDF fornecido contém um erro de digitação na fórmula de nx
    (usa z3x2 ao invés de z3z2). Esta implementação está CORRETA.
    
    Args:
        P1, P2, P3: arrays com coordenadas [x, y, z] dos pontos
    
    Returns:
        array: vetor normal [Nx, Ny, Nz]
    
    Raises:
        ValueError: se os pontos forem colineares
    """
    v1 = P1 - P2
    v2 = P3 - P2
    
    N = produto_vetorial(v1, v2)
    
    # Verifica se os pontos são colineares (vetor normal seria zero)
    if np.allclose(N, 0):
        raise ValueError("Os pontos P1, P2, P3 são colineares. Não definem um plano único.")
    
    return N


def normalizar_vetor(v):
    """
    Normaliza um vetor (retorna vetor unitário na mesma direção).
    
    v_normalizado = v / |v|
    
    Args:
        v: array com o vetor
    
    Returns:
        array: vetor normalizado
    """
    norma = np.linalg.norm(v)
    if norma == 0:
        return v
    return v / norma


def calcular_distancia(P1, P2):
    """
    Calcula a distância euclidiana entre dois pontos.
    
    Args:
        P1, P2: arrays com coordenadas dos pontos
    
    Returns:
        float: distância
    """
    return np.linalg.norm(P2 - P1)