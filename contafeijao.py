# -*- coding: utf-8 -*-
#*=============================================================
# UNIFAL = Universidade Federal de Alfenas .
# BACHARELADO EM CIENCIA DA COMPUTACAO.
# Trabalho . . : Contagem de feijoes
# Professor  . : Luiz Eduardo da Silva
#Aluno . . . . : Mateus Henrique Martins
#Data  . . . . : 20/05/2024
# =============================================================


# %%
#import matplotlib.pyplot as plt # comentei esses dois imports, pois no meu ambiente o codigo so funcionou sem eles, creio que em outro ambiente vai precisar dele 
#import matplotlib.image as img
import numpy as np
import argparse
import os

# %%
def readpgm (name):
    f = open(name,"r")

    assert f.readline() == 'P2\n'
    line = f.readline()
    while (line[0] == '#'):
           line = f.readline()
    (width, height) = [int(i) for i in line.split()]
    print (width, height)
    depth = int(f.readline())
    assert depth <= 255
    print (depth)
    
    img = []
    row = []
    j = 0
    for line in f:
       values = line.split()
       for val in values:
           row.append (int (val))
           j = j + 1
           if j >= width:
              img.append (row)
              j=0
              row = []

    f.close()
    return img

# %%
def savepgm(name, img, depth):
    # Dimensions
    heigth = len(img)
    width = len(img[0])

    # Open file to write in
    with open(name, 'w') as f:
        # Pgm header
        f.write("P2\n")
        f.write("# Image processing with python - ByDu\n")
        f.write("{} {}\n".format(width, heigth))
        f.write("{}\n".format(depth))  # Max gray level

        # write pixels to pgm file
        for line in img:
            for pixel in line:
                f.write("{} ".format(pixel))
            f.write("\n")

# %%
def imgalloc (nl, nc):
    img = []
    for i in range(nl):
        lin = []
        for j in range(nc):
            lin.append(0)
        img.append(lin)
    return img

# %% função para limiarizar
def limiarizacao(img, limiar):
    nl, nc = len(img), len(img[0])
    img_bin = [[0 for _ in range(nc)] for _ in range(nl)]
        
    for i in range(nl):
        for j in range(nc):
            img_bin[i][j] = 0 if img[i][j] < limiar else 255
        
    return img_bin

# %% função dos componentes conexos 
def rotulacao_componentes_conexos(img_bin):
    nl, nc = len(img_bin), len(img_bin[0])
    labels = [[0 for _ in range(nc)] for _ in range(nl)]
    current_label = 1
    component_sizes = {}

    def flood_fill(x, y, label):
        size = 1
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if labels[cx][cy] == 0 and img_bin[cx][cy] == 0:
                labels[cx][cy] = label
                size += 1
                for nx, ny in [(cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)]:
                    if 0 <= nx < nl and 0 <= ny < nc and labels[nx][ny] == 0 and img_bin[nx][ny] == 0:
                        stack.append((nx, ny))
        return size

    for i in range(nl):
        for j in range(nc):
            if img_bin[i][j] == 0 and labels[i][j] == 0:
                size = flood_fill(i, j, current_label)
                if size in component_sizes:
                    component_sizes[size].append(current_label)
                else:
                    component_sizes[size] = [current_label]
                current_label += 1

# filtro dos componentes pequenos
    min_size = 100  # Define o tamanho mínimo para manter um componente
    for size, labels_list in component_sizes.items():
        if size < min_size:
            for label in labels_list:
                for i in range(nl):
                    for j in range(nc):
                        if labels[i][j] == label:
                            labels[i][j] = 0

    return labels, current_label - 1



# %% função para filtrar componentes pequenos
def filtrar_componentes_pequenos(labels, min_size):
    nl, nc = len(labels), len(labels[0])
    label_count = {}

    for i in range(nl):
        for j in range(nc):
            label = labels[i][j]
            if label > 0:
                label_count[label] = label_count.get(label, 0) + 1

    filtered_labels = [[label if label_count.get(label, 0) >= min_size else 0 for label in row] for row in labels]
    
    num_filtered_components = sum(1 for count in label_count.values() if count >= min_size)
    
    return filtered_labels, num_filtered_components


# %% Leitura de imagem
parser = argparse.ArgumentParser(description='Script description')

# %% adiciona argumentos
parser.add_argument('image_name', type=str, help='Image name in format .PGM')

# %% analisa argumentos via linha de comando
args = parser.parse_args()
image_name = args.image_name

img = readpgm(image_name)
print(np.asarray(img))

# %% limiar as imagens 
limiar = 50   # Defina o valor do limiar conforme necessário
img_bin = limiarizacao(img, limiar)

# %% conecta img na tabela
labels, num_components = rotulacao_componentes_conexos(img_bin)

# %% filtra imagens
min_size = 50  # Defina o tamanho mínimo para componentes a serem considerados feijões
filtered_labels, num_filtered_components = filtrar_componentes_pequenos(labels, min_size)

# Salvar a imagem rotulada (opcional, para visualização)
labels_normalized = np.uint8(255 * np.asarray(filtered_labels) / np.max(filtered_labels))
savepgm("limiar.pgm", img_bin, 255)
savepgm("filtered_labels.pgm", labels_normalized.tolist(), 255)

#%% lista os componenetes 
print("")
# print(f"#componentes = {num_filtered_components}") python3, na minha máquina tava desuatalizada
print("#componentes= {}".format(num_filtered_components))


