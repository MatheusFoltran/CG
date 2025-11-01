"""
renderer.py
Módulo de visualização e renderização 2D.
"""

import matplotlib.pyplot as plt
import numpy as np


def desenhar_wireframe(pontos_tela, superficies, largura=800, altura=600, 
                       mostrar_vertices=True, titulo="Projeção Perspectiva"):
    """
    Desenha o objeto projetado em modo wireframe (aramado).
    
    Args:
        pontos_tela: array Nx2 com coordenadas (u, v) em pixels
        superficies: lista de listas com índices dos vértices de cada face
        largura: largura da viewport em pixels
        altura: altura da viewport em pixels
        mostrar_vertices: se True, desenha os vértices como pontos
        titulo: título da janela
    """
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Desenhar cada superfície (face)
    for i, superficie in enumerate(superficies):
        # Extrair pontos desta face
        try:
            pontos_face = [pontos_tela[idx] for idx in superficie]
            # Fechar o polígono (conectar último ao primeiro)
            pontos_face.append(pontos_face[0])
            
            xs = [p[0] for p in pontos_face]
            ys = [p[1] for p in pontos_face]
            
            # Desenhar arestas
            ax.plot(xs, ys, 'b-', linewidth=1.5, alpha=0.7)
            
        except IndexError as e:
            print(f"⚠️ Aviso: Superfície {i} contém índice inválido: {e}")
    
    # Desenhar vértices
    if mostrar_vertices:
        ax.plot(pontos_tela[:, 0], pontos_tela[:, 1], 'ro', 
                markersize=6, label='Vértices', zorder=5)
        
        # Numerar vértices (opcional, útil para debug)
        for i, (x, y) in enumerate(pontos_tela):
            ax.annotate(str(i), (x, y), xytext=(5, 5), 
                       textcoords='offset points', fontsize=8, color='red')
    
    # Configurações do gráfico
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.invert_yaxis()  # Eixo Y da tela cresce para baixo
    ax.set_aspect('equal')
    ax.set_title(titulo, fontsize=16, fontweight='bold')
    ax.set_xlabel('u (pixels)', fontsize=12)
    ax.set_ylabel('v (pixels)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend()
    
    plt.tight_layout()
    plt.show()


def salvar_imagem(pontos_tela, superficies, nome_arquivo, 
                  largura=800, altura=600, dpi=150):
    """
    Salva a visualização em um arquivo de imagem.
    
    Args:
        pontos_tela: array Nx2 com coordenadas na tela
        superficies: lista de superfícies
        nome_arquivo: caminho do arquivo (ex: "resultado.png")
        largura: largura da viewport
        altura: altura da viewport
        dpi: resolução da imagem
    """
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Desenhar superfícies
    for superficie in superficies:
        pontos_face = [pontos_tela[idx] for idx in superficie]
        pontos_face.append(pontos_face[0])
        
        xs = [p[0] for p in pontos_face]
        ys = [p[1] for p in pontos_face]
        
        ax.plot(xs, ys, 'b-', linewidth=1.5)
    
    # Desenhar vértices
    ax.plot(pontos_tela[:, 0], pontos_tela[:, 1], 'ro', markersize=6)
    
    # Configurações
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_title('Projeção Perspectiva', fontsize=16)
    ax.grid(True, alpha=0.3)
    
    # Salvar
    plt.savefig(nome_arquivo, dpi=dpi, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Imagem salva: {nome_arquivo}")


def imprimir_estatisticas(vertices_3d, vertices_2d, pontos_tela):
    """
    Imprime estatísticas úteis sobre a projeção (para debug).
    
    Args:
        vertices_3d: vértices originais 3D
        vertices_2d: vértices projetados no plano
        pontos_tela: coordenadas finais na tela
    """
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DA PROJEÇÃO")
    print("="*60)
    
    print(f"\n🔢 Número de vértices: {len(vertices_3d)}")
    
    print(f"\n📐 Limites 3D (objeto original):")
    print(f"   X: [{vertices_3d[:, 0].min():.2f}, {vertices_3d[:, 0].max():.2f}]")
    print(f"   Y: [{vertices_3d[:, 1].min():.2f}, {vertices_3d[:, 1].max():.2f}]")
    print(f"   Z: [{vertices_3d[:, 2].min():.2f}, {vertices_3d[:, 2].max():.2f}]")
    
    print(f"\n📏 Limites 2D (plano de projeção):")
    print(f"   XP: [{vertices_2d[:, 0].min():.2f}, {vertices_2d[:, 0].max():.2f}]")
    print(f"   YP: [{vertices_2d[:, 1].min():.2f}, {vertices_2d[:, 1].max():.2f}]")
    
    print(f"\n🖥️  Limites Tela (pixels):")
    print(f"   u: [{pontos_tela[:, 0].min():.1f}, {pontos_tela[:, 0].max():.1f}]")
    print(f"   v: [{pontos_tela[:, 1].min():.1f}, {pontos_tela[:, 1].max():.1f}]")
    
    print("\n" + "="*60)