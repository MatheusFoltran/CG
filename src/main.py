"""
main.py
Programa principal do sistema de projeção perspectiva cônica.
Orquestra todo o pipeline de transformações.

Uso:
    python main.py [caminho_arquivo_objeto]
    
Exemplo:
    python main.py ../objetos/cubo.txt
    python main.py ../objetos/piramide.txt
"""

import sys
import os
import numpy as np
from math_utils import calcular_vetor_normal
from projection import (
    calcular_parametros_d,
    criar_matriz_perspectiva,
    projetar_objeto,
    janela_para_viewport
)
from renderer import desenhar_wireframe, salvar_imagem, imprimir_estatisticas
from file_parser import ler_objeto_3d, listar_objetos_disponiveis, imprimir_info_objeto


def obter_arquivo_objeto():
    """
    Obtém o arquivo de objeto a partir dos argumentos da linha de comando
    ou permite seleção interativa.
    
    Returns:
        str: caminho para o arquivo do objeto
    """
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
        if os.path.exists(caminho):
            return caminho
        else:
            print(f"⚠️ Arquivo não encontrado: {caminho}")
    
    # Tentar listar objetos disponíveis no diretório padrão
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_objetos = os.path.join(os.path.dirname(dir_atual), 'objetos')
    
    objetos = listar_objetos_disponiveis(dir_objetos)
    
    if not objetos:
        print("❌ Nenhum objeto encontrado no diretório 'objetos/'")
        print("\nUso: python main.py <caminho_arquivo_objeto>")
        sys.exit(1)
    
    # Seleção interativa
    print("\n📁 Objetos disponíveis:")
    for i, obj in enumerate(objetos, 1):
        nome = os.path.basename(obj)
        print(f"   {i}. {nome}")
    
    while True:
        try:
            escolha = input("\nEscolha um objeto (1-{}): ".format(len(objetos)))
            idx = int(escolha) - 1
            if 0 <= idx < len(objetos):
                return objetos[idx]
            else:
                print("❌ Escolha inválida. Tente novamente.")
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Operação cancelada.")
            sys.exit(0)


def main():
    """
    Executa todo o pipeline de projeção perspectiva cônica.
    """
    print("\n" + "="*70)
    print(" "*15 + "SISTEMA DE PROJEÇÃO PERSPECTIVA CÔNICA")
    print(" "*20 + "Computação Gráfica - UEM")
    print("="*70)
    
    # ========================================
    # 1. CARREGAR OBJETO DO ARQUIVO
    # ========================================
    
    print("\n📥 CARREGANDO OBJETO 3D...")
    
    try:
        arquivo_objeto = obter_arquivo_objeto()
        vertices, superficies, nome_objeto = ler_objeto_3d(arquivo_objeto)
        imprimir_info_objeto(vertices, superficies, nome_objeto)
    except Exception as e:
        print(f"❌ ERRO ao carregar objeto: {e}")
        return
    
    # ========================================
    # 2. CONFIGURAR CÂMERA E PLANO DE PROJEÇÃO
    # ========================================
    
    print("\n🎥 CONFIGURANDO CÂMERA E PLANO...")
    
    # Calcular centro do objeto para melhor posicionamento
    centro_objeto = vertices.mean(axis=0)
    bbox_min = vertices.min(axis=0)
    bbox_max = vertices.max(axis=0)
    tamanho_objeto = bbox_max - bbox_min
    
    print(f"   Centro do objeto: {centro_objeto}")
    print(f"   Tamanho: {tamanho_objeto}")
    
    # Ponto de Vista (Centro de Projeção - Câmera)
    # Posicionar a câmera atrás e acima do objeto
    distancia_camera = max(tamanho_objeto) * 3  # 3x o tamanho do objeto
    C = centro_objeto + np.array([0, 0, distancia_camera])
    print(f"   Centro de Projeção (C): {C}")
    print(f"   💡 Raios de projeção convergem para C (perspectiva cônica)")
    
    # Plano de Projeção (3 pontos distintos não-colineares)
    # Plano perpendicular ao eixo Z, entre câmera e objeto
    z_plano = centro_objeto[2] - tamanho_objeto[2]  # À frente do objeto
    tam_plano = max(tamanho_objeto) * 2
    
    P1 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] - tam_plano, z_plano])
    P2 = np.array([centro_objeto[0] + tam_plano, centro_objeto[1] - tam_plano, z_plano])
    P3 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] + tam_plano, z_plano])
    R0 = P1  # Ponto sobre o plano
    
    print(f"   Plano em z={z_plano:.2f}")
    print(f"   P1={P1}")
    print(f"   P2={P2}")
    print(f"   P3={P3}")
    
    # ========================================
    # 3. CALCULAR VETOR NORMAL AO PLANO
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
    # 4. CALCULAR PARÂMETROS d0, d1, d
    # ========================================
    
    print("\n📐 CALCULANDO PARÂMETROS...")
    print("   💡 d determina a distância do centro de projeção ao plano")
    
    d0, d1, d = calcular_parametros_d(C, R0, N)
    print(f"   d0 = {d0:.4f}")
    print(f"   d1 = {d1:.4f}")
    print(f"   d = {d:.4f}")
    
    if d == 0:
        print("   ⚠️ AVISO: d=0, câmera está no plano de projeção!")
        print("   💡 Na perspectiva cônica, C deve estar fora do plano")
    
    # ========================================
    # 5. CRIAR MATRIZ DE PERSPECTIVA
    # ========================================
    
    print("\n🔢 MONTANDO MATRIZ DE PERSPECTIVA CÔNICA...")
    print("   💡 A matriz implementa a convergência para o ponto de fuga")
    
    M_per = criar_matriz_perspectiva(C, N, d0, d)
    print("   Matriz 4×4:")
    for linha in M_per:
        print(f"   [{linha[0]:8.3f} {linha[1]:8.3f} {linha[2]:8.3f} {linha[3]:8.3f}]")
    
    # ========================================
    # 6. PROJETAR VÉRTICES NO PLANO 2D
    # ========================================
    
    print("\n📍 PROJETANDO VÉRTICES...")
    print("   💡 Raios partem de cada vértice em direção a C")
    print("   💡 Intersecção com o plano define o ponto projetado")
    
    vertices_2d = projetar_objeto(vertices, M_per)
    print(f"   Projetados: {len(vertices_2d)} vértices")
    
    # Mostrar alguns vértices projetados
    print("\n   Exemplos (primeiros 4 vértices):")
    for i in range(min(4, len(vertices_2d))):
        print(f"   V{i}: 3D{vertices[i]} → 2D{vertices_2d[i]}")
    
    # ========================================
    # 7. TRANSFORMAR PARA VIEWPORT (TELA)
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
    # 8. ESTATÍSTICAS (DEBUG)
    # ========================================
    
    imprimir_estatisticas(vertices, vertices_2d, pontos_tela)
    
    # ========================================
    # 9. RENDERIZAÇÃO
    # ========================================
    
    print("\n🎨 RENDERIZANDO...")
    
    desenhar_wireframe(
        pontos_tela, 
        superficies, 
        largura_tela, 
        altura_tela,
        mostrar_vertices=True,
        titulo=f"Projeção Perspectiva Cônica - {nome_objeto.upper()}"
    )
    
    # Opcional: Salvar imagem
    # salvar_imagem(pontos_tela, superficies, "resultado.png", largura_tela, altura_tela)
    
    print("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
