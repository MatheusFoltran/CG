"""
main.py
Sistema completo de visualização com projeção perspectiva cônica.

COMO USAR:
    python main.py
"""

import argparse
import numpy as np
import os
from file_parser import ler_objeto_3d, imprimir_info_objeto, listar_objetos_disponiveis
from math_utils import calcular_vetor_normal
from projection import (
    calcular_parametros_d,
    criar_matriz_perspectiva,
    projetar_objeto,
    projetar_ponto,
    janela_para_viewport,
    calcular_pontos_de_fuga
)
from renderer import desenhar_wireframe, desenhar_wireframe_opengl, imprimir_estatisticas

# Variável global para controlar uso de OpenGL
USAR_OPENGL = False


def configurar_camera_e_plano():
    """
    Configura os parâmetros de visualização.
    
    Returns:
        tuple: (C, P1, P2, P3, R0)
    """
    print("\n" + "="*70)
    print("🎥 CONFIGURAÇÃO DE CÂMERA E PLANO DE PROJEÇÃO")
    print("="*70)
    
    # ============================================
    # CONFIGURAÇÃO PADRÃO - VISTA FRONTAL DO CUBO
    # ============================================
    # Ponto de vista (câmera)
    C = np.array([1.0, 1.0, 10.0])  # Câmera à frente do objeto
    
    # Plano de projeção (paralelo ao plano XY, em z=5)
    P1 = np.array([0.0, 0.0, 5.0])
    P2 = np.array([4.0, 0.0, 5.0])
    P3 = np.array([0.0, 4.0, 5.0])
    
    # Ponto sobre o plano (pode ser P1, P2 ou P3)
    R0 = P1
    
    print(f"\n📍 Ponto de Vista (C):      {C}")
    print(f"📐 Plano de Projeção:")
    print(f"   P1 = {P1}")
    print(f"   P2 = {P2}")
    print(f"   P3 = {P3}")
    print(f"   R0 = {R0}")
    
    return C, P1, P2, P3, R0


def configurar_viewport():
    """
    Configura os limites da viewport (tela).
    
    Returns:
        tuple: (u_min, u_max, v_min, v_max)
    """
    print("\n🖥️  CONFIGURAÇÃO DA VIEWPORT")
    
    # Resolução da tela (pixels)
    u_min = 0
    u_max = 800
    v_min = 0
    v_max = 600
    
    print(f"   Limites: u=[{u_min}, {u_max}], v=[{v_min}, {v_max}]")
    print(f"   Resolução: {u_max}x{v_max} pixels")
    
    return u_min, u_max, v_min, v_max


def processar_projecao_perspectiva(caminho_arquivo):
    """
    Pipeline completo de projeção perspectiva.
    
    Args:
        caminho_arquivo: caminho para o arquivo do objeto 3D
    """
    print("\n" + "="*70)
    print("🚀 SISTEMA DE VISUALIZAÇÃO COM PROJEÇÃO PERSPECTIVA CÔNICA")
    print("="*70)
    
    # ========================================
    # PASSO 1: Carregar objeto 3D
    # ========================================
    try:
        vertices, superficies, nome = ler_objeto_3d(caminho_arquivo)
        imprimir_info_objeto(vertices, superficies, nome)
    except Exception as e:
        print(f"\n❌ Erro ao carregar objeto: {e}")
        return
    
    # ========================================
    # PASSO 2: Configurar câmera e plano
    # ========================================
    C, P1, P2, P3, R0 = configurar_camera_e_plano()
    
    # ========================================
    # PASSO 3: Calcular vetor normal
    # ========================================
    print("\n" + "="*70)
    print("🧮 CÁLCULO DO VETOR NORMAL AO PLANO")
    print("="*70)
    
    try:
        N = calcular_vetor_normal(P1, P2, P3)
        print(f"\n✅ Vetor Normal N = {N}")
        print(f"   Componentes: Nx={N[0]:.4f}, Ny={N[1]:.4f}, Nz={N[2]:.4f}")
    except ValueError as e:
        print(f"\n❌ Erro: {e}")
        return
    
    # ========================================
    # PASSO 4: Calcular parâmetros d
    # ========================================
    print("\n" + "="*70)
    print("📐 CÁLCULO DOS PARÂMETROS d0, d1, d")
    print("="*70)
    
    d0, d1, d = calcular_parametros_d(C, R0, N)
    print(f"\n   d0 = R0 · N = {d0:.4f}")
    print(f"   d1 = C · N  = {d1:.4f}")
    print(f"   d  = d0 - d1 = {d:.4f}")
    
    if abs(d) < 1e-10:
        print("\n⚠️  AVISO: d ≈ 0. Câmera está muito próxima do plano!")
        print("   Isso pode causar distorções extremas na projeção.")
    
    # ========================================
    # PASSO 5: Criar matriz de perspectiva
    # ========================================
    print("\n" + "="*70)
    print("🔢 MATRIZ DE PROJEÇÃO PERSPECTIVA")
    print("="*70)
    
    M_per = criar_matriz_perspectiva(C, N, d0, d)
    print(f"\nM_per = ")
    print(M_per)

    pontos_fuga = calcular_pontos_de_fuga(C, N, R0)
    pontos_finitos = {k: v for k, v in pontos_fuga.items() if v is not None}
    print("\n📍 Pontos de fuga detectados:")
    if not pontos_finitos:
        print("   Nenhum ponto de fuga finito (plano paralelo aos eixos principais).")
    else:
        for eixo, ponto in pontos_fuga.items():
            if ponto is None:
                print(f"   {eixo}: ponto no infinito (retas paralelas ao plano)")
            else:
                fuga_2d = projetar_ponto(ponto, M_per)
                print(f"   {eixo}: 3D{ponto} → 2D{fuga_2d}")
    
    # ========================================
    # PASSO 6: Projetar objeto no plano
    # ========================================
    print("\n" + "="*70)
    print("📍 PROJEÇÃO DOS VÉRTICES NO PLANO")
    print("="*70)
    
    vertices_2d = projetar_objeto(vertices, M_per)
    print(f"\n✅ {len(vertices_2d)} vértices projetados com sucesso")
    print(f"   Exemplo - Vértice 0:")
    print(f"      3D: {vertices[0]}")
    print(f"      2D: {vertices_2d[0]}")
    
    # ========================================
    # PASSO 7: Transformar para viewport
    # ========================================
    print("\n" + "="*70)
    print("🖼️  TRANSFORMAÇÃO JANELA → VIEWPORT")
    print("="*70)
    
    u_min, u_max, v_min, v_max = configurar_viewport()
    pontos_tela = janela_para_viewport(
        vertices_2d, 
        u_min=u_min, 
        u_max=u_max, 
        v_min=v_min, 
        v_max=v_max
    )
    
    print(f"\n✅ Transformação concluída")
    print(f"   Exemplo - Vértice 0 na tela:")
    print(f"      Plano: {vertices_2d[0]}")
    print(f"      Tela:  {pontos_tela[0]} pixels")
    
    # ========================================
    # PASSO 8: Exibir estatísticas
    # ========================================
    imprimir_estatisticas(vertices, vertices_2d, pontos_tela)
    
    # ========================================
    # PASSO 9: Renderizar
    # ========================================
    print("\n" + "="*70)
    print("🎨 RENDERIZAÇÃO")
    print("="*70)
    print("\n   Abrindo janela de visualização...")
    
    titulo = f"Projeção Perspectiva - {nome.upper()}"
    
    # Escolher renderer baseado na configuração
    if USAR_OPENGL:
        desenhar_wireframe_opengl(
            pontos_tela, 
            superficies,
            largura=u_max,
            altura=v_max,
            mostrar_vertices=True,
            titulo=titulo + " [OpenGL]"
        )
    else:
        desenhar_wireframe(
            pontos_tela, 
            superficies,
            largura=u_max,
            altura=v_max,
            mostrar_vertices=True,
            titulo=titulo
        )
    
    print("\n✅ Visualização concluída!")
    print("="*70)


def menu_interativo(dir_objetos=None):
    """
    Menu interativo para escolher objeto e configurações.
    """
    print("\n" + "="*70)
    print("🎯 SISTEMA DE VISUALIZAÇÃO 3D - PROJEÇÃO PERSPECTIVA")
    print("="*70)
    
    # Local padrão da pasta 'objetos' (um nível acima de src)
    if dir_objetos is None:
        dir_atual = os.path.dirname(os.path.abspath(__file__))
        dir_objetos = os.path.join(os.path.dirname(dir_atual), 'objetos')

    while True:
        objetos = listar_objetos_disponiveis(dir_objetos)

        print("\n📁 Objetos disponíveis na pasta 'objetos/':")
        if not objetos:
            print("   (Nenhum arquivo .txt encontrado em 'objetos/')")
        else:
            for i, caminho in enumerate(objetos, start=1):
                nome = os.path.basename(caminho)
                print(f"   {i:2d} - {nome}")

        print("\n   Opções:")
        print("     [número] - Selecionar arquivo pelo índice")
        print("     [nome]   - Selecionar arquivo pelo nome (com ou sem .txt)")
        print("     r        - Recarregar lista")
        print("     q        - Sair")

        escolha = input("\n   Escolha um arquivo (índice/nome) ou opção: ").strip()
        if not escolha:
            print("   ⚠️  Entrada vazia. Tente novamente.")
            continue

        if escolha.lower() == 'q':
            print("\n👋 Até logo!")
            break

        if escolha.lower() == 'r':
            continue

        # Seleção por índice
        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(objetos):
                caminho = objetos[idx]
                processar_projecao_perspectiva(caminho)
            else:
                print("   ⚠️ Índice inválido. Tente novamente.")
            continue

        # Seleção por nome (com ou sem .txt)
        nome_input = escolha
        nome_ok = nome_input if nome_input.endswith('.txt') else nome_input + '.txt'
        encontrados = [p for p in objetos if os.path.basename(p).lower() in (nome_input.lower(), nome_ok.lower())]
        if encontrados:
            processar_projecao_perspectiva(encontrados[0])
            continue

        print("   ⚠️ Arquivo não encontrado na pasta 'objetos/'. Use o índice ou nome correto.")


def resolver_caminho_objeto(caminho, dir_objetos):
    """Resolve caminho informado pelo usuário considerando diretório padrão."""
    if os.path.isabs(caminho) and os.path.exists(caminho):
        return caminho

    candidato = os.path.join(dir_objetos, caminho)
    if os.path.exists(candidato):
        return candidato

    # Tenta adicionar extensão caso não tenha
    if not caminho.lower().endswith('.txt'):
        candidato = os.path.join(dir_objetos, caminho + '.txt')
        if os.path.exists(candidato):
            return candidato

    raise FileNotFoundError(f"Arquivo '{caminho}' não encontrado (diretório base: {dir_objetos})")


def listar_arquivos(dir_objetos):
    objetos = listar_objetos_disponiveis(dir_objetos)
    if not objetos:
        print("Nenhum arquivo .txt encontrado em", dir_objetos)
        return
    print("\nArquivos disponíveis:")
    for caminho in objetos:
        print(" •", os.path.basename(caminho))


def parse_args():
    parser = argparse.ArgumentParser(description="Sistema de projeção perspectiva cônica")
    parser.add_argument('-o', '--objeto', help='Caminho para o arquivo do objeto (.txt)')
    parser.add_argument('--objetos-dir', help="Diretório contendo arquivos .txt de objetos")
    parser.add_argument('--listar', action='store_true', help='Apenas listar objetos disponíveis e sair')
    parser.add_argument('--opengl', action='store_true', help='Usar renderização OpenGL (pyglet) em vez de Matplotlib')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    dir_padrao_objetos = os.path.join(os.path.dirname(dir_atual), 'objetos')
    dir_objetos = args.objetos_dir or dir_padrao_objetos

    # Configurar uso de OpenGL
    if args.opengl:
        USAR_OPENGL = True
        print("🎮 Modo OpenGL ativado")

    if args.listar:
        listar_arquivos(dir_objetos)
        raise SystemExit(0)

    if args.objeto:
        try:
            caminho = resolver_caminho_objeto(args.objeto, dir_objetos)
        except FileNotFoundError as exc:
            print(f"❌ {exc}")
            raise SystemExit(1)
        processar_projecao_perspectiva(caminho)
    else:
        menu_interativo(dir_objetos=dir_objetos)