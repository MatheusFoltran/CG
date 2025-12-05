# Makefile para rodar o visualizador facilmente
# Uso:
#   make cubo.txt      -> executa `python src/main.py -o objetos/cubo.txt`
#   make piramide.txt  -> executa `python src/main.py -o objetos/piramide.txt`

.PHONY: help all $(OBJECTS) $(addsuffix .txt,$(OBJECTS))

OBJECTS = cubo paralelepipedo piramide prisma_triangular

help:
	@echo "Usage: make <object>    (e.g. make cubo)"
	@echo "       make <object>.txt (e.g. make cubo.txt)"
	@echo "       make all          (runs all objects)"

# Regra padrão: qualquer alvo terminado em .txt será passado para o visualizador
# Passamos apenas o nome do arquivo (ex: `cubo.txt`) para que `main.py` resolva
# o caminho usando o diretório padrão `objetos/` (um nível acima de `src`).
# OPENGL: se definido (qualquer valor), adiciona o flag `--opengl` ao comando
OPENGL_FLAG :=
ifneq ($(OPENGL),)
OPENGL_FLAG := --opengl
endif

%.txt:
	@echo "Running visualization for $@ $(OPENGL_FLAG)"
	python -u src/main.py -o $@ $(OPENGL_FLAG)

# Alvos sem extensão para conveniência (chamam os targets .txt)
$(OBJECTS):
	@$(MAKE) $@.txt

# Alvo para rodar tudo
all: $(OBJECTS)
	@echo "Ran all visualizations"
