"""
renderer.py
Módulo de visualização e renderização 2D.
Suporta renderização com Matplotlib (padrão) ou OpenGL (via pyglet 2.x).
"""

import matplotlib.pyplot as plt
import numpy as np

# ============================================================================
# RENDERER OPENGL (pyglet 2.x)
# ============================================================================

try:
    import pyglet
    from pyglet import shapes
    OPENGL_DISPONIVEL = True
except ImportError:
    OPENGL_DISPONIVEL = False


def desenhar_wireframe_opengl(pontos_tela, superficies, largura=800, altura=600,
                               mostrar_vertices=True, titulo="Projeção Perspectiva - OpenGL",
                               vertices_3d=None, matriz_perspectiva=None):
    """
    Desenha o objeto projetado em modo wireframe usando OpenGL (pyglet 2.x).
    Responsivo: escala automaticamente quando a janela é redimensionada.
    O objeto é automaticamente redimensionado para caber na área de visualização.
    
    Args:
        pontos_tela: array Nx2 com coordenadas (u, v) em pixels
        superficies: lista de listas com índices dos vértices de cada face
        largura: largura da viewport em pixels
        altura: altura da viewport em pixels
        mostrar_vertices: se True, desenha os vértices como pontos
        titulo: título da janela
        vertices_3d: array Nx3 com coordenadas 3D originais (para exibir info)
        matriz_perspectiva: matriz de projeção (para projetar eixos 3D)
    """
    if not OPENGL_DISPONIVEL:
        print("⚠️  OpenGL não disponível. Instale com: pip install pyglet")
        print("    Usando Matplotlib como fallback...")
        desenhar_wireframe(pontos_tela, superficies, largura, altura, mostrar_vertices, titulo)
        return

    # Calcular bounding box dos pontos do objeto
    u_min_obj = pontos_tela[:, 0].min()
    u_max_obj = pontos_tela[:, 0].max()
    v_min_obj = pontos_tela[:, 1].min()
    v_max_obj = pontos_tela[:, 1].max()
    
    obj_largura = u_max_obj - u_min_obj
    obj_altura = v_max_obj - v_min_obj
    
    # Centro do objeto
    centro_u = (u_min_obj + u_max_obj) / 2
    centro_v = (v_min_obj + v_max_obj) / 2

    print(f"\n   Debug - Renderização OpenGL:")
    print(f"   Pontos na tela: {len(pontos_tela)}")
    print(f"   Superfícies: {len(superficies)}")
    print(f"   Bounding box objeto: u=[{u_min_obj:.1f}, {u_max_obj:.1f}], v=[{v_min_obj:.1f}, {v_max_obj:.1f}]")
    print(f"   Tamanho objeto: {obj_largura:.1f} x {obj_altura:.1f}")
    print(f"   Centro objeto: ({centro_u:.1f}, {centro_v:.1f})")

    # Criar janela pyglet (centralizada na tela)
    window = pyglet.window.Window(width=largura, height=altura, caption=titulo, resizable=True)
    
    # Centralizar janela na tela
    try:
        screen = window.display.get_default_screen()
        pos_x = (screen.width - largura) // 2
        pos_y = (screen.height - altura) // 2
        window.set_location(pos_x, pos_y)
    except Exception:
        pass  # Se não conseguir centralizar, continua normalmente
    
    # Margem fixa em pixels (será escalada com a janela)
    MARGEM_BASE = 80
    
    # Estado do desenho
    estado = {
        'win_escala': 1.0,  # Escala da janela relativa ao tamanho inicial
    }
    
    def calcular_transformacao_objeto(area_w, area_h):
        """
        Calcula a transformação para que o objeto caiba na área de desenho.
        Retorna: escala, offset_x, offset_y para centralizar o objeto.
        """
        # Escala para caber o objeto na área (com margem interna)
        margem_interna = 20
        area_util_w = area_w - 2 * margem_interna
        area_util_h = area_h - 2 * margem_interna
        
        if obj_largura > 0 and obj_altura > 0:
            escala_x = area_util_w / obj_largura
            escala_y = area_util_h / obj_altura
            escala_obj = min(escala_x, escala_y)
        else:
            escala_obj = 1.0
        
        # Tamanho do objeto escalado
        obj_w_escalado = obj_largura * escala_obj
        obj_h_escalado = obj_altura * escala_obj
        
        # Offset para centralizar
        offset_x = (area_w - obj_w_escalado) / 2
        offset_y = (area_h - obj_h_escalado) / 2
        
        return escala_obj, offset_x, offset_y
    
    def transformar_ponto_objeto(x, y, area_x, area_y, escala_obj, offset_x, offset_y):
        """Transforma coordenadas do objeto para coordenadas da janela."""
        # Normalizar para origem do objeto
        x_norm = x - u_min_obj
        y_norm = y - v_min_obj
        
        # Aplicar escala do objeto
        x_esc = x_norm * escala_obj
        y_esc = y_norm * escala_obj
        
        # Aplicar offset para centralizar + posição da área
        # y em tela cresce para baixo, em OpenGL para cima
        x_final = area_x + offset_x + x_esc
        y_final = area_y + offset_y + (obj_altura * escala_obj - y_esc)  # Inverter Y
        
        return x_final, y_final

    @window.event
    def on_draw():
        window.clear()
        pyglet.gl.glClearColor(0.95, 0.95, 0.95, 1.0)
        
        win_w = window.width
        win_h = window.height
        
        # Escala da janela
        win_escala = min(win_w / largura, win_h / altura)
        estado['win_escala'] = win_escala
        
        # Margem escalada
        margem = MARGEM_BASE * win_escala
        
        # ========================================
        # ÁREA DE DESENHO (o "plano de projeção")
        # ========================================
        area_x = margem
        area_y = margem
        area_w = win_w - 2 * margem
        area_h = win_h - 2 * margem - 30 * win_escala  # Espaço para título
        
        # Fundo branco da área
        fundo = shapes.Rectangle(area_x, area_y, area_w, area_h, color=(255, 255, 255))
        fundo.draw()
        
        # Borda da área
        borda = shapes.BorderedRectangle(area_x, area_y, area_w, area_h,
                                        border=2, color=(255, 255, 255),
                                        border_color=(100, 100, 100))
        borda.draw()
        
        # ========================================
        # CALCULAR TRANSFORMAÇÃO DO OBJETO (precisa antes dos eixos)
        # ========================================
        escala_obj, off_x, off_y = calcular_transformacao_objeto(area_w, area_h)
        
        # ========================================
        # EIXOS COM VALORES (régua) - baseados nas coordenadas do objeto
        # ========================================
        font_size_tick = max(8, int(9 * win_escala))
        tick_size = 6 * win_escala
        
        # Calcular intervalo dos ticks baseado no tamanho do objeto
        max_dim = max(obj_largura, obj_altura)
        if max_dim > 500:
            intervalo_tick = 100
        elif max_dim > 200:
            intervalo_tick = 50
        elif max_dim > 50:
            intervalo_tick = 20
        else:
            intervalo_tick = 10
        
        # --- EIXO HORIZONTAL (u) - embaixo da área ---
        # Linha do eixo
        eixo_u_linha = shapes.Line(area_x, area_y - 2, area_x + area_w, area_y - 2,
                                   thickness=2, color=(80, 80, 80))
        eixo_u_linha.draw()
        
        # Ticks e valores no eixo U
        u_tick_start = int(u_min_obj / intervalo_tick) * intervalo_tick
        for val in range(u_tick_start, int(u_max_obj) + intervalo_tick + 1, intervalo_tick):
            if val < u_min_obj or val > u_max_obj + 1:
                continue
            x_tick, _ = transformar_ponto_objeto(val, v_min_obj, area_x, area_y, escala_obj, off_x, off_y)
            if area_x - 5 <= x_tick <= area_x + area_w + 5:
                # Tick
                tick = shapes.Line(x_tick, area_y - 2, x_tick, area_y - 2 - tick_size,
                                  thickness=1, color=(80, 80, 80))
                tick.draw()
                # Valor
                # posicionar o label mais abaixo para que não seja coberto pelo eixo/ticks
                lbl = pyglet.text.Label(str(int(val)), font_name='Arial', font_size=font_size_tick,
                                       x=x_tick, y=area_y - tick_size - 18 * win_escala,
                                       anchor_x='center', anchor_y='top',
                                       color=(60, 60, 60, 255))
                lbl.draw()
        
        # Label do eixo U
        # afastar o label do eixo U para baixo para não sobrepor os ticks
        label_u = pyglet.text.Label('u (pixels)', font_name='Arial', font_size=max(9, int(10 * win_escala)),
                       x=area_x + area_w / 2, y=area_y - tick_size - 40 * win_escala,
                       anchor_x='center', color=(50, 50, 50, 255))
        label_u.draw()
        
        # --- EIXO VERTICAL (v) - à esquerda da área ---
        # Linha do eixo
        eixo_v_linha = shapes.Line(area_x - 2, area_y, area_x - 2, area_y + area_h,
                                   thickness=2, color=(80, 80, 80))
        eixo_v_linha.draw()
        
        # Ticks e valores no eixo V
        v_tick_start = int(v_min_obj / intervalo_tick) * intervalo_tick
        for val in range(v_tick_start, int(v_max_obj) + intervalo_tick + 1, intervalo_tick):
            if val < v_min_obj or val > v_max_obj + 1:
                continue
            _, y_tick = transformar_ponto_objeto(u_min_obj, val, area_x, area_y, escala_obj, off_x, off_y)
            if area_y - 5 <= y_tick <= area_y + area_h + 5:
                # Tick
                tick = shapes.Line(area_x - 2, y_tick, area_x - 2 - tick_size, y_tick,
                                  thickness=1, color=(80, 80, 80))
                tick.draw()
                # Valor
                lbl = pyglet.text.Label(str(int(val)), font_name='Arial', font_size=font_size_tick,
                                       x=area_x - tick_size - 5 * win_escala, y=y_tick,
                                       anchor_x='right', anchor_y='center',
                                       color=(60, 60, 60, 255))
                lbl.draw()
        
        # Label do eixo V
        label_v = pyglet.text.Label('v (pixels)', font_name='Arial', font_size=max(9, int(10 * win_escala)),
                                   x=area_x - tick_size - 35 * win_escala, y=area_y + area_h / 2,
                                   anchor_x='center', anchor_y='center',
                                   rotation=90, color=(50, 50, 50, 255))
        label_v.draw()
        
        # ========================================
        # EIXOS 3D NO CANTO (X vermelho, Y verde, Z azul)
        # ========================================
        tamanho_eixo = 60 * win_escala
        origem_3d_x = area_x + 60 * win_escala
        origem_3d_y = area_y + area_h - 90 * win_escala  # Canto superior esquerdo
        
        # Eixo X (vermelho) - horizontal para direita
        eixo_x = shapes.Line(origem_3d_x, origem_3d_y, 
                            origem_3d_x + tamanho_eixo, origem_3d_y,
                            thickness=3, color=(220, 50, 50))
        eixo_x.draw()
        
        # Eixo Y (verde) - vertical para cima
        eixo_y = shapes.Line(origem_3d_x, origem_3d_y,
                            origem_3d_x, origem_3d_y + tamanho_eixo * 0.7,
                            thickness=3, color=(50, 180, 50))
        eixo_y.draw()
        
        # Eixo Z (azul) - diagonal para baixo-esquerda (profundidade)
        eixo_z = shapes.Line(origem_3d_x, origem_3d_y,
                            origem_3d_x - tamanho_eixo * 0.5, origem_3d_y - tamanho_eixo * 0.5,
                            thickness=3, color=(50, 50, 220))
        eixo_z.draw()
        
        # Labels dos eixos 3D
        font_size_eixo = max(10, int(12 * win_escala))
        label_x = pyglet.text.Label('X', font_name='Arial', font_size=font_size_eixo,
                                    x=origem_3d_x + tamanho_eixo + 5, y=origem_3d_y - 5,
                                    color=(220, 50, 50, 255))
        label_y = pyglet.text.Label('Y', font_name='Arial', font_size=font_size_eixo,
                                    x=origem_3d_x - 5, y=origem_3d_y + tamanho_eixo * 0.7 + 5,
                                    color=(50, 180, 50, 255))
        label_z = pyglet.text.Label('Z', font_name='Arial', font_size=font_size_eixo,
                                    x=origem_3d_x - tamanho_eixo * 0.5 - 18, 
                                    y=origem_3d_y - tamanho_eixo * 0.5 - 5,
                                    color=(50, 50, 220, 255))
        label_x.draw()
        label_y.draw()
        label_z.draw()
        
        # Título do sistema de eixos
        label_eixos = pyglet.text.Label('Eixos 3D', font_name='Arial', font_size=max(8, int(9 * win_escala)),
                                       x=origem_3d_x, y=origem_3d_y + tamanho_eixo * 0.7 + 25,
                                       anchor_x='center', color=(80, 80, 80, 255))
        label_eixos.draw()
        
        # ========================================
        # GRADE DE FUNDO (usa mesmo intervalo dos eixos)
        # ========================================
        grade_batch = pyglet.graphics.Batch()
        grade_elementos = []
        
        # Usar o mesmo intervalo dos ticks para a grade
        intervalo_grade = intervalo_tick
        
        # Linhas verticais
        x_inicio = int(u_min_obj / intervalo_grade) * intervalo_grade
        for val in range(x_inicio, int(u_max_obj) + intervalo_grade, intervalo_grade):
            x, y1 = transformar_ponto_objeto(val, v_min_obj, area_x, area_y, escala_obj, off_x, off_y)
            _, y2 = transformar_ponto_objeto(val, v_max_obj, area_x, area_y, escala_obj, off_x, off_y)
            if area_x <= x <= area_x + area_w:
                linha = shapes.Line(x, max(y1, area_y), x, min(y2, area_y + area_h),
                                   thickness=1, color=(230, 230, 230), batch=grade_batch)
                grade_elementos.append(linha)
        
        # Linhas horizontais
        y_inicio = int(v_min_obj / intervalo_grade) * intervalo_grade
        for val in range(y_inicio, int(v_max_obj) + intervalo_grade, intervalo_grade):
            x1, y = transformar_ponto_objeto(u_min_obj, val, area_x, area_y, escala_obj, off_x, off_y)
            x2, _ = transformar_ponto_objeto(u_max_obj, val, area_x, area_y, escala_obj, off_x, off_y)
            if area_y <= y <= area_y + area_h:
                linha = shapes.Line(max(x1, area_x), y, min(x2, area_x + area_w), y,
                                   thickness=1, color=(230, 230, 230), batch=grade_batch)
                grade_elementos.append(linha)
        
        grade_batch.draw()
        
        # ========================================
        # OBJETO (arestas)
        # ========================================
        objeto_batch = pyglet.graphics.Batch()
        linhas_obj = []
        
        for superficie in superficies:
            n = len(superficie)
            for i in range(n):
                idx1 = superficie[i]
                idx2 = superficie[(i + 1) % n]
                try:
                    x1, y1 = pontos_tela[idx1]
                    x2, y2 = pontos_tela[idx2]
                    # Transformar para coordenadas da janela
                    x1_t, y1_t = transformar_ponto_objeto(x1, y1, area_x, area_y, escala_obj, off_x, off_y)
                    x2_t, y2_t = transformar_ponto_objeto(x2, y2, area_x, area_y, escala_obj, off_x, off_y)
                    linha = shapes.Line(x1_t, y1_t, x2_t, y2_t,
                                       thickness=2, color=(0, 50, 200), batch=objeto_batch)
                    linhas_obj.append(linha)
                except IndexError:
                    pass
        
        objeto_batch.draw()
        
        # ========================================
        # VÉRTICES (círculos e labels)
        # ========================================
        if mostrar_vertices:
            for i, (x, y) in enumerate(pontos_tela):
                x_t, y_t = transformar_ponto_objeto(x, y, area_x, area_y, escala_obj, off_x, off_y)
                
                # Verificar se está dentro da área
                if area_x <= x_t <= area_x + area_w and area_y <= y_t <= area_y + area_h:
                    raio = max(4, 5 * win_escala)
                    circulo = shapes.Circle(x_t, y_t, radius=raio, color=(200, 0, 0))
                    circulo.draw()
                    
                    # Label com índice do vértice
                    font_size = max(8, int(9 * win_escala))
                    label = pyglet.text.Label(str(i), font_name='Arial', font_size=font_size,
                                             x=x_t + 8 * win_escala, y=y_t + 8 * win_escala,
                                             color=(180, 0, 0, 255))
                    label.draw()
        
        # ========================================
        # INFORMAÇÕES DO OBJETO
        # ========================================
        font_size_info = max(8, int(9 * win_escala))
        info_text = f'Escala: {escala_obj:.2f}x | Objeto: {obj_largura:.0f}x{obj_altura:.0f} px'
        info_label = pyglet.text.Label(info_text, font_name='Arial', font_size=font_size_info,
                                      x=area_x + area_w - 10, y=area_y + 10,
                                      anchor_x='right', color=(120, 120, 120, 255))
        info_label.draw()
        
        # ========================================
        # TÍTULO
        # ========================================
        font_size_titulo = max(12, int(14 * win_escala))
        titulo_label = pyglet.text.Label(titulo, font_name='Arial', font_size=font_size_titulo,
                                        x=win_w // 2, y=win_h - 25 * win_escala,
                                        anchor_x='center', color=(50, 50, 50, 255))
        titulo_label.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE or symbol == pyglet.window.key.Q:
            window.close()

    print("\n   🎮 Controles OpenGL:")
    print("      ESC ou Q - Fechar janela")
    print("      Redimensione a janela livremente")

    pyglet.app.run()


# ============================================================================
# RENDERER MATPLOTLIB
# ============================================================================
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
    print(f"\n   Debug - Renderização:")
    print(f"   Pontos na tela: {len(pontos_tela)}")
    print(f"   Superfícies: {len(superficies)}")
    print(f"   Limites u: [{pontos_tela[:, 0].min():.1f}, {pontos_tela[:, 0].max():.1f}]")
    print(f"   Limites v: [{pontos_tela[:, 1].min():.1f}, {pontos_tela[:, 1].max():.1f}]")
    
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Centralizar janela Matplotlib na tela
    try:
        # Funciona com backend TkAgg (padrão no Windows)
        mng = plt.get_current_fig_manager()
        # Obter tamanho da tela
        fig_width, fig_height = fig.get_size_inches() * fig.dpi
        screen_width = mng.window.winfo_screenwidth()
        screen_height = mng.window.winfo_screenheight()
        x = int((screen_width - fig_width) // 2)
        y = int((screen_height - fig_height) // 2)
        mng.window.geometry(f"+{x}+{y}")
    except Exception:
        pass  # Se não conseguir centralizar, continua normalmente
    
    arestas_desenhadas = 0
    
    # Desenhar cada superfície (face)
    for i, superficie in enumerate(superficies):
        # Extrair pontos desta face
        try:
            pontos_face = [pontos_tela[idx] for idx in superficie]
            # Fechar o polígono (conectar último ao primeiro)
            pontos_face.append(pontos_face[0])
            
            xs = [p[0] for p in pontos_face]
            ys = [p[1] for p in pontos_face]
            
            # Desenhar arestas com cores alternadas para melhor visualização
            cor = 'blue' if i % 2 == 0 else 'darkblue'
            ax.plot(xs, ys, color=cor, linewidth=2, alpha=0.8, solid_capstyle='round')
            arestas_desenhadas += len(xs) - 1
            
        except IndexError as e:
            print(f"⚠️ Aviso: Superfície {i} contém índice inválido: {e}")
    
    print(f"   Arestas desenhadas: {arestas_desenhadas}")
    
    # Desenhar vértices
    if mostrar_vertices:
        ax.plot(pontos_tela[:, 0], pontos_tela[:, 1], 'ro', 
                markersize=8, label='Vértices', zorder=5, markeredgecolor='darkred', markeredgewidth=1)
        
        # Numerar vértices (opcional, útil para debug)
        for i, (x, y) in enumerate(pontos_tela):
            ax.annotate(str(i), (x, y), xytext=(7, 7), 
                       textcoords='offset points', fontsize=10, color='red', 
                       fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', 
                       facecolor='white', edgecolor='red', alpha=0.7))
    
    # Configurações do gráfico
    ax.set_xlim(0, largura)
    ax.set_ylim(0, altura)
    ax.invert_yaxis()  # Eixo Y da tela cresce para baixo
    ax.set_aspect('equal')
    ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('u (pixels)', fontsize=12)
    ax.set_ylabel('v (pixels)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.legend(fontsize=10)
    
    # Adicionar fundo cinza claro
    ax.set_facecolor('#f5f5f5')
    
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