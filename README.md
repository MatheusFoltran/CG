# 🎨 Sistema de Projeção Perspectiva

---

## 📋 Descrição

Sistema de visualização projetivo baseado em **perspectiva cônica**. Implementa a projeção de objetos 3D em um plano 2D, simulando a visão humana.

---

Nota rápida: este projeto suporta dois modos de renderização — o renderer padrão com `Matplotlib` (recomendado para geração de imagens estáticas e ambientes sem aceleração gráfica) e um renderer interativo acelerado por GPU via `pyglet` (OpenGL). Use `--opengl` para abrir a janela OpenGL interativa (veja exemplos abaixo).

---

## 🗂️ Estrutura do Projeto

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
   ⎣  nx      ny      nz        d   ⎦
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

## 🧪 Validação

Para verificar se está funcionando corretamente:

1. **Vetor Normal** - Deve ser perpendicular ao plano
2. **Matriz de Perspectiva** - Elementos devem seguir as fórmulas matemáticas
3. **Projeção** - Objetos mais distantes devem parecer menores
4. **Viewport** - Objeto deve estar centralizado na tela
5. **Pontos de Fuga** - Conferir logs para ver se os pontos de fuga fazem sentido geométrico

---

## 🐛 Troubleshooting

### Objeto não aparece na tela
- Verifique se o objeto está à frente do plano de projeção
- Ajuste a posição da câmera (C)

### Divisão por zero
- Verifique se w' ≠ 0 após a projeção
- Pontos no infinito são tratados como (0, 0)

### Objeto distorcido
- Verifique se o vetor normal está correto
- Confirme que os 3 pontos do plano não são colineares

---

## 🎓 Notas de Implementação

1. **Vetor Normal**: O cálculo usa `np.cross()` para garantir precisão.
2. **Transformação Viewport**: Implementação clara e robusta.
3. **Coordenadas Homogêneas**: Tratamento explícito de casos especiais (w=0).
4. **Pontos de Fuga**: Calculados e exibidos automaticamente no log.

---