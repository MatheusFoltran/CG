import matplotlib.pyplot as plt

def desenhar_wireframe(pontos_tela, superficies, largura=800, altura=600):
    """
    Desenha o objeto em wireframe (só as arestas).
    
    pontos_tela: array Nx2 com coordenadas (u, v) na tela
    superficies: lista de listas com índices dos vértices de cada face
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Desenhar cada superfície (face)
    for superficie in superficies:
        # Pega os pontos desta face
        pontos_face = [pontos_tela[i] for i in superficie]
        # Fecha o polígono
        pontos_face.append(pontos_face[0])
        
        xs = [p[0] for p in pontos_face]
        ys = [p[1] for p in pontos_face]
        
        # Desenha as arestas
        ax.plot(xs, ys, 'b-', linewidth=1.5)
    
    # Desenhar os vértices (opcional, fica bonito)
    ax.plot(pontos_tela[:, 0], pontos_tela[:, 1], 'ro', markersize=6)
    
    # Configurações da tela
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.invert_yaxis()  # Inverte Y (tela começa em cima)
    ax.set_aspect('equal')
    ax.set_title('Projeção Perspectiva', fontsize=14)
    ax.set_xlabel('u (pixels)')
    ax.set_ylabel('v (pixels)')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def salvar_imagem(pontos_tela, superficies, nome_arquivo, largura=800, altura=600):
    """Salva a visualização em arquivo (PNG, JPG, etc)"""
    fig, ax = plt.subplots(figsize=(10, 7))
    
    for superficie in superficies:
        pontos_face = [pontos_tela[i] for i in superficie]
        pontos_face.append(pontos_face[0])
        xs = [p[0] for p in pontos_face]
        ys = [p[1] for p in pontos_face]
        ax.plot(xs, ys, 'b-', linewidth=1.5)
    
    ax.plot(pontos_tela[:, 0], pontos_tela[:, 1], 'ro', markersize=6)
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    plt.savefig(nome_arquivo, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Imagem salva em: {nome_arquivo}")