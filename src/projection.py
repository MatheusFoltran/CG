import numpy as np
from math_utils import produto_escalar

def calcular_parametros_d(C, R0, N):
    """
    Calcula d0, d1 e d conforme o PDF
    d0 = x0·nx + y0·ny + z0·nz
    d1 = a·nx + b·ny + c·nz
    d = d0 - d1
    """
    x0, y0, z0 = R0
    a, b, c = C
    Nx, Ny, Nz = N
    
    d0 = x0 * Nx + y0 * Ny + z0 * Nz
    d1 = a * Nx + b * Ny + c * Nz
    d = d0 - d1
    
    return d0, d1, d


def criar_matriz_perspectiva(C, N, d0, d):
    """
    Monta a matriz de projeção perspectiva 4x4
    Exatamente como no PDF
    """
    a, b, c = C
    Nx, Ny, Nz = N
    
    M = np.array([
        [d + a*Nx,     a*Ny,         a*Nz,         -a*d0],
        [b*Nx,         d + b*Ny,     b*Nz,         -b*d0],
        [c*Nx,         c*Ny,         d + c*Nz,     -c*d0],
        [Nx,           Ny,           Nz,           d]
    ])
    
    return M


def projetar_ponto(ponto, matriz):
    """
    Projeta um ponto 3D no plano usando a matriz de perspectiva.
    
    P' = M_per · P
    Resultado em coordenadas homogêneas (x', y', z', w')
    
    Converte para cartesianas:
    XC = x'/w
    YC = y'/w
    ZC = z'/w
    
    Coordenadas no plano:
    XP = XC
    YP = YC
    """
    # Converte para coordenadas homogêneas [x, y, z, 1]
    x, y, z = ponto
    P_homo = np.array([x, y, z, 1])
    
    # Multiplica pela matriz: P' = M_per · P
    P_prime = matriz @ P_homo
    
    x_prime, y_prime, z_prime, w_prime = P_prime
    
    # Converte de coordenadas homogêneas para cartesianas
    if w_prime != 0:
        XC = x_prime / w_prime
        YC = y_prime / w_prime
        ZC = z_prime / w_prime
    else:
        # Ponto no infinito ou erro
        XC, YC, ZC = 0, 0, 0
    
    # Coordenadas no plano de projeção
    XP = XC
    YP = YC
    
    return np.array([XP, YP])


def projetar_objeto(vertices, matriz):
    """Projeta todos os vértices de um objeto"""
    vertices_2d = []
    for vertice in vertices:
        ponto_2d = projetar_ponto(vertice, matriz)
        vertices_2d.append(ponto_2d)
    return np.array(vertices_2d)


def janela_para_viewport(pontos_2d, u_min=0, u_max=800, v_min=0, v_max=600):
    """
    Transforma coordenadas do plano (janela/mundo) para viewport (dispositivo/tela).
    Implementação seguindo as fórmulas do PDF.
    
    Centraliza o objeto independente da diferença de razão de aspecto.
    """
    if len(pontos_2d) == 0:
        return np.array([])
    
    # Limites da janela (mundo) - coordenadas do plano
    x_min = pontos_2d[:, 0].min()
    x_max = pontos_2d[:, 0].max()
    y_min = pontos_2d[:, 1].min()
    y_max = pontos_2d[:, 1].max()
    
    # Evitar divisão por zero
    largura_janela = x_max - x_min
    altura_janela = y_max - y_min
    
    if largura_janela == 0:
        largura_janela = 1
    if altura_janela == 0:
        altura_janela = 1
    
    # Razões de aspecto
    Rw = largura_janela / altura_janela  # Razão da janela
    Rv = (u_max - u_min) / (v_max - v_min)  # Razão da viewport
    
    # Fatores de escala
    sx = (u_max - u_min) / largura_janela
    sy = (v_max - v_min) / altura_janela
    
    pontos_tela = []
    
    # Seguindo as fórmulas do PDF
    if Rw > Rv:
        # Ajustar v_max (altura da viewport)
        v_max_novo = (u_max - u_min) / Rw + v_min
        
        # Offset para centralizar verticalmente
        offset_v = (v_max - v_max_novo) / 2
        
        # Aplicar transformação
        for x, y in pontos_2d:
            u = sx * (x - x_min) + u_min
            v = -sy * (y - y_max) + v_max - offset_v
            pontos_tela.append([u, v])
            
    else:  # Rw <= Rv
        # Ajustar u_max (largura da viewport)
        u_max_novo = Rw * (v_max - v_min) + u_min
        
        # Offset para centralizar horizontalmente
        offset_u = (u_max - u_max_novo) / 2
        
        # Aplicar transformação
        for x, y in pontos_2d:
            u = sx * (x - x_min) + u_min + offset_u
            v = -sy * (y - y_max) + v_max
            pontos_tela.append([u, v])
    
    return np.array(pontos_tela)


def janela_para_viewport_matricial(pontos_2d, u_min=0, u_max=800, v_min=0, v_max=600):
    """
    Versão usando matrizes (como no PDF), caso você queira usar.
    Matematicamente equivalente à versão acima, mas usa multiplicação de matrizes.
    """
    if len(pontos_2d) == 0:
        return np.array([])
    
    # Limites da janela
    x_min = pontos_2d[:, 0].min()
    x_max = pontos_2d[:, 0].max()
    y_min = pontos_2d[:, 1].min()
    y_max = pontos_2d[:, 1].max()
    
    largura_janela = x_max - x_min if (x_max - x_min) != 0 else 1
    altura_janela = y_max - y_min if (y_max - y_min) != 0 else 1
    
    # Razões de aspecto
    Rw = largura_janela / altura_janela
    Rv = (u_max - u_min) / (v_max - v_min)
    
    # Fatores de escala
    sx = (u_max - u_min) / largura_janela
    sy = (v_max - v_min) / altura_janela
    
    # Montar matriz de transformação conforme PDF
    if Rw > Rv:
        v_max_novo = (u_max - u_min) / Rw + v_min
        
        M = np.array([
            [sx,  0,   u_min - sx * x_min],
            [0,  -sy,  sy * y_max + (v_max - v_max_novo) / 2 + v_min],
            [0,   0,   1]
        ])
    else:
        u_max_novo = Rw * (v_max - v_min) + u_min
        
        M = np.array([
            [sx,  0,  -sx * x_min + (u_max - u_max_novo) / 2 + u_min],
            [0,  -sy, sy * y_max + v_min],
            [0,   0,  1]
        ])
    
    # Aplicar transformação a todos os pontos
    pontos_tela = []
    for x, y in pontos_2d:
        P_homo = np.array([x, y, 1])
        P_transformed = M @ P_homo
        pontos_tela.append([P_transformed[0], P_transformed[1]])
    
    return np.array(pontos_tela)