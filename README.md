# 🎨 Sistema de Projeção Perspectiva

---

## 📋 Descrição

Sistema de visualização projetivo baseado em **perspectiva cônica**. Implementa a projeção de objetos 3D em um plano 2D, simulando a visão humana.

---

## 🗂️ Estrutura do Projeto

```
projecao-perspectiva/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── math_utils.py      # Operações matemáticas (vetores, produto vetorial)
│   ├── projection.py      # Lógica de projeção perspectiva
│   ├── renderer.py        # Visualização 2D do resultado
│   └── main.py            # Programa principal
│
└── objetos/
    ├── cubo.txt
    └── piramide.txt
```

---

## 🚀 Como Executar

### 1️⃣ Instalação

```bash
# Clonar/baixar o projeto
cd projecao-perspectiva

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Execução

```bash
cd src
python main.py
```

**Saída:**
- Logs no terminal mostrando cada etapa do cálculo
- Janela gráfica com o objeto projetado

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
   ⎢ b·nx   d+b·ny   b·nz    -b·d0 ⎥
   ⎢ c·nx    c·ny   d+c·nz   -c·d0 ⎥
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

## 📝 Formato de Arquivos de Objetos (Opcional)

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
2. **Matriz de Perspectiva** - Elementos devem seguir as fórmulas do PDF
3. **Projeção** - Objetos mais distantes devem parecer menores
4. **Viewport** - Objeto deve estar centralizado na tela

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