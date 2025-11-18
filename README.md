# 🎨 Sistema de Projeção Perspectiva

---

## 📋 Descrição

Sistema de visualização projetivo baseado em **perspectiva cônica**. Implementa a projeção de objetos 3D em um plano 2D, simulando a visão humana.

---

## 🗂️ Estrutura do Projeto

```
Trabalho/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── main.py            # Programa principal
│   ├── file_parser.py     # Parser de objetos 3D
│   ├── config_parser.py   # Configurações de câmera/plano
│   ├── projection.py      # Lógica de projeção perspectiva
│   ├── math_utils.py      # Operações matemáticas
│   └── renderer.py        # Visualização 2D
│
└── objetos/
    ├── cubo.txt                  # Objeto: Cubo
    ├── piramide.txt              # Objeto: Pirâmide
    └── COMO_CRIAR_CONFIGS.txt    # Guia para configs personalizadas
```

---

## 🚀 Como Executar

### 1️⃣ Instalação

```bash
# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Modos de Execução

**Modo 1: Automático com Ângulos Pré-definidos** ⭐ (RECOMENDADO)
```bash
cd src

# Visão frontal (padrão)
python main.py ../objetos/cubo.txt --modo frontal

# Visão lateral (câmera à direita)
python main.py ../objetos/cubo.txt --modo lateral

# Visão superior (câmera acima)
python main.py ../objetos/cubo.txt --modo superior

# Visão isométrica (câmera em diagonal) - MELHOR!
python main.py ../objetos/cubo.txt --modo isometrica
```
✅ Funciona para **qualquer objeto**
✅ Calcula posições automaticamente
✅ Adapta-se ao tamanho do objeto

**Modo 2: Automático Simples**
```bash
cd src
python main.py ../objetos/cubo.txt
python main.py ../objetos/piramide.txt
```
Usa configuração automática padrão (frontal).

**Modo 3: Com Arquivo de Configuração Personalizado** (avançado)
```bash
cd src
python main.py ../objetos/cubo.txt ../objetos/minha_config.txt
```
Para controle total da câmera e plano.
Veja `objetos/COMO_CRIAR_CONFIGS.txt` para detalhes.

**Modo 4: Seleção Interativa**
```bash
cd src
python main.py
```
Escolhe o objeto de uma lista.

**Saída:**
- Logs no terminal mostrando cada etapa do cálculo
- Janela gráfica com o objeto projetado em perspectiva cônica

---

## 📝 Formatos de Arquivo

### Arquivo de Objeto (.txt)

```
# Comentários começam com #

NV <número_de_vértices>
<x1> <y1> <z1>
<x2> <y2> <z2>
...

NS <número_de_superfícies>
<n_verts> <idx1> <idx2> ... <idxN>
...
```

### Arquivo de Configuração Personalizado (.txt) - OPCIONAL

⚠️ **Use apenas quando precisar de controle total!**
⚠️ **Para uso normal, prefira `--modo frontal/lateral/superior/isometrica`**

```
# Configuração de câmera e plano de projeção

CAMERA <x> <y> <z>           # Centro de projeção
PLANO_P1 <x> <y> <z>         # Ponto 1 do plano
PLANO_P2 <x> <y> <z>         # Ponto 2 do plano
PLANO_P3 <x> <y> <z>         # Ponto 3 do plano
VIEWPORT <largura> <altura>  # Opcional (padrão: 800 600)
```

**Como criar:** Veja o arquivo `objetos/COMO_CRIAR_CONFIGS.txt`

**Dica:** Execute primeiro com `--modo frontal` para ver onde está o objeto,
depois crie sua configuração baseada nos valores mostrados no console.

---

## 📐 Fundamentos Matemáticos

### Entrada de Dados

- **Ponto de Vista** C = (a, b, c) - Posição da câmera
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

---

## 📁 Descrição dos Módulos

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

---

## 🎯 Exemplos de Uso

### Trocar o Objeto

Edite `main.py`:

```python
# Pirâmide
vertices = np.array([
    [0, 0, 0],    # base
    [2, 0, 0],
    [1, 2, 0],
    [1, 1, 2]     # topo
])

superficies = [
    [0, 1, 2],    # base
    [0, 1, 3],    # faces laterais
    [1, 2, 3],
    [2, 0, 3]
]
```

### Mudar Posição da Câmera

```python
C = np.array([10, 10, 15])  # Mais distante
C = np.array([3, 3, 5])     # Mais perto
C = np.array([-5, 5, 10])   # Vista lateral
```

### Alterar Plano de Projeção

```python
# Plano inclinado
P1 = np.array([0, 0, 0])
P2 = np.array([10, 0, 5])
P3 = np.array([0, 10, 3])
```

---

## 🔧 Dependências

- **Python** >= 3.8
- **NumPy** >= 1.24.0 - Operações matriciais
- **Matplotlib** >= 3.7.0 - Visualização

---

## 🎓 Notas de Implementação

### Diferenças em relação ao PDF

1. **Vetor Normal**: O PDF contém um erro de digitação na fórmula de nx (usa z3x2 ao invés de z3z2). Nosso código usa `np.cross()` que implementa corretamente.

2. **Transformação Viewport**: Implementamos tanto a versão iterativa (mais clara) quanto a matricial (mais matemática).

3. **Coordenadas Homogêneas**: Tratamento explícito de casos especiais (w=0).

### Melhorias Possíveis

- [ ] Leitura de objetos de arquivos .txt
- [ ] Remoção de faces ocultas (back-face culling)
- [ ] Iluminação e sombreamento
- [ ] Rotação interativa do objeto
- [ ] Suporte a múltiplos objetos na cena
- [ ] Exportação para diferentes formatos de imagem

---