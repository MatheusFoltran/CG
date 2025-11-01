import numpy as np
from math_utils import calcular_vetor_normal
from projection import (
    calcular_parametros_d,
    criar_matriz_perspectiva,
    projetar_objeto,
    janela_para_viewport
)
from renderer import desenhar_wireframe

def main():
    print("=" * 50)
    print("SISTEMA DE PROJEÇÃO PERSPECTIVA")
    print("=" * 50)
    
    # ========================================
    # 1. DADOS DE ENTRADA
    # ========================================
    
    # Ponto de Vista (Câmera)
    C = np.array([5, 5, 10])
    
    # Plano de Projeção (3 pontos)
    P1 = np.array([0, 0, 0])
    P2 = np.array([10, 0, 0])
    P3 = np.array([0, 10, 0])
    R0 = P1  # Ponto sobre o plano
    
    # Objeto 3D - CUBO
    vertices = np.array([
        [0, 0, 0],
        [2, 0, 0],
        [2, 2, 0],
        [0, 2, 0],
        [0, 0, 2],
        [2, 0, 2],
        [2, 2, 2],
        [0, 2, 2]
    ])
    
    # Superfícies (faces do cubo)
    superficies = [
        [0, 1, 2, 3],  # frente
        [4, 5, 6, 7],  # trás
        [0, 1, 5, 4],  # baixo
        [2, 3, 7, 6],  # cima
        [0, 3, 7, 4],  # esquerda
        [1, 2, 6, 5]   # direita
    ]
    
    print(f"\n📌 Ponto de Vista: {C}")
    print(f"📌 Número de Vértices: {len(vertices)}")
    print(f"📌 Número de Faces: {len(superficies)}")
    
    # ========================================
    # 2. CALCULAR VETOR NORMAL DO PLANO
    # ========================================
    
    N = calcular_vetor_normal(P1, P2, P3)
    print(f"\n🧮 Vetor Normal: {N}")
    
    # ========================================
    # 3. CALCULAR d0, d1, d
    # ========================================
    
    d0, d1, d = calcular_parametros_d(C, R0, N)
    print(f"\n📐 d0 = {d0}")
    print(f"📐 d1 = {d1}")
    print(f"📐 d = {d}")
    
    # ========================================
    # 4. CRIAR MATRIZ DE PERSPECTIVA
    # ========================================
    
    M_per = criar_matriz_perspectiva(C, N, d0, d)
    print(f"\n🔢 Matriz de Perspectiva:")
    print(M_per)
    
    # ========================================
    # 5. PROJETAR VÉRTICES NO PLANO
    # ========================================
    
    vertices_2d = projetar_objeto(vertices, M_per)
    print(f"\n📍 Vértices Projetados (plano 2D):")
    for i, v in enumerate(vertices_2d):
        print(f"   V{i}: {v}")
    
    # ========================================
    # 6. TRANSFORMAR PARA VIEWPORT (TELA)
    # ========================================
    
    largura_tela = 800
    altura_tela = 600
    
    pontos_tela = janela_para_viewport(vertices_2d, largura_tela, altura_tela)
    print(f"\n🖥️  Pontos na Tela (pixels):")
    for i, p in enumerate(pontos_tela):
        print(f"   V{i}: ({p[0]:.1f}, {p[1]:.1f})")
    
    # ========================================
    # 7. RENDERIZAR
    # ========================================
    
    print(f"\n🎨 Renderizando...")
    desenhar_wireframe(pontos_tela, superficies, largura_tela, altura_tela)
    
    print("\n✅ CONCLUÍDO!\n")
    print("=" * 50)

if __name__ == "__main__":
    main()