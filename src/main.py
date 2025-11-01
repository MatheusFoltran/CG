"""
main.py
Programa principal do sistema de projeção perspectiva.
Orquestra todo o pipeline de transformações.
"""

import numpy as np
from math_utils import calcular_vetor_normal
from projection import (
    calcular_parametros_d,
    criar_matriz_perspectiva,
    projetar_objeto,
    janela_para_viewport
)
from renderer import desenhar_wireframe, salvar_imagem, imprimir_estatisticas


def main():
    """
    Executa todo o pipeline de projeção perspectiva.
    """
    print("\n" + "="*70)
    print(" "*15 + "SISTEMA DE PROJEÇÃO PERSPECTIVA")
    print(" "*20 + "Computação Gráfica - UEM")
    print("="*70)
    
    # ========================================
    # 1. ENTRADA DE DADOS
    # ========================================
    
    print("\n📥 CONFIGURANDO CENA...")
    
    # Ponto de Vista (Câmera)
    C = np.array([5.0, 5.0, 10.0])
    print(f"   Câmera (C): {C}")
    
    # Plano de Projeção (3 pontos distintos não-colineares)
    P1 = np.array([0.0, 0.0, 0.0])
    P2 = np.array([10.0, 0.0, 0.0])
    P3 = np.array([0.0, 10.0, 0.0])
    R0 = P1  # Ponto sobre o plano (pode ser P1, P2 ou P3)
    
    print(f"   Plano: P1={P1}, P2={P2}, P3={P3}")
    print(f"   Ponto Referência (R0): {R0}")
    
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
    ], dtype=float)
    
    # Superfícies (faces) - regra da mão direita
    superficies = [
        [0, 1, 2, 3],  # face z=0 (frente)
        [4, 5, 6, 7],  # face z=2 (trás)
        [0, 1, 5, 4],  # face y=0 (baixo)
        [2, 3, 7, 6],  # face y=2 (cima)
        [0, 3, 7, 4],  # face x=0 (esquerda)
        [1, 2, 6, 5]   # face x=2 (direita)
    ]
    
    print(f"   Objeto: Cubo")
    print(f"   Vértices: {len(vertices)}")
    print(f"   Faces: {len(superficies)}")
    
    # ========================================
    # 2. CALCULAR VETOR NORMAL AO PLANO
    # ========================================
    
    print("\n🧮 CALCULANDO VETOR NORMAL...")
    
    try:
        N = calcular_vetor_normal(P1, P2, P3)
        print(f"   N = {N}")
        print(f"   |N| = {np.linalg.norm(N):.4f}")
    except ValueError as e:
        print(f"   ❌ ERRO: {e}")
        return
    
    # ========================================
    # 3. CALCULAR PARÂMETROS d0, d1, d
    # ========================================
    
    print("\n📐 CALCULANDO PARÂMETROS...")
    
    d0, d1, d = calcular_parametros_d(C, R0, N)
    print(f"   d0 = {d0:.4f}")
    print(f"   d1 = {d1:.4f}")
    print(f"   d = {d:.4f}")
    
    if d == 0:
        print("   ⚠️ AVISO: d=0, câmera está no plano de projeção!")
    
    # ========================================
    # 4. CRIAR MATRIZ DE PERSPECTIVA
    # ========================================
    
    print("\n🔢 MONTANDO MATRIZ DE PERSPECTIVA...")
    
    M_per = criar_matriz_perspectiva(C, N, d0, d)
    print("   Matriz 4×4:")
    for linha in M_per:
        print(f"   [{linha[0]:8.3f} {linha[1]:8.3f} {linha[2]:8.3f} {linha[3]:8.3f}]")
    
    # ========================================
    # 5. PROJETAR VÉRTICES NO PLANO 2D
    # ========================================
    
    print("\n📍 PROJETANDO VÉRTICES...")
    
    vertices_2d = projetar_objeto(vertices, M_per)
    print(f"   Projetados: {len(vertices_2d)} vértices")
    
    # Mostrar alguns vértices projetados
    print("\n   Exemplos (primeiros 4 vértices):")
    for i in range(min(4, len(vertices_2d))):
        print(f"   V{i}: 3D{vertices[i]} → 2D{vertices_2d[i]}")
    
    # ========================================
    # 6. TRANSFORMAR PARA VIEWPORT (TELA)
    # ========================================
    
    print("\n🖥️  TRANSFORMANDO PARA VIEWPORT...")
    
    largura_tela = 800
    altura_tela = 600
    
    pontos_tela = janela_para_viewport(
        vertices_2d, 
        u_min=0, u_max=largura_tela,
        v_min=0, v_max=altura_tela
    )
    
    print(f"   Viewport: {largura_tela}×{altura_tela} pixels")
    print(f"   Pontos mapeados: {len(pontos_tela)}")
    
    # ========================================
    # 7. ESTATÍSTICAS (DEBUG)
    # ========================================
    
    imprimir_estatisticas(vertices, vertices_2d, pontos_tela)
    
    # ========================================
    # 8. RENDERIZAÇÃO
    # ========================================
    
    print("\n🎨 RENDERIZANDO...")
    
    desenhar_wireframe(
        pontos_tela, 
        superficies, 
        largura_tela, 
        altura_tela,
        mostrar_vertices=True,
        titulo="Projeção Perspectiva - Cubo"
    )
    
    # Opcional: Salvar imagem
    # salvar_imagem(pontos_tela, superficies, "resultado.png", largura_tela, altura_tela)
    
    print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
    