# 🎨 Sistema de Projeção Perspectiva

---

## 📋 Descrição

Sistema de visualização projetivo baseado em **perspectiva cônica**. Implementa a projeção de objetos 3D em um plano 2D, simulando a visão humana.

---

## 🖼️ Modos de Renderização: Matplotlib vs Pyglet (OpenGL)

Este projeto oferece **dois modos de visualização** com resultados visualmente idênticos, mas propósitos diferentes:

| Característica | **Matplotlib** (padrão) | **Pyglet/OpenGL** (`--opengl`) |
|----------------|------------------------|-------------------------------|
| **Propósito** | Biblioteca científica para plotagem de gráficos e dados | Biblioteca de jogos/multimídia que usa OpenGL real |
| **Renderização** | Software (CPU) | Hardware acelerado (GPU) |
| **Janela** | Estática, ideal para exportar imagens | Interativa e redimensionável em tempo real |
| **Uso típico** | Gráficos científicos, papers, relatórios | Aplicações gráficas, jogos, simulações |
| **Performance** | Suficiente para wireframes simples | Mais eficiente para cenas complexas |

### Por que dois renderers?

- **Matplotlib** foi projetado para *plotar gráficos* (funções, histogramas, scatter plots). Usamos ele aqui porque é simples, já vem com NumPy/SciPy, e gera imagens de alta qualidade para documentação.

- **Pyglet** é um wrapper Python para **OpenGL**, a API padrão da indústria para renderização 3D em tempo real. Ele simula o pipeline gráfico que GPUs reais executam, oferecendo uma experiência mais próxima de como engines de jogos e softwares CAD funcionam.

> 💡 **Na prática**: Para este trabalho acadêmico, ambos produzem o **mesmo resultado visual** (wireframe 2D projetado). A diferença está na tecnologia subjacente — Matplotlib "desenha pixels em uma imagem", enquanto Pyglet "envia comandos para a GPU renderizar".

---

## 🗂️ Estrutura do Projeto

```bash
Trabalho - Computação Gráfica/
├── README.md
├── requirements.txt
├── objetos/
│   ├── cubo.txt
│   ├── paralelepipedo.txt
│   ├── piramide.txt
│   └── prisma_triangular.txt
└── src/
   ├── file_parser.py      # Leitura de arquivos de objetos 3D
   ├── math_utils.py       # Operações matemáticas (vetores, produto vetorial)
   ├── projection.py       # Lógica de projeção perspectiva
   ├── renderer.py         # Visualização 2D do resultado
   ├── main.py             # Programa principal (CLI/menu)
   └── __pycache__/
```
   
## 🚀 Como Executar

### 1️⃣ Instalação

```bash
1. Clonar o repositório

2. Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Execução

#### Modo Interativo (menu)

```bash
python src/main.py
```

#### Modo CLI (sem menu)

```bash
# Projetar diretamente um arquivo do diretório padrão
python src/main.py --objeto cubo.txt

# Projetar e abrir a janela OpenGL (interativo)
python src/main.py --objeto cubo.txt --opengl

# Projetar arquivo em outro diretório
python src/main.py --objeto caminho/para/objeto.txt

# Listar objetos disponíveis em um diretório específico
python src/main.py --listar --objetos-dir ./objetos
```

#### Opção rápida com Makefile

Se preferir, existe um `Makefile` na raiz que facilita executar as visualizações:

```bash
# Executa a visualização para `objetos/cubo.txt`
make cubo

# Ou passando a extensão
make cubo.txt

# Executa todas as visualizações listadas em `objetos/`
make all

# Passar o flag OpenGL (janela interativa) via variável `OPENGL`:
# Exemplo: executar a visualização em OpenGL
make cubo OPENGL=1

# Ou para executar todos em OpenGL:
make all OPENGL=1
```

**Saída:**
- Logs no terminal mostrando cada etapa do cálculo (vetor normal, parâmetros d, matriz, pontos de fuga, etc.)
- Janela gráfica com o objeto projetado

---

## 📐 Fundamentos Matemáticos

### Entrada de Dados

- **Ponto de Vista** C = (a, b, c) - Posição da câmera (único centro de projeção)
- **Plano de Projeção** - Definido por 3 pontos: P1, P2, P3
- **Objeto 3D** - Vértices e superfícies (faces)

### Etapas do Algoritmo

1. **Calcular Vetor Normal ao Plano**
   ```
   N = (P1-P2) × (P3-P2)
   ```

2. **Calcular Parâmetros d0, d1, d**
   ```
   d0 = R0 · N
   d1 = C · N
   d = d0 - d1
   ```

3. **Montar Matriz de Perspectiva 4×4**
   ```
   ⎡ d+a·nx   a·ny    a·nz    -a·d0 ⎤
   ⎢ b·nx   d+b·ny   b·nz     -b·d0 ⎥
   ⎢ c·nx    c·ny   d+c·nz    -c·d0 ⎥
   ⎣  nx      ny      nz        1   ⎦
   ```

4. **Projetar Vértices**
   ```
   P' = M_per · P  (coordenadas homogêneas)
   XC = x'/w', YC = y'/w'  (conversão para cartesianas)
   ```

5. **Transformação Janela-Viewport**
   - Mapeia coordenadas do plano para pixels da tela
   - Centraliza objeto mantendo proporções

### Pontos de Fuga

- O sistema calcula automaticamente os pontos de fuga para as direções X, Y e Z.
- Dependendo da orientação do plano de projeção em relação a cada eixo, podemos
  ter 0, 1, 2 ou 3 pontos de fuga finitos.
- Pontos paralelos ao plano produzem vanishing points no infinito (indicados no log).

---

## 📁 Descrição dos Módulos

### `file_parser.py`
Leitura e parsing dos arquivos de objetos 3D (.txt).
- `ler_objeto_3d()` - Carrega vértices e superfícies a partir de arquivo.

### `math_utils.py`
Funções matemáticas fundamentais:
- `produto_vetorial()` - Calcula v1 × v2
- `produto_escalar()` - Calcula v1 · v2
- `calcular_vetor_normal()` - Normal ao plano por 3 pontos

### `projection.py`
Núcleo do sistema de projeção:
- `calcular_parametros_d()` - Calcula d0, d1, d
- `criar_matriz_perspectiva()` - Monta matriz 4×4
- `projetar_ponto()` - Projeta um vértice 3D → 2D
- `projetar_objeto()` - Projeta todos os vértices
- `janela_para_viewport()` - Transforma para coordenadas da tela
- `calcular_pontos_de_fuga()` - Calcula pontos de fuga dos eixos principais

### `renderer.py`
Visualização gráfica:
- `desenhar_wireframe()` - Renderiza o objeto em modo aramado
- `salvar_imagem()` - Exporta resultado para arquivo

### `main.py`
Orquestra todo o pipeline:
1. Define dados de entrada (C, plano, objeto)
2. Calcula vetor normal
3. Calcula parâmetros d
4. Cria matriz de perspectiva
5. Projeta vértices
6. Transforma para viewport
7. Renderiza resultado
8. Mostra pontos de fuga dos eixos principais

---

## 🎯 Exemplos de Uso

### Trocar o Objeto

Use arquivos `.txt` em `objetos/` ou passe o caminho via CLI:

```bash
python src/main.py --objeto objetos/piramide.txt
```

### Mudar Posição da Câmera

Edite os parâmetros no menu interativo ou diretamente no código.


### Alterar Plano de Projeção

Edite os pontos do plano no menu ou código.

---

## 🔧 Dependências

- **Python** >= 3.8
- **NumPy** >= 1.24.0 - Operações matriciais
- **Matplotlib** >= 3.7.0 - Visualização
 - **pyglet** >= 2.0.0 - (opcional) Janela OpenGL para renderização interativa
 - **PyOpenGL, PyOpenGL_accelerate** - (opcional) Necessários apenas se for usar código GL em baixo nível / shaders

---

## 📝 Formato de Arquivos de Objetos

```
# cubo.txt
NV 8
0 0 0
2 0 0
2 2 0
0 2 0
0 0 2
2 0 2
2 2 2
0 2 2

NS 6
4 0 1 2 3
4 4 5 6 7
4 0 1 5 4
4 2 3 7 6
4 0 3 7 4
4 1 2 6 5
```

- `NV` = Número de Vértices
- Seguido das coordenadas (x, y, z)
- `NS` = Número de Superfícies
- Cada linha: número de vértices + índices dos vértices

---
