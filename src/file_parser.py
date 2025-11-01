"""
file_parser.py
Parser para ler arquivos de objetos 3D no formato especificado.
"""

import numpy as np
import os


def ler_objeto_3d(caminho_arquivo):
    """
    Lê um arquivo de objeto 3D e retorna vértices e superfícies.
    
    Formato esperado:
        NV <número_de_vértices>
        <x1> <y1> <z1>
        <x2> <y2> <z2>
        ...
        NS <número_de_superfícies>
        <n_verts> <idx1> <idx2> ... <idxN>
        ...
    
    Args:
        caminho_arquivo: caminho para o arquivo .txt
    
    Returns:
        tuple: (vertices, superficies, nome_objeto)
            - vertices: array Nx3 com coordenadas dos vértices
            - superficies: lista de listas com índices dos vértices
            - nome_objeto: nome do arquivo sem extensão
    
    Raises:
        FileNotFoundError: se o arquivo não existir
        ValueError: se o formato do arquivo for inválido
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    
    nome_objeto = os.path.splitext(os.path.basename(caminho_arquivo))[0]
    vertices = []
    superficies = []
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        i = 0
        num_vertices = 0
        num_superficies = 0
        
        # Processar linha por linha
        while i < len(linhas):
            linha = linhas[i].strip()
            
            # Ignorar comentários e linhas vazias
            if not linha or linha.startswith('#'):
                i += 1
                continue
            
            partes = linha.split()
            
            # Ler número de vértices
            if partes[0] == 'NV':
                num_vertices = int(partes[1])
                i += 1
                
                # Ler os vértices
                vertices_lidos = 0
                while vertices_lidos < num_vertices and i < len(linhas):
                    linha_v = linhas[i].strip()
                    if linha_v and not linha_v.startswith('#'):
                        coords = linha_v.split()
                        if len(coords) >= 3:
                            x, y, z = float(coords[0]), float(coords[1]), float(coords[2])
                            vertices.append([x, y, z])
                            vertices_lidos += 1
                    i += 1
            
            # Ler número de superfícies
            elif partes[0] == 'NS':
                num_superficies = int(partes[1])
                i += 1
                
                # Ler as superfícies
                superficies_lidas = 0
                while superficies_lidas < num_superficies and i < len(linhas):
                    linha_s = linhas[i].strip()
                    if linha_s and not linha_s.startswith('#'):
                        dados = linha_s.split()
                        if len(dados) >= 2:
                            num_verts_face = int(dados[0])
                            indices = [int(dados[j]) for j in range(1, num_verts_face + 1)]
                            superficies.append(indices)
                            superficies_lidas += 1
                    i += 1
            
            else:
                i += 1
        
        # Validações
        if len(vertices) != num_vertices:
            raise ValueError(f"Esperados {num_vertices} vértices, encontrados {len(vertices)}")
        
        if len(superficies) != num_superficies:
            raise ValueError(f"Esperadas {num_superficies} superfícies, encontradas {len(superficies)}")
        
        # Converter para numpy array
        vertices_array = np.array(vertices, dtype=float)
        
        return vertices_array, superficies, nome_objeto
    
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo {caminho_arquivo}: {str(e)}")


def listar_objetos_disponiveis(diretorio_objetos):
    """
    Lista todos os arquivos .txt no diretório de objetos.
    
    Args:
        diretorio_objetos: caminho para o diretório com os objetos
    
    Returns:
        list: lista de caminhos para arquivos .txt
    """
    if not os.path.exists(diretorio_objetos):
        return []
    
    arquivos = []
    for arquivo in os.listdir(diretorio_objetos):
        if arquivo.endswith('.txt'):
            arquivos.append(os.path.join(diretorio_objetos, arquivo))
    
    return sorted(arquivos)


def imprimir_info_objeto(vertices, superficies, nome):
    """
    Imprime informações sobre o objeto carregado.
    
    Args:
        vertices: array de vértices
        superficies: lista de superfícies
        nome: nome do objeto
    """
    print(f"\n📦 Objeto carregado: {nome.upper()}")
    print(f"   Vértices: {len(vertices)}")
    print(f"   Superfícies: {len(superficies)}")
    
    # Bounding box
    if len(vertices) > 0:
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        print(f"   Limites X: [{min_coords[0]:.2f}, {max_coords[0]:.2f}]")
        print(f"   Limites Y: [{min_coords[1]:.2f}, {max_coords[1]:.2f}]")
        print(f"   Limites Z: [{min_coords[2]:.2f}, {max_coords[2]:.2f}]")
