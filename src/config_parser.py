"""
config_parser.py
Parser para arquivos de configuração de câmera e plano de projeção.
"""

import numpy as np
import os


def ler_configuracao_camera(caminho_arquivo):
    """
    Lê configuração de câmera e plano de projeção de um arquivo.
    
    Formato esperado:
        # Comentários começam com #
        CAMERA <x> <y> <z>
        PLANO_P1 <x> <y> <z>
        PLANO_P2 <x> <y> <z>
        PLANO_P3 <x> <y> <z>
        VIEWPORT <largura> <altura>  # opcional
    
    Args:
        caminho_arquivo: caminho para o arquivo .txt de configuração
    
    Returns:
        dict: dicionário com configurações
            {
                'camera': np.array([x, y, z]),
                'plano_p1': np.array([x, y, z]),
                'plano_p2': np.array([x, y, z]),
                'plano_p3': np.array([x, y, z]),
                'viewport': (largura, altura)  # opcional
            }
    
    Raises:
        FileNotFoundError: se o arquivo não existir
        ValueError: se o formato for inválido
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {caminho_arquivo}")
    
    config = {
        'camera': None,
        'plano_p1': None,
        'plano_p2': None,
        'plano_p3': None,
        'viewport': None
    }
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                
                # Ignorar comentários e linhas vazias
                if not linha or linha.startswith('#'):
                    continue
                
                partes = linha.split()
                if len(partes) < 2:
                    continue
                
                comando = partes[0].upper()
                
                if comando == 'CAMERA':
                    if len(partes) >= 4:
                        config['camera'] = np.array([
                            float(partes[1]),
                            float(partes[2]),
                            float(partes[3])
                        ])
                
                elif comando == 'PLANO_P1':
                    if len(partes) >= 4:
                        config['plano_p1'] = np.array([
                            float(partes[1]),
                            float(partes[2]),
                            float(partes[3])
                        ])
                
                elif comando == 'PLANO_P2':
                    if len(partes) >= 4:
                        config['plano_p2'] = np.array([
                            float(partes[1]),
                            float(partes[2]),
                            float(partes[3])
                        ])
                
                elif comando == 'PLANO_P3':
                    if len(partes) >= 4:
                        config['plano_p3'] = np.array([
                            float(partes[1]),
                            float(partes[2]),
                            float(partes[3])
                        ])
                
                elif comando == 'VIEWPORT':
                    if len(partes) >= 3:
                        config['viewport'] = (int(partes[1]), int(partes[2]))
        
        # Validar configurações obrigatórias
        if config['camera'] is None:
            raise ValueError("CAMERA não definida no arquivo de configuração")
        if config['plano_p1'] is None or config['plano_p2'] is None or config['plano_p3'] is None:
            raise ValueError("Plano de projeção incompleto (faltam P1, P2 ou P3)")
        
        return config
    
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo de configuração {caminho_arquivo}: {str(e)}")


def gerar_configuracao_automatica(vertices, modo='frontal'):
    """
    Gera configuração automática de câmera e plano baseada no objeto.
    
    Args:
        vertices: array Nx3 com vértices do objeto
        modo: 'frontal', 'lateral', 'superior', 'isometrica'
    
    Returns:
        dict: configuração automática
    """
    centro_objeto = vertices.mean(axis=0)
    bbox_min = vertices.min(axis=0)
    bbox_max = vertices.max(axis=0)
    tamanho_objeto = bbox_max - bbox_min
    
    # Distância da câmera
    distancia = max(tamanho_objeto) * 3
    
    # Tamanho do plano
    tam_plano = max(tamanho_objeto) * 2
    
    if modo == 'frontal':
        # Câmera atrás do objeto (eixo +Z)
        camera = centro_objeto + np.array([0, 0, distancia])
        
        # Plano XY perpendicular a Z (além do objeto, oposto à câmera)
        z_plano = centro_objeto[2] - distancia * 0.5
        plano_p1 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p2 = np.array([centro_objeto[0] + tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p3 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] + tam_plano, z_plano])
    
    elif modo == 'lateral':
        # Câmera à direita e um pouco atrás (vista 3/4)
        camera = centro_objeto + np.array([distancia * 0.8, 0, distancia * 0.5])
        
        # Plano perpendicular à direção da câmera
        z_plano = centro_objeto[2] - distancia * 0.5
        plano_p1 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p2 = np.array([centro_objeto[0] + tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p3 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] + tam_plano, z_plano])
    
    elif modo == 'superior':
        # Câmera acima e um pouco atrás (vista 3/4 de cima)
        camera = centro_objeto + np.array([0, distancia * 0.8, distancia * 0.5])
        
        # Plano perpendicular à direção da câmera
        z_plano = centro_objeto[2] - distancia * 0.5
        plano_p1 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p2 = np.array([centro_objeto[0] + tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p3 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] + tam_plano, z_plano])
    
    elif modo == 'isometrica':
        # Câmera em diagonal (visão isométrica aproximada)
        camera = centro_objeto + np.array([distancia * 0.7, distancia * 0.7, distancia * 0.7])
        
        # Plano perpendicular à direção da câmera (além do objeto)
        z_plano = centro_objeto[2] - distancia * 0.5
        plano_p1 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p2 = np.array([centro_objeto[0] + tam_plano, centro_objeto[1] - tam_plano, z_plano])
        plano_p3 = np.array([centro_objeto[0] - tam_plano, centro_objeto[1] + tam_plano, z_plano])
    
    else:
        # Default: frontal
        return gerar_configuracao_automatica(vertices, 'frontal')
    
    return {
        'camera': camera,
        'plano_p1': plano_p1,
        'plano_p2': plano_p2,
        'plano_p3': plano_p3,
        'viewport': (800, 600)
    }


def imprimir_configuracao(config):
    """
    Imprime informações da configuração.
    
    Args:
        config: dicionário com configurações
    """
    print(f"   Câmera (C): {config['camera']}")
    print(f"   Plano P1: {config['plano_p1']}")
    print(f"   Plano P2: {config['plano_p2']}")
    print(f"   Plano P3: {config['plano_p3']}")
    if config['viewport']:
        print(f"   Viewport: {config['viewport'][0]}×{config['viewport'][1]} pixels")
