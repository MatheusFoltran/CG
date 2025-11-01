"""
projection.py
Sistema de projeção perspectiva cônica.
Implementa transformações para projetar objetos 3D em 2D usando perspectiva cônica.

Perspectiva Cônica:
- Centro de projeção (C): ponto de vista da câmera
- Plano de projeção: definido por 3 pontos não-colineares
- Raios de projeção convergem para o centro C (pontos de fuga)
- Distância do ponto ao plano afeta o tamanho projetado
"""

import numpy as np
from math_utils import produto_escalar


def calcular_parametros_d(C, R0, N):
    """
    Calcula os parâmetros d0, d1 e d conforme especificação do PDF.
    
    Fórmulas:
        d0 = x0·nx + y0·ny + z0·nz  (produto escalar de R0 com N)
        d1 = a·nx + b·ny + c·nz     (produto escalar de C com N)
        d = d0 - d1
    
    Args:
        C: ponto de vista (câmera) [a, b, c]
        R0: ponto sobre o plano [x0, y0, z0]
        N: vetor normal ao plano [nx, ny, nz]
    
    Returns:
        tuple: (d0, d1, d)
    """
    # Extrair coordenadas explicitamente (como no PDF)
    x0, y0, z0 = R0
    a, b, c = C
    Nx, Ny, Nz = N
    
    # Calcular d0 = R0 · N
    d0 = x0 * Nx + y0 * Ny + z0 * Nz
    
    # Calcular d1 = C · N
    d1 = a * Nx + b * Ny + c * Nz
    
    # Calcular d
    d = d0 - d1
    
    return d0, d1, d


def criar_matriz_perspectiva(C, N, d0, d):
    """
    Monta a matriz de projeção perspectiva 4×4.
    
    Matriz conforme especificação do PDF:
    ⎡ d+a·nx   a·ny    a·nz    -a·d0 ⎤
    ⎢ b·nx   d+b·ny   b·nz    -b·d0 ⎥
    ⎢ c·nx    c·ny   d+c·nz   -c·d0 ⎥
    ⎣  nx      ny      nz        d   ⎦
    
    Args:
        C: ponto de vista [a, b, c]
        N: vetor normal [nx, ny, nz]
        d0: parâmetro d0
        d: parâmetro d
    
    Returns:
        array 4×4: matriz de projeção perspectiva
    """
    a, b, c = C
    Nx, Ny, Nz = N
    
    M_per = np.array([
        [d + a*Nx,     a*Ny,         a*Nz,         -a*d0],
        [b*Nx,         d + b*Ny,     b*Nz,         -b*d0],
        [c*Nx,         c*Ny,         d + c*Nz,     -c*d0],
        [Nx,           Ny,           Nz,           d]
    ])
    
    return M_per


def projetar_ponto(ponto, matriz):
    """
    Projeta um ponto 3D no plano de projeção usando perspectiva cônica.
    
    Perspectiva Cônica:
    - Raios de projeção convergem para o centro de projeção C
    - Pontos mais distantes de C aparecem menores (efeito de profundidade)
    - Linhas paralelas convergem para pontos de fuga no plano de projeção
    - A divisão por w' implementa a convergência perspectiva
    
    Processo:
    1. Converter para coordenadas homogêneas: P = [x, y, z, 1]
    2. Multiplicar pela matriz: P' = M_per · P
    3. Resultado em coordenadas homogêneas: P' = [x', y', z', w']
    4. Divisão perspectiva: XC = x'/w', YC = y'/w', ZC = z'/w'
       💡 Esta divisão cria o efeito de PONTO DE FUGA
       💡 w' varia com a distância do ponto ao plano
       💡 Quanto maior w', menor o ponto projetado
    5. Coordenadas no plano: XP = XC, YP = YC
    
    Args:
        ponto: array [x, y, z] - coordenadas 3D
        matriz: matriz de perspectiva 4×4
    
    Returns:
        array [XP, YP]: coordenadas 2D no plano de projeção
    """
    x, y, z = ponto
    
    # 1. Coordenadas homogêneas
    P_homogeneas = np.array([x, y, z, 1])
    
    # 2. Multiplicação: P' = M_per · P
    P_prime = matriz @ P_homogeneas
    
    x_prime, y_prime, z_prime, w_prime = P_prime
    
    # 3. DIVISÃO PERSPECTIVA (cria o efeito de ponto de fuga)
    if w_prime != 0:
        XC = x_prime / w_prime
        YC = y_prime / w_prime
        ZC = z_prime / w_prime
    else:
        # Ponto no infinito - no ponto de fuga
        XC, YC, ZC = 0, 0, 0
        print(f"⚠️ Aviso: Ponto {ponto} está no ponto de fuga (w'=0)")
    
    # 4. Coordenadas no plano de projeção
    XP = XC
    YP = YC
    
    return np.array([XP, YP])


def projetar_objeto(vertices, matriz):
    """
    Projeta todos os vértices de um objeto 3D.
    
    Args:
        vertices: array Nx3 com coordenadas 3D dos vértices
        matriz: matriz de perspectiva 4×4
    
    Returns:
        array Nx2: coordenadas 2D de todos os vértices projetados
    """
    vertices_2d = []
    
    for i, vertice in enumerate(vertices):
        try:
            ponto_2d = projetar_ponto(vertice, matriz)
            vertices_2d.append(ponto_2d)
        except Exception as e:
            print(f"❌ Erro ao projetar vértice {i}: {e}")
            vertices_2d.append(np.array([0, 0]))
    
    return np.array(vertices_2d)


def janela_para_viewport(pontos_2d, u_min=0, u_max=800, v_min=0, v_max=600):
    """
    Transforma coordenadas do plano (janela/mundo) para viewport (dispositivo/tela).
    
    Centraliza e escala o objeto para caber na viewport mantendo proporções.
    
    Args:
        pontos_2d: array Nx2 com coordenadas no plano
        u_min, u_max: limites horizontais da viewport
        v_min, v_max: limites verticais da viewport
    
    Returns:
        array Nx2: coordenadas em pixels na tela
    """
    if len(pontos_2d) == 0:
        return np.array([])
    
    # Limites da janela (mundo)
    x_min = pontos_2d[:, 0].min()
    x_max = pontos_2d[:, 0].max()
    y_min = pontos_2d[:, 1].min()
    y_max = pontos_2d[:, 1].max()
    
    # Dimensões
    largura_janela = x_max - x_min
    altura_janela = y_max - y_min
    largura_viewport = u_max - u_min
    altura_viewport = v_max - v_min
    
    # Evitar divisão por zero
    if largura_janela == 0:
        largura_janela = 1
    if altura_janela == 0:
        altura_janela = 1
    
    # Calcular escala para caber na viewport mantendo proporção
    # Usa a menor escala para garantir que tudo caiba
    escala_x = largura_viewport / largura_janela
    escala_y = altura_viewport / altura_janela
    escala = min(escala_x, escala_y) * 0.8  # 0.8 = margem de 10% em cada lado
    
    # Centro da janela
    centro_janela_x = (x_min + x_max) / 2
    centro_janela_y = (y_min + y_max) / 2
    
    # Centro da viewport
    centro_viewport_u = (u_min + u_max) / 2
    centro_viewport_v = (v_min + v_max) / 2
    
    # Transformar pontos
    pontos_tela = []
    for x, y in pontos_2d:
        # Centralizar na origem
        x_cent = x - centro_janela_x
        y_cent = y - centro_janela_y
        
        # Escalar
        x_esc = x_cent * escala
        y_esc = y_cent * escala
        
        # Mover para centro da viewport
        u = centro_viewport_u + x_esc
        v = centro_viewport_v - y_esc  # Inverter Y (tela cresce para baixo)
        
        pontos_tela.append([u, v])
    
    return np.array(pontos_tela)