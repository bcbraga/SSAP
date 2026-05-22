"""
Este código é uma implementação feita por Bruna Cristina Braga Charytitsch do método ILS (Iterated Local Search)
para o Student Seat Allocation Problem (SSAP), inspirado na formulação apresentada no artigo:

Charytitsch, B. C. B., & Nascimento, M. C. V.
"Conflict-Aware Seat Assignment in Classroom Environments." [Submetido, 2025].

A implementação foi feita em linguagem Python.

Date: [20/08/2025]

---

This code is an implementation by Bruna Cristina Braga Charytitsch of the ILS (Iterated Local Search)
for the Student Seat Allocation Problem (SSAP), inspired by the formulation presented in the article:

Braga Charytitsch, B. C., & Nascimento, M. C. V.
"Conflict-Aware Seat Assignment in Classroom Environments." [Submitted, 2024].

The implementation was developed in Python.

Date: [08/20/2025]
"""


# BIBLIOTECAS/LIBRARIES

import networkx as nx
import numpy as np
from datetime import timedelta
from collections import defaultdict, deque
import random
import itertools
import time
import copy

# Minimum distance between students in the same row / there must be at least 1 desk separating two conflicting students
d_min = 2


def ler_elementos_por_id(nome_arquivo):
    elementos_por_id = {}

    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            indice, elementos_str = linha.split(',', 1)
            elementos = eval(elementos_str)
            elementos_por_id[int(indice)] = elementos

    return elementos_por_id


def ler_arestas_por_id(nome_arquivo):
    arestas_por_id = {}

    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            indice, arestas_str = linha.split(',', 1)
            arestas = eval(arestas_str)
            arestas_por_id[int(indice)] = arestas

    return arestas_por_id


def carregar_segundos_elementos(nome_arquivo):
    segundos_elementos_por_id = {}

    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            elementos = linha.split(',')
            id_atual = int(elementos[0])
            segundos_elementos_por_id[id_atual] = elementos[1]

    return segundos_elementos_por_id


def gerar_lista(frente, atras, x):
    lista = [0] * x

    for indice in frente:
        lista[indice] = 1

    for indice in atras:
        lista[indice] = -1

    return lista


# function receive total desks and number desks per layer, return  list of lists (classroom map)
def gerar_lista_de_listas(total_carteiras, carteiras_por_fileira):
    lista_de_listas = []
    indice_carta = 0

    for num_carteiras in carteiras_por_fileira:
        fileira = []
        for _ in range(num_carteiras):
            if indice_carta < total_carteiras:
                fileira.append(indice_carta)
                indice_carta += 1
        lista_de_listas.append(fileira)

    return lista_de_listas


# function map desks to layers
def map_cartas_to_lists(cartas, lista_de_listas):
    mapeamento = {}
    indice_carta = 0

    for i, row in enumerate(lista_de_listas):
        for j, _ in enumerate(row):
            if indice_carta < len(cartas):
                mapeamento[cartas[indice_carta]] = (i, j)
                indice_carta += 1

    return mapeamento


# define list of desks in front and back
def criar_listas_posicionais(lista_de_listas):
    carteiras_frente = []
    carteiras_atras = []

    for row in lista_de_listas:
        if len(row) >= 2:
            carteiras_frente.extend(row[:2])
            carteiras_atras.extend(row[-2:])

    return carteiras_frente, carteiras_atras


def elementos_na_fileira(lista_de_listas, indice_fileira):
    if indice_fileira < 0 or indice_fileira >= len(lista_de_listas):
        return []

    return lista_de_listas[indice_fileira]


def calcular_peso(pos1, pos2, c_):
    d = abs(pos1 - pos2)
    if d <= d_min - 1:
        p = 2 * c_

    else:
        p = 1 * c_ - 0.1 * d

    return p


def calcular_peso2(pos1, pos2, c_):
    d = abs(pos1 - pos2)
    if d == 0 or d == 1:
        p = 2 * c_
    else:
        p = 2 * c_ - 0.1 * d

    return p


def matriz_zeros(total):
    return np.zeros((total, total))


def prioridade(mat, vet, tot, cor, frente, atras):

    for i in range(tot):

        if vet[i] == -1:
            for j in atras:
                mat[i, j] -= tot * cor

        if vet[i] == 1:
            for j in frente:
                mat[i, j] -= tot * cor  # -100
    return mat


# Ensure the matrix has no negative values
def nao_neg(matrix):
    if np.any(matrix < 0):
        menor_valor_negativo = np.min(matrix)

        valor_a_somar = -menor_valor_negativo
        matrix = matrix + valor_a_somar

    return matrix


def criar_matriz_sala(fileiras, alunos, posicoes):
    sala = []
    num_carteira = 0
    for num_carteiras in fileiras:
        fileira = [None] * num_carteiras
        sala.append(fileira)
        num_carteira += num_carteiras

    for aluno, posicao in zip(alunos, posicoes):
        num_carteira = 0
        for i, fileira in enumerate(sala):
            if posicao < num_carteira + len(fileira):
                fileira[posicao - num_carteira] = aluno
                break
            num_carteira += len(fileira)

    return sala


def encontrar_posicao_aluno(sala, aluno):
    for i, fileira in enumerate(sala):
        if aluno in fileira:
            return i, fileira.index(aluno)
    return None


def verificar_distancia_conflitos(sala, arestas):
    conflitos_layers_consecutivos = []
    conflitos_mesmo_layer = []
    conflitos_distancia_maior_igual_2 = []
    conflitos_distancia_menor_2 = []

    posicoes_alunos = {}
    for i, fileira in enumerate(sala):
        for j, aluno in enumerate(fileira):
            if aluno is not None:
                posicoes_alunos[aluno] = (i, j)

    for x, y in arestas:

        pos_x = posicoes_alunos.get(x)
        pos_y = posicoes_alunos.get(y)

        if pos_x and pos_y:
            fileira_x, posicao_x = pos_x
            fileira_y, posicao_y = pos_y

            # Check if the students are in consecutive layers
            if abs(fileira_x - fileira_y) == 1:
                conflitos_layers_consecutivos.append((x, y))

            # Check if the students are in the same layer (row)
            if fileira_x == fileira_y:
                conflitos_mesmo_layer.append((x, y))

            # Check if the students are in the same row or in consecutive rows, with distance >= 2
            if abs(fileira_x - fileira_y) <= 1 and abs(posicao_x - posicao_y) >= 2:
                conflitos_distancia_maior_igual_2.append((x, y))

            # Check if the students are in the same layer (row) or in consecutive layers, with distance < 2
            if abs(fileira_x - fileira_y) <= 1 and abs(posicao_x - posicao_y) < 2:
                conflitos_distancia_menor_2.append((x, y))

    return (
        conflitos_layers_consecutivos,
        conflitos_mesmo_layer,
        conflitos_distancia_maior_igual_2,
        conflitos_distancia_menor_2
    )


# Returns the sum of the distances between students in consecutive layers in conflict along with other information
def verificar_distancia_conflitos2(sala, arestas):
    conflitos_layers_consecutivos = []
    conflitos_mesmo_layer = []
    conflitos_distancia_maior_igual_2_mesmo_layer = []
    conflitos_distancia_menor_2_mesmo_layer = []
    conflitos_distancia_maior_igual_2_layer_consecutivos = []
    conflitos_distancia_menor_2_layer_consecutivos = []

    soma_distancias_consecutivos = 0

    posicoes_alunos = {}
    for i, fileira in enumerate(sala):
        for j, aluno in enumerate(fileira):
            if aluno is not None:
                posicoes_alunos[aluno] = (i, j)

    for x, y in arestas:

        pos_x = posicoes_alunos.get(x)
        pos_y = posicoes_alunos.get(y)

        if pos_x and pos_y:
            fileira_x, posicao_x = pos_x
            fileira_y, posicao_y = pos_y

            if abs(fileira_x - fileira_y) == 1:
                conflitos_layers_consecutivos.append((x, y))

                distancia = abs(posicao_x - posicao_y)
                if distancia >= 2:
                    conflitos_distancia_maior_igual_2_layer_consecutivos.append((x, y))
                    soma_distancias_consecutivos += distancia
                else:
                    conflitos_distancia_menor_2_layer_consecutivos.append((x, y))

            if fileira_x == fileira_y:
                conflitos_mesmo_layer.append((x, y))

                if abs(posicao_x - posicao_y) >= d_min:
                    conflitos_distancia_maior_igual_2_mesmo_layer.append((x, y))
                else:
                    conflitos_distancia_menor_2_mesmo_layer.append((x, y))

    return (
        conflitos_layers_consecutivos,
        conflitos_mesmo_layer,
        conflitos_distancia_maior_igual_2_mesmo_layer,
        conflitos_distancia_menor_2_mesmo_layer,
        conflitos_distancia_maior_igual_2_layer_consecutivos,
        conflitos_distancia_menor_2_layer_consecutivos,
        soma_distancias_consecutivos
    )


#  ---------------
def identificar_posicoes(matriz_de_pesos, num_carteiras_por_fileira, arestas_conflito, lista_cart_frente,
                         lista_cart_atras, lista_r):
    num_alunos, num_total_carteiras = matriz_de_pesos.shape
    num_fileiras = len(num_carteiras_por_fileira)

    sala_de_aula = [[None] * num_carteiras_por_fileira[fileira] for fileira in range(num_fileiras)]

    posicoes_ocupadas = set()
    posicoes_alunos = {}

    grau_aluno = defaultdict(int)
    for a1, a2 in arestas_conflito:
        grau_aluno[a1] += 1
        grau_aluno[a2] += 1

    alunos_ordenados = sorted(grau_aluno.keys(), key=lambda aluno: -grau_aluno[aluno])

    def pos_to_fileira_coluna(pos):
        fileira, coluna = 0, pos
        for i in range(num_fileiras):
            if coluna < num_carteiras_por_fileira[i]:
                return i, coluna
            coluna -= num_carteiras_por_fileira[i]
        return None, None

    def fileira_coluna_to_pos(fileira, coluna):
        pos = sum(num_carteiras_por_fileira[:fileira]) + coluna
        return pos

    def atualizar_matriz_pesos(pos, aluno):
        fileira, coluna = pos_to_fileira_coluna(pos)

        for c in range(max(0, coluna - (d_min - 1)), min(num_carteiras_por_fileira[fileira], coluna + d_min)):
            if c != coluna:
                pos_vizinho = fileira_coluna_to_pos(fileira, c)
                for a in range(num_alunos):
                    if (aluno, a) in arestas_conflito or (a, aluno) in arestas_conflito:
                        matriz_de_pesos[a][
                            pos_vizinho] += 10

        for f in range(max(0, fileira - 1), min(num_fileiras, fileira + 2)):
            if f != fileira:
                for c in range(max(0, coluna - 1), min(num_carteiras_por_fileira[f], coluna + 2)):
                    pos_vizinho = fileira_coluna_to_pos(f, c)
                    for a in range(num_alunos):
                        if (aluno, a) in arestas_conflito or (a, aluno) in arestas_conflito:
                            matriz_de_pesos[a][
                                pos_vizinho] += 10

    def verificar_restricoes(pos, aluno):
        fileira, coluna = pos_to_fileira_coluna(pos)

        if lista_r[aluno] == 1 and pos not in lista_cart_frente:
            return False
        if lista_r[aluno] == -1 and pos not in lista_cart_atras:
            return False

        for outro_aluno, outra_pos in posicoes_alunos.items():
            outra_fileira, outra_coluna = pos_to_fileira_coluna(outra_pos)

            if (aluno, outro_aluno) in arestas_conflito or (outro_aluno, aluno) in arestas_conflito:

                if fileira == outra_fileira:
                    if abs(coluna - outra_coluna) < d_min:
                        return False

                elif abs(fileira - outra_fileira) == 1:
                    if abs(coluna - outra_coluna) < 2:
                        return False

        return True

    # Function to try to allocate a student in the best possible position, respecting preferences
    def tentar_alocar_aluno(aluno):
        posicoes_ordenadas = np.argsort(matriz_de_pesos[aluno])
        for melhor_posicao in posicoes_ordenadas:
            if melhor_posicao not in posicoes_ocupadas and verificar_restricoes(melhor_posicao, aluno):
                posicoes_ocupadas.add(melhor_posicao)
                posicoes_alunos[aluno] = melhor_posicao
                fileira, coluna = pos_to_fileira_coluna(melhor_posicao)
                sala_de_aula[fileira][coluna] = aluno
                atualizar_matriz_pesos(melhor_posicao, aluno)
                return True
        return False

    # Main function to allocate all students
    def alocar_alunos():
        na_fila = set(alunos_ordenados)
        fila = deque(alunos_ordenados)
        while fila:
            aluno = fila.popleft()
            na_fila.discard(aluno)

            if aluno in posicoes_alunos:
                continue

            if tentar_alocar_aluno(aluno):

                vizinhos = [a2_ for a1_, a2_ in arestas_conflito if a1_ == aluno] + \
                           [a1_ for a1_, a2_ in arestas_conflito if a2_ == aluno]
                vizinhos = list(set(vizinhos))

                vizinhos.sort(key=lambda v0: -grau_aluno[v0])

                for v in vizinhos:
                    if v not in posicoes_alunos and v not in na_fila:
                        fila.append(v)
                        na_fila.add(v)

    alocar_alunos()

    return sala_de_aula


# Insert the non-allocated students randomly
def inserir_nos_nao_inseridos(lista_de_listas, total_nos):
    nos_inseridos = set()
    for sublista in lista_de_listas:
        for no in sublista:
            if no is not None:
                nos_inseridos.add(no)

    nos_nao_inseridos = set(range(total_nos)) - nos_inseridos

    posicoes_none = [(i, j) for i, sublista in enumerate(lista_de_listas) for j, no in enumerate(sublista) if
                     no is None]

    if len(nos_nao_inseridos) > len(posicoes_none):
        raise ValueError("There are more non-allocated nodes than available None positions.")

    for no in nos_nao_inseridos:
        posicao = random.choice(posicoes_none)
        posicoes_none.remove(posicao)
        lista_de_listas[posicao[0]][posicao[1]] = no

    return lista_de_listas


# Check if the nodes with priorities are inserted correctly
def verificar_posicionamento(sala, alunos_frente, alunos_tras):
    total_frente_correto = 0
    total_tras_correto = 0
    total_frente_errado = []
    total_tras_errado = []

    for fileira in sala:
        for posicao in range(2):
            aluno = fileira[posicao]
            if aluno in alunos_frente:
                total_frente_correto += 1
            elif aluno in alunos_tras:
                total_tras_errado.append(aluno)

        for posicao in range(len(fileira) - 2, len(fileira)):
            aluno = fileira[posicao]
            if aluno in alunos_tras:
                total_tras_correto += 1
            elif aluno in alunos_frente:
                total_frente_errado.append(aluno)

        for posicao in range(2, len(fileira) - 2):
            aluno = fileira[posicao]
            if aluno in alunos_frente:
                total_frente_errado.append(aluno)
            elif aluno in alunos_tras:
                total_tras_errado.append(aluno)

    return total_frente_correto, total_tras_correto, total_frente_errado, total_tras_errado


# Return a list with non-allocated nodes and free desks
def listas_retorna(classroom, x):
    students = [i for i in range(x)]

    lista = []
    for alun in students:
        exist = any(alun in sublista for sublista in classroom)
        if not exist:
            lista.append(alun)

    lista2 = []
    cart = 0
    for i in range(len(classroom)):
        for j in range(len(classroom[i])):
            if classroom[i][j] is None:
                lista2.append(cart)
            cart += 1

    return lista, lista2


# Return parameters for the objective function
def pre_obj(sal_, edge_, frt_, atr_):

    (v1_, _, _, v4_, _, v6_, som_dist_) = verificar_distancia_conflitos2(sal_, edge_)

    # a3 = wrong front, a4 = wrong back
    _, _, fr_, at_ = verificar_posicionamento(sal_, frt_, atr_)

    '''
    print(' ')
    print("Conflicts in consecutive layers:", v1)
    print("Conflicts in the same layer:", v2)
    print("Conflicts in the same row (distance >= 2):", v3)
    print(' ')
    print("Conflicts in the same layer (distance < 2):", v4)
    print("Conflicts in consecutive rows (distance >= 2):", v5)
    print(' ')
    print("Conflicts in consecutive layers (distance < 2):", v6)
    '''

    return fr_, at_, v4_, v6_, v1_, som_dist_


# Return value of the objective function
def objective(aa, ss, num_arest_timesmaxn):
    # Objective function according to model
    value = ss - 2 * num_arest_timesmaxn * abs(aa)

    return value


# penalized objective function (fo)
def penalizar_obj(fo_base, num_frente_errado, num_atras_errado, num_p2_errado, num_p3_errado,
                  peso_penalizacao=pow(10, 7)):
    """
    fo_base → value of the objective function without penalty
    num_frente_errado → number of students incorrectly placed in the front
    num_atras_errado → number of students incorrectly placed in the back
    num_p2_errado → number of conflicts in the same layer with distance < d_min
    num_p3_errado → number of conflicts in consecutive layers with distance < 2
    """

    penalidade = peso_penalizacao * (num_frente_errado + num_atras_errado + num_p2_errado + num_p3_errado)
    return fo_base - penalidade


# penalized objective function (fo)
def penalizar_obj2(fo_base_, som_p, peso_penalizacao=pow(10, 7)):
    penalidade_ = peso_penalizacao * som_p
    return fo_base_ - penalidade_


# Check feasibility - returns 1 if feasible, otherwise infeasible
def verify(nfe, nae, dmlm2, dlcm2):
    value = (abs(nfe) + abs(nae) + abs(dmlm2) + abs(dlcm2))

    if value == 0:
        return 1, value

    else:
        return 0, value


# Convert list of lists to a vector
def converter_sala_para_vetor(sala):
    vetor_sala = []

    for fileira in sala:
        for carteira in fileira:
            if carteira is None:
                vetor_sala.append(-1)
            else:
                vetor_sala.append(carteira)

    return vetor_sala


# Convert vector to a list of lists
def converter_vetor_para_sala(vetor, carteiras_por_fileira):
    sala = []
    indice_atual = 0

    for num_carteiras in carteiras_por_fileira:
        fileira = []
        for _ in range(num_carteiras):
            fileira.append(vetor[indice_atual])
            indice_atual += 1
        sala.append(fileira)

    return sala


# Given a list of students and edges, return a list with students of degree zero
# and another with students of non-zero degree
def calcular_graus(arestas, numeros):
    graus = {numero: 0 for numero in numeros}

    for aresta in arestas:
        for numero in aresta:
            if numero in graus:
                graus[numero] += 1

    graus_zero = [numero for numero, grau in graus.items() if grau == 0]
    graus_maior_igual_um = [numero for numero, grau in graus.items() if grau >= 1]

    return graus_zero, graus_maior_igual_um


def posicao_linear_para_fileira_coluna_util(pos, num_carteiras_por_fileira):
    """
    Convert a linear position (in the vector vet) to (row, column).

    Parameters:
    - pos - linear position (0 to total number of desks - 1)
    - num_carteiras_por_fileira - list with the number of desks per row

    Returns:
    - (row, column)
    """

    coluna = pos
    for fileira_index, num_cart_fileira in enumerate(num_carteiras_por_fileira):
        if coluna < num_cart_fileira:
            return fileira_index, coluna
        else:
            coluna -= num_cart_fileira

    raise ValueError(f'Invalid linear position: {pos}')


def busca1_otimizada(sala__, n_, s_, frente_, atras_, edges_):

    sala_ = sala__.copy()
    ins_stu, free_cart = listas_retorna(sala_, s_)
    vet = converter_sala_para_vetor(sala_)

    (fr, at, p2, p3, p1, som_z) = pre_obj(sala_, edges_, frente_, atras_)
    f0_temp = objective(len(p1), som_z, len(edges_)*max(n_)+1)
    f0 = penalizar_obj(f0_temp, len(fr), len(at), len(p2), len(p3))

    vet0 = vet.copy()
    best_ind = None
    best = []

    if free_cart:
        for ind1 in range(len(free_cart)):
            indicador = 0

            for no in range(len(vet)):
                if vet0[no] != -1:

                    vet0[free_cart[ind1]], vet0[no] = vet0[no], -1

                    clas = converter_vetor_para_sala(vet0, n_)
                    (fr1, at1, p2_, p3_, p1_, ss_) = pre_obj(clas, edges_, frente_, atras_)
                    f_temp = objective(len(p1_), ss_, len(edges_)*max(n_)+1)
                    f = penalizar_obj(f_temp, len(fr1), len(at1), len(p2_), len(p3_))

                    if f > f0:
                        best_ind = no
                        best = vet0[free_cart[ind1]]
                        indicador = 1
                        f0 = f

                    vet0[no], vet0[free_cart[ind1]] = vet0[free_cart[ind1]], -1

            if indicador != 0:
                vet0[free_cart[ind1]] = best
                vet0[best_ind] = -1

    # pós-processing
    vet0 = [None if x == -1 else x for x in vet0]
    sala_final = converter_vetor_para_sala(vet0, n_)
    (fr1f, at1f, p2_f, p3_f, p1_f, ss_2) = pre_obj(sala_final, edges_, frente_, atras_)
    f_final0 = objective(len(p1_f), ss_2, len(edges_)*max(n_)+1)
    f_final = penalizar_obj(f_final0, len(fr1f), len(at1f), len(p2_f), len(p3_f))

    return sala_final, f_final


# -----------------------------------------------------------------------------------------------------------------
def permute_within_bounds(arr, lower_limit, upper_limit):

    if lower_limit < 0 or upper_limit >= len(arr):
        raise ValueError("Limits are out of the vector range")
    if lower_limit > upper_limit:
        raise ValueError("The lower limit must be less than or equal to the upper limit")

    if lower_limit == upper_limit:
        return [arr.copy()]

    sub_arr = arr[lower_limit:upper_limit + 1]
    rest_arr_before = arr[:lower_limit]
    rest_arr_after = arr[upper_limit + 1:]

    max_permute_size = 5
    sub_arr_size = len(sub_arr)

    if sub_arr_size > max_permute_size:
        permute_size = min(max_permute_size, sub_arr_size)
        indices_to_permute = random.sample(range(sub_arr_size), permute_size)

        permute_sub_arr = [sub_arr[i] for i in indices_to_permute]
        permutations = itertools.permutations(permute_sub_arr)

        result = []
        for perm in permutations:
            permuted_sub_arr = sub_arr.copy()
            for idx, value in zip(indices_to_permute, perm):
                permuted_sub_arr[idx] = value
            result.append(rest_arr_before + permuted_sub_arr + rest_arr_after)
    else:
        result = [rest_arr_before + list(perm) + rest_arr_after
                  for perm in itertools.permutations(sub_arr)]

    return result


#     -----------------------------------------------------------------------------------------------------------------

# Return indices with the limits of the layers
def calcular_indices(vetor_numeros_elementos):
    """
    Calculate the lower and upper indices of each sublist mapped in the main vector.

    Args:
        vetor_numeros_elementos (list): List containing the number of elements in each sublist.

    Returns:
        list: List of tuples where each tuple contains the lower and upper index of a sublist in the main vector.
    """
    indices = []
    inicio = 0

    for num_elementos in vetor_numeros_elementos:
        fim = inicio + num_elementos - 1
        indices.append((inicio, fim))
        inicio = fim + 1

    return indices


# --- Optimized Main Function: random_diversification_search ---
def busca_diversificadora_aleatoria(sala_inicial, n_config, arestas_conflito, r_prioridades,
                                    carteiras_frente_pos, carteiras_atras_pos):
    current_sala = copy.deepcopy(sala_inicial)

    aluno_para_posicao = {}
    posicao_para_aluno = {}

    def update_mapeamentos(s_aula_map):
        # Update the student - position mappings by rebuilding them.
        aluno_para_posicao.clear()
        posicao_para_aluno.clear()
        for r_idx, row0 in enumerate(s_aula_map):
            for c_idx0, student_id in enumerate(row0):
                if student_id is not None:
                    aluno_para_posicao[student_id] = (r_idx, c_idx0)
                    posicao_para_aluno[(r_idx, c_idx0)] = student_id

    update_mapeamentos(current_sala)

    temp_frente_alunos = [i for i, pref in enumerate(r_prioridades) if pref == 1]
    temp_atras_alunos = [i for i, pref in enumerate(r_prioridades) if pref == -1]

    fr_orig, at_orig, p2_orig, p3_orig, p1_orig, som_dist_orig = pre_obj(current_sala, arestas_conflito,
                                                                         temp_frente_alunos, temp_atras_alunos)
    f_orig = penalizar_obj(objective(len(p1_orig), som_dist_orig, len(arestas_conflito)*max(n_config)+1), len(fr_orig), len(at_orig),
                           len(p2_orig), len(p3_orig))

    best_sala_global = copy.deepcopy(current_sala)
    best_f_global = f_orig

    max_sweeps = 100
    current_sweep = 0
    improvement_found_in_sweep = True

    while improvement_found_in_sweep and current_sweep < max_sweeps:
        improvement_found_in_sweep = False
        current_sweep += 1

        if best_f_global == 0:
            print(f"Random diversification search finished: FO 0 reached at sweep {current_sweep}.")
            return best_sala_global, best_f_global

        alunos_foco_diversificacao = []

        min_alunos_por_fileira = 1

        for fileira_idx, row in enumerate(best_sala_global):
            alunos_na_fileira = [aluno for aluno in row if aluno is not None]
            if alunos_na_fileira:
                percentual_sorteado_para_fileira = 0.15
                num_to_sample_in_row = max(min_alunos_por_fileira,
                                           int(len(alunos_na_fileira) * percentual_sorteado_para_fileira))
                num_to_sample_in_row = min(num_to_sample_in_row, len(alunos_na_fileira))

                if num_to_sample_in_row > 0:
                    alunos_foco_diversificacao.extend(
                        random.sample(alunos_na_fileira, num_to_sample_in_row)
                    )

        random.shuffle(alunos_foco_diversificacao)

        if not alunos_foco_diversificacao:
            fr_current, at_current, p2_current, p3_current, p1_current, _ = pre_obj(best_sala_global, arestas_conflito,
                                                                                    temp_frente_alunos,
                                                                                    temp_atras_alunos)
            _, num_fact_current = verify(len(fr_current), len(at_current), len(p2_current), len(p3_current))
            if num_fact_current == 0:
                print(f"Rand. div. search fin.: No further improvement and feasible solution at sweep {current_sweep}.")
                return best_sala_global, best_f_global
            else:
                break

        for aluno_problema in alunos_foco_diversificacao:
            pos_aluno_problema = aluno_para_posicao.get(aluno_problema)
            if pos_aluno_problema is None:
                continue

            fileira_atual, carteira_atual = pos_aluno_problema
            candidato_a_troca_pos = []

            if r_prioridades[aluno_problema] == 1:
                for pos_linear in carteiras_frente_pos:
                    f, c = posicao_linear_para_fileira_coluna_util(pos_linear, n_config)
                    if (0 <= f < len(best_sala_global) and 0 <= c < len(best_sala_global[f]) and
                            (f, c) != pos_aluno_problema):
                        candidato_a_troca_pos.append((f, c))
            elif r_prioridades[aluno_problema] == -1:
                for pos_linear in carteiras_atras_pos:
                    f, c = posicao_linear_para_fileira_coluna_util(pos_linear, n_config)
                    if (0 <= f < len(best_sala_global) and 0 <= c < len(best_sala_global[f]) and
                            (f, c) != pos_aluno_problema):
                        candidato_a_troca_pos.append((f, c))
            else:

                for c_idx in range(len(best_sala_global[fileira_atual])):
                    if (fileira_atual, c_idx) != pos_aluno_problema:
                        candidato_a_troca_pos.append((fileira_atual, c_idx))

                fileiras_pool_sorteio = [f_idx for f_idx in range(len(n_config)) if f_idx != fileira_atual]
                random.shuffle(fileiras_pool_sorteio)

                num_fileiras_para_sorteio = min(2, len(fileiras_pool_sorteio))
                fileiras_aleatorias = random.sample(fileiras_pool_sorteio, num_fileiras_para_sorteio)

                for f_rand in fileiras_aleatorias:
                    for c_rand in range(len(best_sala_global[f_rand])):
                        if (f_rand, c_rand) != pos_aluno_problema:
                            candidato_a_troca_pos.append((f_rand, c_rand))

            random.shuffle(candidato_a_troca_pos)

            num_candidatos_gerados = len(candidato_a_troca_pos)

            min_swaps_por_aluno = 8
            percentual_candidatos_a_avaliar = 0.15
            max_swaps_por_aluno = 30

            limite_dinamico_percentual = int(num_candidatos_gerados * percentual_candidatos_a_avaliar)
            limite_final_para_swaps = max(min_swaps_por_aluno, min(max_swaps_por_aluno, limite_dinamico_percentual))
            # ------------------------------------------------------------------------------------------------

            # Iterate over the candidates, respecting the dynamic limit
            for (f_cand, c_cand) in candidato_a_troca_pos[:limite_final_para_swaps]:
                aluno_na_pos_candidata = best_sala_global[f_cand][c_cand]

                best_sala_global[fileira_atual][carteira_atual] = aluno_na_pos_candidata
                best_sala_global[f_cand][c_cand] = aluno_problema

                fr_temp, at_temp, p2_temp, p3_temp, p1_temp, som_dist_temp = pre_obj(best_sala_global, arestas_conflito,
                                                                                     temp_frente_alunos,
                                                                                     temp_atras_alunos)
                f_temp = penalizar_obj(objective(len(p1_temp), som_dist_temp, len(arestas_conflito)*max(n_config)+1), len(fr_temp),
                                       len(at_temp), len(p2_temp), len(p3_temp))

                # Acceptance criterion: strictly better (MAXIMIZATION)
                if f_temp > best_f_global:
                    best_f_global = f_temp
                    improvement_found_in_sweep = True
                    update_mapeamentos(best_sala_global)

                    if best_f_global == 0:
                        print(f"Random diversification search finished: OF 0 reached at sweep {current_sweep}.")
                        return best_sala_global, best_f_global

                    break
                else:
                    # Undo the swap if there is no improvement, restoring the previous classroom state
                    best_sala_global[fileira_atual][carteira_atual] = aluno_problema
                    best_sala_global[f_cand][c_cand] = aluno_na_pos_candidata

    return best_sala_global, best_f_global


# ----------------------------------------------------------------------------
def permute_and_evaluate(vector, node_index, evaluate_func):
    best_vector = vector[:]
    f0, _, _ = evaluate_func(vector)

    vector_list = list(vector)

    for i in range(len(vector_list)):
        if i != node_index:
            vector_list[node_index], vector_list[i] = vector_list[i], vector_list[node_index]

            f, fact_03, _ = evaluate_func(vector_list)

            if f > f0:
                best_vector = vector_list[:]
                f0 = f

            vector_list[node_index], vector_list[i] = vector_list[i], vector_list[node_index]

    return best_vector, f0


# -----------------------------------------------------------------------------------------------------------

def permute_and_evaluate_with_indices(vector, indices, element_index, evaluate_func):
    best_vector = vector[:]
    f0, _ = evaluate_func(vector)

    vector_list = list(vector)

    for idx in indices:
        if idx != element_index:

            vector_list[element_index], vector_list[idx] = vector_list[idx], vector_list[element_index]

            f, fact00 = evaluate_func(vector_list)

            if f > f0:
                best_vector = vector_list[:]
                f0 = f

            vector_list[element_index], vector_list[idx] = vector_list[idx], vector_list[element_index]

    return best_vector, f0


def busca_indiv_ativas(sala_o, f_o, n_o, frente_o, atras_o, edges_o):
    tot_e = len(edges_o)

    vet = converter_sala_para_vetor(sala_o)

    (fr, at, p2, p3, p1, soma_02) = pre_obj(sala_o, edges_o, frente_o, atras_o)

    f0 = f_o
    vet0 = vet.copy()

    def evaluate_vector(vector):
        clas_f = converter_vetor_para_sala(vector, n_o)
        fr1_f, at1_f, p2_f, p3_f, p1_f, soma_02_f = pre_obj(clas_f, edges_o, frente_o, atras_o)
        fact1_02, fact1_02_ = verify(len(fr1_f), len(at1_f), len(p2_f), len(p3_f))
        return objective(len(p1_f), soma_02_f, tot_e*max(n_o)+1) - pow(10, 7) * fact1_02_, fact1_02, fact1_02

    if not fr and not at and not p2 and not p3:
        return converter_vetor_para_sala(vet0, n_o), f0
    else:
        if p3:
            conjunto = {item for par in p3 for item in par}

            for elemento in conjunto:
                vet0, f0 = permute_and_evaluate(vet0, vet0.index(elemento), evaluate_vector)

    return converter_vetor_para_sala(vet0, n_o), f0


def busca_indiv_front(sala_o, f_o, n_o, frente_o, atras_o, edges_o, c_front):
    tot_e = len(edges_o)

    vet = converter_sala_para_vetor(sala_o)

    (fr, at, p2, p3, p1, soma_01) = pre_obj(sala_o, edges_o, frente_o, atras_o)

    f0 = f_o
    vet0 = vet.copy()

    def evaluate_vector(vector):
        clas_f = converter_vetor_para_sala(vector, n_o)
        fr1_f, at1_f, p2_f, p3_f, p1_f, soma_01_f = pre_obj(clas_f, edges_o, frente_o, atras_o)
        fact1_01, fact1_01_ = verify(len(fr1_f), len(at1_f), len(p2_f), len(p3_f))
        return objective(len(p1_f), soma_01_f, tot_e*max(n_o)+1) - pow(10, 7) * fact1_01_, fact1_01

    if not fr and not at and not p2 and not p3 and not p1:
        return converter_vetor_para_sala(vet0, n_o), f0
    else:
        if fr:
            for elemento in fr:
                vet0, f0 = permute_and_evaluate_with_indices(vet0, c_front, vet0.index(elemento), evaluate_vector)

    return converter_vetor_para_sala(vet0, n_o), f0


def busca_indiv_back(sala_o, f_o, n_o, frente_o, atras_o, edges_o, c_back):

    tot_e = len(edges_o)

    vet = converter_sala_para_vetor(sala_o)

    (fr, at, p2, p3, p1, soma_00) = pre_obj(sala_o, edges_o, frente_o, atras_o)

    f0 = f_o
    vet0 = vet.copy()

    def evaluate_vector(vector):
        clas_f = converter_vetor_para_sala(vector, n_o)
        fr1_f, at1_f, p2_f, p3_f, p1_f, soma_00_f = pre_obj(clas_f, edges_o, frente_o, atras_o)
        fact1_00, fact1_00_ = verify(len(fr1_f), len(at1_f), len(p2_f), len(p3_f))
        return objective(len(p1_f), soma_00_f, tot_e*max(n_o)+1) - pow(10, 7) * fact1_00_, fact1_00

    if not fr and not at and not p2 and not p3:
        return converter_vetor_para_sala(vet0, n_o), f0
    else:
        if at:
            for elemento in at:
                vet0, f0 = permute_and_evaluate_with_indices(vet0, c_back, vet0.index(elemento), evaluate_vector)

    return converter_vetor_para_sala(vet0, n_o), f0


# Initial Solution
def initial_solution__(g, nos_com_grau_sorted, s9, r, n, coringa, carteiras_frente, carteiras_atras, mapeamento,
                       lista_de_listas, frente, atras):
    sequencia_f = carteiras_frente[:]
    sequencia_a = carteiras_atras[:]
    sequencia = list(range(s9))
    # j = None

    matriz = prioridade(matriz_zeros(s9), r, s9, s9 * coringa, carteiras_frente, carteiras_atras)

    nos_com_grau_sorted_filtrado = [(x, y) for (x, y) in nos_com_grau_sorted if y != 0]

    lista_geral = []

    for est, grau_est in nos_com_grau_sorted_filtrado:
        if r[est] == 1 or r[est] == -1:
            prioridade_pref = 3
        else:
            prioridade_pref = 1

        lista_geral.append((est, grau_est, prioridade_pref, random.random()))

    lista_geral.sort(key=lambda x: (-x[1], -x[2], x[3]))

    # Extract the final ordered list of students
    '''
        [ est for (est, _, _, _) in lista_geral ]
        means:

        take the first element of the tuple (est, which is the student ID);

        ignore (_) the other elements of the tuple (degree, preference priority, random number);

        generate a list only with the student IDs, in the final desired order
    '''

    lista_students = [est for (est, _, _, _) in lista_geral]

    # ------------------------------------------------------------

    for i in lista_students:

        viz = list(g.neighbors(i))

        if r[i] == 1 and sequencia_f:
            j = random.choice(sequencia_f)
        elif r[i] == -1 and sequencia_a:
            j = random.choice(sequencia_a)
        elif r[i] == 0 and sequencia:
            j = random.choice(sequencia)
        else:
            continue

        # Removing the selected element from the corresponding lists
        sequencia = [elem for elem in sequencia if elem != j]
        sequencia_f = [elem for elem in sequencia_f if elem != j]
        sequencia_a = [elem for elem in sequencia_a if elem != j]

        mask = np.arange(matriz.shape[0]) != i
        mask2 = np.arange(matriz.shape[1]) != j

        matriz[mask, j] += 2 * coringa
        matriz[i, mask2] += 2 * coringa

        # ------------------------------------------------------------------------------------------

        # Given desk j, access row/position (dictionary)
        carteira_escolhida = j
        posicao_na_sala = mapeamento[carteira_escolhida]

        # Row to which desk j belongs
        indice_fileira = posicao_na_sala[0]

        # List of column indices that must be changed (those in the same layer as j)
        indices_alterar = elementos_na_fileira(lista_de_listas, indice_fileira)

        # SAME LAYER --------------------------------------------------------------

        for k in viz:
            for ind0 in indices_alterar:
                if ind0 != j:
                    carteira_escolhida_k = ind0
                    posicao_na_sala_k = mapeamento[carteira_escolhida_k]
                    matriz[k, ind0] += calcular_peso(posicao_na_sala[1], posicao_na_sala_k[1], coringa)

        # CONSECUTIVE LAYERS -------------------------------------------------------------------

        if indice_fileira == 0:
            elementos_d = elementos_na_fileira(lista_de_listas, indice_fileira + 1)

            for k in viz:
                for f0 in elementos_d:
                    pos_na_sala_k2 = mapeamento[f0]
                    matriz[k, f0] += calcular_peso2(posicao_na_sala[1], pos_na_sala_k2[1], coringa)

        if indice_fileira == len(n) - 1:
            elementos_a = elementos_na_fileira(lista_de_listas, indice_fileira - 1)

            for k in viz:
                for f0 in elementos_a:
                    pos_na_sala_k2 = mapeamento[f0]
                    matriz[k, f0] += calcular_peso2(posicao_na_sala[1], pos_na_sala_k2[1], coringa)

        if 0 < indice_fileira < len(n) - 1:
            elementos_a = elementos_na_fileira(lista_de_listas, indice_fileira - 1)
            elementos_d = elementos_na_fileira(lista_de_listas, indice_fileira + 1)

            for k in viz:

                for f0a in elementos_a:
                    pos_na_sala_k2a = mapeamento[f0a]
                    matriz[k, f0a] += calcular_peso2(posicao_na_sala[1], pos_na_sala_k2a[1], coringa)

                for f0d in elementos_d:
                    pos_na_sala_k2d = mapeamento[f0d]
                    matriz[k, f0d] += calcular_peso2(posicao_na_sala[1], pos_na_sala_k2d[1], coringa)

    # --------------------------------------------------------------------------------------------------

    sala_ini = identificar_posicoes(nao_neg(matriz), n, g.edges(), carteiras_frente, carteiras_atras, r)
    (r1, r2, r3, r4, r5, r6, r_d_sum) = verificar_distancia_conflitos2(sala_ini, g.edges())
    _, _, a3, a4 = verificar_posicionamento(sala_ini, frente, atras)

    # ----------------------------------------------------------------------------------------------------

    return sala_ini, objective(len(r1), r_d_sum, len(g.edges())*max(n)+1), nao_neg(matriz)


# Get the nodes involved in the conflicts
def conj(tuplas):
    nos_unicos = set()

    for tupla in tuplas:
        nos_unicos.update(tupla)

    lista_nos_unicos = list(nos_unicos)

    return lista_nos_unicos


# Given the total number of elements and a list with some numbers smaller than the total
# return a list with layers that are not consecutive to these
def numeros_nao_consecutivos(total, lista):
    numeros_set = set(lista)

    nao_consecutivos = set()

    for num in range(total):
        if (num - 1 not in numeros_set) and (num + 1 not in numeros_set) and (num not in numeros_set):
            nao_consecutivos.add(num)

    return sorted(list(nao_consecutivos))


# Function to test swapping elements between non-consecutive layers
# vector with the element to be swapped, element, intervals where the swaps will be attempted
# nodes in front, nodes behind, edge list
def trocar_elemento(vector, elemento, intervalos, front, back, edg, vec_n0):
    def evaluate_vector(vector0):
        clas_f = converter_vetor_para_sala(vector0, vec_n0)
        fr1_f, at1_f, p2_f, p3_f, p1_f, sum_05 = pre_obj(clas_f, edg, front, back)
        fact1_05, fact1_05_n = verify(len(fr1_f), len(at1_f), len(p2_f), len(p3_f))
        return objective(len(p1_f), sum_05, len(edg)*max(vec_n0)+1) - pow(10, 7) * fact1_05_n, fact1_05, fact1_05_n

    try:
        posicao_elemento = vector.index(elemento)
    except ValueError:
        raise ValueError("Elemento não encontrado no vetor")

    melhor_vector = vector[:]
    melhor_valor, _, _ = evaluate_vector(vector)

    for (lim_inf, lim_sup) in intervalos:
        for i in range(lim_inf, lim_sup + 1):
            if i == posicao_elemento:
                continue

            novo_vector = vector[:]
            novo_vector[posicao_elemento], novo_vector[i] = novo_vector[i], novo_vector[posicao_elemento]

            novo_valor, fact_05, _ = evaluate_vector(novo_vector)

            if novo_valor > melhor_valor:
                melhor_vector = novo_vector
                melhor_valor = novo_valor

    return converter_vetor_para_sala(melhor_vector, vec_n0), melhor_valor


# Given a list of lists, a sublist index, and two elements of this sublist, swap the positions of the elements
def trocar_elementos_na_sublista(lista_de_listas, indice_sublista, indice_elemento1, indice_elemento2):
    if indice_sublista < 0 or indice_sublista >= len(lista_de_listas):
        raise IndexError("Sublist index is out of valid range")

    # Check if the element indices are valid
    if indice_elemento1 < 0 or indice_elemento1 >= len(lista_de_listas[indice_sublista]):
        raise IndexError("Index of element1 is out of valid range")
    if indice_elemento2 < 0 or indice_elemento2 >= len(lista_de_listas[indice_sublista]):
        raise IndexError("Index of element2 is out of valid range")

    lista_de_listas[indice_sublista][indice_elemento1], lista_de_listas[indice_sublista][indice_elemento2] = (
        lista_de_listas[indice_sublista][indice_elemento2], lista_de_listas[indice_sublista][indice_elemento1])

    return lista_de_listas


# Calls function to minimize active edges if possible
def aresta_ativa_min(s_melhor_, s_melhor_fo_, g0_, g0_edges, frente0_, atras0_, c_, n0_):

    _, _, _, _, p1_test1, _ = pre_obj(s_melhor_, g0_edges, frente0_, atras0_)
    res_best = s_melhor_[:]
    fo_res_best = s_melhor_fo_

    # There is an active edge
    if p1_test1:

        envolvidos = conj(p1_test1)

        for node in envolvidos:
            viz_no = list(g0_.neighbors(node))

            layer = []
            for viz in viz_no:
                fileira_v, carteira_v = encontrar_posicao_aluno(res_best, viz)
                layer.append(fileira_v)

            layers = list(set(layer))
            nc = numeros_nao_consecutivos(c_, layers)

            if nc:
                indice_viz = calcular_indices(n0_)
                selecionados = [indice_viz[i] for i in nc]
                res_best, fo_res_best = trocar_elemento(converter_sala_para_vetor(res_best), node, selecionados,
                                                        frente0_, atras0_, g0_edges, n0_)

    return res_best, fo_res_best


# REFINEMENT PART 2 - MAXIMUM DISTANCES
def distancias_max(res_best_2, fo_res_best_2, g0_edges_2, frente0_2, atras0_2, p1_test1_2_, peso0_2):
    def evaluate_class(sa_la2):
        fr1_f2, at1_f2, p2_f2, p3_f2, p1_f2, soma_06 = pre_obj(sa_la2, g0_edges_2, frente0_2, atras0_2)
        fact1_06, fact1_06_ = verify(len(fr1_f2), len(at1_f2), len(p2_f2), len(p3_f2))
        return objective(len(p1_f2), soma_06, peso0_2+1) - pow(10, 7) * fact1_06_, fact1_06

    lista_cop = res_best_2[:]
    lista_cop_fo = fo_res_best_2

    # Place the elements of active edges as far apart as possible ------------------------------
    if p1_test1_2_:

        for aresta in p1_test1_2_:
            fileira_x, carteira_x = encontrar_posicao_aluno(lista_cop, aresta[0])
            fileira_y, carteira_y = encontrar_posicao_aluno(lista_cop, aresta[1])

            dist_ini = abs(carteira_x - carteira_y)
            controlador = 0

            melhor_lista = copy.deepcopy(lista_cop)
            melhor_fo = lista_cop_fo
            melhor_dist = dist_ini

            for z in range(len(lista_cop[fileira_x])):
                lista_temp = copy.deepcopy(lista_cop)
                lista_temp = trocar_elementos_na_sublista(lista_temp, fileira_x, carteira_x, z)

                for w in range(len(lista_temp[fileira_y])):
                    lista_temp = copy.deepcopy(lista_cop)
                    lista_temp = trocar_elementos_na_sublista(lista_temp, fileira_x, carteira_x, z)
                    lista_temp = trocar_elementos_na_sublista(lista_temp, fileira_y, carteira_y, w)

                    dist_new = abs(z - w)

                    if dist_new >= 2:
                        fo_temp, res_fact = evaluate_class(lista_temp)

                        if fo_temp >= melhor_fo and dist_new > melhor_dist:
                            melhor_lista = copy.deepcopy(lista_temp)
                            melhor_fo = fo_temp
                            melhor_dist = dist_new
                            controlador = 1

            if controlador != 0:
                lista_cop = copy.deepcopy(melhor_lista)
                lista_cop_fo = melhor_fo

    return lista_cop, lista_cop_fo


# Distribute zero-degree nodes into empty positions
def distribuir_elementos(elementos_x, lista_de_listas_x):
    posicoes_vazias = [(i, j) for i in range(len(lista_de_listas_x))
                       for j in range(len(lista_de_listas_x[i]))
                       if lista_de_listas_x[i][j] is None]

    random.shuffle(elementos_x)

    num_posicoes_a_preencher = min(len(posicoes_vazias), len(elementos_x))

    for idx in range(num_posicoes_a_preencher):
        pos = posicoes_vazias[idx]
        i, j = pos
        lista_de_listas_x[i][j] = elementos_x[idx]

    return lista_de_listas_x


def separar_nos_por_preferencia(nos, lista_r2):
    nos_com_zero = []  # List for nodes where lista_r2[node] == 0
    nos_outros = []  # List for nodes where lista_r2[node] != 0

    for no in nos:
        if lista_r2[no] == 0:
            nos_com_zero.append(no)
        else:
            nos_outros.append(no)

    return nos_com_zero, nos_outros


def inserir_alunos_respeitando_factibilidade_z(sala_parcial_z, alunos_a_inserir_z, arestas_conflito_z,
                                               alunos_frente_z, alunos_atras_z):

    posicoes_vazias_z = [(i, j) for i in range(len(sala_parcial_z))
                         for j in range(len(sala_parcial_z[i]))
                         if sala_parcial_z[i][j] is None]

    def verificar_solucao_z(sala_z, arestas_conflito_z0, alunos_frente_z0, alunos_atras_z0):
        fr1f, at1f, p2_f, p3_f, p1_f, soma_f = pre_obj(sala_z, arestas_conflito_z0, alunos_frente_z0, alunos_atras_z0)
        fact1, _ = verify(len(fr1f), len(at1f), len(p2_f), len(p3_f))
        return fact1 != 0

    for aluno_a_inserir_z in list(alunos_a_inserir_z):
        for (i_vazia_z, j_vazia_z) in posicoes_vazias_z:
            nova_sala_z = copy.deepcopy(sala_parcial_z)

            nova_sala_z[i_vazia_z][j_vazia_z] = aluno_a_inserir_z

            if verificar_solucao_z(nova_sala_z, arestas_conflito_z, alunos_frente_z, alunos_atras_z):
                sala_parcial_z[i_vazia_z][j_vazia_z] = aluno_a_inserir_z
                alunos_a_inserir_z.remove(aluno_a_inserir_z)
                posicoes_vazias_z.remove((i_vazia_z, j_vazia_z))
                break

    return sala_parcial_z, alunos_a_inserir_z


# FOR NODES TO BE INSERTED
def posicoes_permitidas(sala, no_atual, arestas, dist_min_mesma_fileira, dist_min_consecutivas, lista_r):
    """
    Returns the allowed positions to insert the current node, considering conflict and seating priority constraints.
    The node can be inserted in any position, as long as the restrictions are satisfied.

    :param sala: List of lists representing the classroom (rows).
    :param no_atual: ID of the node being inserted.
    :param arestas: List of ordered pairs representing conflicts between nodes (e.g., [(X, Y), (Y, Z)]).
    :param dist_min_mesma_fileira: Minimum distance between conflicting nodes in the same row.
    :param dist_min_consecutivas: Minimum distance between conflicting nodes in consecutive rows.
    :param lista_r: Priority list for each node (1 = front, -1 = back, 0 = any position).
    :return: List of allowed positions (row, seat) for the current node.
    """

    nos_conflitantes = set()
    for x, y in arestas:
        if x == no_atual or y == no_atual:
            nos_conflitantes.add(x if x != no_atual else y)

    posicoes_conflitantes = []

    for i, fileira in enumerate(sala):
        for j, posicao in enumerate(fileira):
            if posicao in nos_conflitantes:
                posicoes_conflitantes.append((i, j))

    posicoes_permitidas0 = []

    prioridade0 = lista_r[no_atual]

    for i, fileira in enumerate(sala):
        for j, posicao in enumerate(fileira):
            permitido = True

            for (k, l) in posicoes_conflitantes:
                if i == k:
                    if abs(j - l) < dist_min_mesma_fileira:
                        permitido = False
                        break

            if permitido:
                if i > 0:
                    for (k, l) in posicoes_conflitantes:
                        if k == i - 1:
                            if abs(j - l) < dist_min_consecutivas:
                                permitido = False
                                break
                if permitido and i < len(sala) - 1:
                    for (k, l) in posicoes_conflitantes:
                        if k == i + 1:
                            if abs(j - l) < dist_min_consecutivas:
                                permitido = False
                                break

            if permitido:
                if prioridade0 == 1:
                    if j >= 2:
                        permitido = False
                elif prioridade0 == -1:
                    if j < len(fileira) - 2:
                        permitido = False

            if permitido:
                posicoes_permitidas0.append((i, j))

    return posicoes_permitidas0


# For inserted nodes
def posicoes_permitidas_para_no_inserido(sala, no_atual, arestas, dist_min_mesma_fileira, dist_min_consecutivas,
                                         lista_r):
    """
    Returns the allowed positions for a node already inserted in the classroom, considering conflict
    restrictions and seating priorities. It checks the current position and all other possible ones,
    respecting the constraints.

    :param sala: List of lists representing the classroom (rows).
    :param no_atual: ID of the already inserted node being checked.
    :param arestas: List of ordered pairs representing conflicts between nodes (e.g., [(X, Y), (Y, Z)]).
    :param dist_min_mesma_fileira: Minimum distance between conflicting nodes in the same row.
    :param dist_min_consecutivas: Minimum distance between conflicting nodes in consecutive rows.
    :param lista_r: List of seating priorities for each node (1 = front, -1 = back, 0 = any position).
    :return: Tuple containing the current position of the node and a list of other allowed positions
             (row, seat), or (None, []) if the node is not in the classroom.
    """

    posicao_atual = None

    for i, fileira in enumerate(sala):
        for j, posicao in enumerate(fileira):
            if posicao == no_atual:
                posicao_atual = (i, j)
                break
        if posicao_atual is not None:
            break

    if posicao_atual is None:
        return None, []

    nos_conflitantes = set()
    for x, y in arestas:
        if x == no_atual or y == no_atual:
            nos_conflitantes.add(x if x != no_atual else y)

    posicoes_conflitantes = []

    for i, fileira in enumerate(sala):
        for j, posicao in enumerate(fileira):
            if posicao in nos_conflitantes:
                posicoes_conflitantes.append((i, j))

    posicoes_permitidas1 = []

    prioridade1 = lista_r[no_atual]

    for i, fileira in enumerate(sala):
        for j, posicao in enumerate(fileira):
            if posicao == no_atual:
                continue

            permitido = True

            for (k, l) in posicoes_conflitantes:
                if i == k:
                    if abs(j - l) < dist_min_mesma_fileira:
                        permitido = False
                        break

            if permitido:
                if i > 0:
                    for (k, l) in posicoes_conflitantes:
                        if k == i - 1:
                            if abs(j - l) < dist_min_consecutivas:
                                permitido = False
                                break
                if permitido and i < len(sala) - 1:
                    for (k, l) in posicoes_conflitantes:
                        if k == i + 1:
                            if abs(j - l) < dist_min_consecutivas:
                                permitido = False
                                break

            if permitido:
                if prioridade1 == 1:
                    if j >= 2:
                        permitido = False
                elif prioridade1 == -1:
                    if j < len(fileira) - 2:
                        permitido = False

            if permitido:
                posicoes_permitidas1.append((i, j))

    return posicao_atual, posicoes_permitidas1


def perturbacao_elementos_remover(vetor, percentual):

    quantidade_remover = max(1, int(len(vetor) * percentual / 100))

    quantidade_remover = min(quantidade_remover, len(vetor))

    indices_remover = random.sample(range(len(vetor)), quantidade_remover)

    elementos_remover = [vetor[indice] for indice in indices_remover]

    return elementos_remover


def pode_ocupar(posicoes_permitidas2, no_novo, sala):
    for pos in posicoes_permitidas2:
        if sala[pos[0]][pos[1]] == no_novo:
            return True
    return False


# Randomly swaps nodes between allowed positions
def trocar_nos(s_viz, nos_a_mover, g0, d_min0, r0):
    """
    Swaps nodes in the classroom s_viz based on the allowed positions.

    :param s_viz: List of lists representing the classroom.
    :param nos_a_mover: List of nodes to be moved.
    :param g0: Graph containing the edges.
    :param d_min0: Minimum allowed distance.
    :param r0: List of priorities.
    """

    for node in nos_a_mover:
        pos_atual, pos_permitida = posicoes_permitidas_para_no_inserido(s_viz, node, g0.edges(), d_min0, 2, r0)

        if pos_atual is None or not pos_permitida:
            continue

        pos_aleatoria = random.choice(pos_permitida)
        xl, yl = pos_aleatoria

        al, bl = pos_atual

        s_viz[al][bl], s_viz[xl][yl] = s_viz[xl][yl], s_viz[al][bl]

    return s_viz


# Total number of instances
exe = 131

# Total number of algorithm runs - external / robustness (set between 30 and 100)
total_run = 30

# Total number of internal runs - to guarantee an optimum
total_exec = 1


def main():
    # read the data
    nome_arquivo = 'data/grafo.txt'
    nome_arquivo2 = 'data/grafo_vet.txt'
    nome_arquivo3 = 'data/grafo_frente.txt'
    nome_arquivo4 = 'data/grafo_tras.txt'
    nome_arquivo5 = 'data/grafo_info.txt'

    dicionario_arestas = ler_arestas_por_id(nome_arquivo)
    dicionario_elementos = ler_elementos_por_id(nome_arquivo2)
    dicionario_frente = ler_elementos_por_id(nome_arquivo3)
    dicionario_atras = ler_elementos_por_id(nome_arquivo4)
    dicionario_nodes = carregar_segundos_elementos(nome_arquivo5)

    # total run
    for ru in np.arange(total_run):

        arq_heur = open('res_heur/heuristica_' + str(ru + 1) + '.txt', 'a')
        arq_heur2 = open('res_heur/info_' + str(ru + 1) + '.txt', 'a')

        arq_heur0 = open('res_heur/ini_solution_' + str(ru + 1) + '.txt', 'a')
        arq_heur1 = open('res_heur/refin_pre_' + str(ru + 1) + '.txt', 'a')
        arq_heur3 = open('res_heur/refin_pos_' + str(ru + 1) + '.txt', 'a')

        # Sweep each instance
        for instancia in np.arange(exe):

            # Make an undirected graph --------------------------------------
            g0 = nx.Graph()

            # total students
            s0 = int(dicionario_nodes[instancia + 1])

            # Add nodes
            g0.add_nodes_from(range(s0))

            # Add edges
            arestas = dicionario_arestas[instancia + 1]

            # data2
            g0.add_edges_from([tuple(sorted(aresta)) for aresta in arestas[0]])

            # desks per layer
            n0 = dicionario_elementos[instancia + 1]

            # total edges
            ta = g0.number_of_edges()

            n_lambda = max(n0)

            # Active edge weight
            peso = ta * n_lambda

            # total layers
            c = len(n0)

            # requirements 1: front / -1:f  back / 0: without
            r0 = gerar_lista(dicionario_frente[instancia + 1], dicionario_atras[instancia + 1], s0)

            # node's degree array
            graus0 = list(dict(g0.degree()).values())

            # tuples list (index, degree)
            nos_com_grau = [(i, graus0[i]) for i in range(len(graus0))]

            # Ordenate tuple list from degreee (second element in the tuple) em ordem decrescente
            nos_com_grau_sorted0 = sorted(nos_com_grau, key=lambda x: x[1], reverse=True)

            # -------------------------------------------------------------------------------------------------------

            # function make_list_of_lists    ------------------------------------------------
            total_carteiras = s0
            carteiras_por_fileira = n0  # Each element represents the number of desks in each layer

            lista_de_listas0 = gerar_lista_de_listas(total_carteiras, carteiras_por_fileira)

            cartas = list(range(s0))

            mapeamento0 = map_cartas_to_lists(cartas, lista_de_listas0)

            carteiras_frente0, carteiras_atras0 = criar_listas_posicionais(lista_de_listas0)

            coringa0 = max(n0) + 1

            frente0 = []
            atras0 = []

            for i in range(s0):
                if r0[i] == -1:
                    atras0.append(i)

                if r0[i] == 1:
                    frente0.append(i)

            # ------------------------------------------------------------

            #  ----------------------------- # Executes the heuristic 'total_exec' times

            # list of executions
            part1 = []
            part2 = []
            execucoes = []

            for _ in np.arange(total_exec):

                start_time_in = time.monotonic()

                # Create the initial solution for the ILS ------------------------------------------------------------

                start_time = time.monotonic()

                # initial solution
                class_, obj_, mat_ = initial_solution__(g0, nos_com_grau_sorted0, s0, r0, n0, coringa0,
                                                        carteiras_frente0,
                                                        carteiras_atras0, mapeamento0, lista_de_listas0, frente0,
                                                        atras0)

                # Local Search 1 - considers the penalized objective function
                s_, f_s_ = busca1_otimizada(class_, n0, s0, frente0, atras0, g0.edges())
                s = copy.deepcopy(s_)

                # Students to insert and available seats
                alunos_ins, carte_free = listas_retorna(s, s0)
                graus_zero, graus_maior_igual_um = calcular_graus(g0.edges(), alunos_ins)
                nos_com_zero, nos_outros = separar_nos_por_preferencia(graus_zero, r0)

                # Insertion of the remaining nodes
                sala_atualizada_z, alunos_nao_inseridos_z = inserir_alunos_respeitando_factibilidade_z(
                    copy.deepcopy(s),
                    graus_maior_igual_um + nos_outros,
                    g0.edges(), frente0, atras0)

                # Insert zero-degree nodes
                if nos_com_zero:
                    sala_atualizada_z = distribuir_elementos(nos_com_zero, sala_atualizada_z)

                # If there are still uninserted students - insert them randomly
                if alunos_nao_inseridos_z:
                    sala_atualizada_z = inserir_nos_nao_inseridos(sala_atualizada_z, s0)

                # ---------------------------------------- INITIAL SOLUTION ANALYSIS - FEASIBILITY
                # Check feasibility after insertions
                (var1, var2, var3, var4, var5, var6) = pre_obj(sala_atualizada_z, g0.edges(), frente0, atras0)
                var_fact0, num_fact = verify(len(var1), len(var2), len(var3), len(var4))
                f_sala_atualizada_z0 = objective(len(var5), var6, peso+1)
                f_sala_atualizada_z = penalizar_obj2(f_sala_atualizada_z0, num_fact)

                # -----------------------------------------------------------------------------------------------------

                # lOCAL SEARCH

                # Perturbation rate
                iter_ = 0
                itermax = 10000
                itermaxsemmelhora = 1500

                # ------------------------------------------------------------------------------------------------
                end_time = time.monotonic()

                # STORE INITIAL SOLUTION
                # id graph, feasibility, f(x) objective function, time, time
                arq_heur0.write(str(instancia + 1) + str(',') + str(var_fact0) + str(',') + str(sala_atualizada_z) +
                                str(',') + str(f_sala_atualizada_z) + str(',') + str(end_time - start_time) + '\n')
                # -------------------------------------------------------------------------------------------------

                # apply local search
                # Diversification
                s_melhor, s_melhor_fo = busca_diversificadora_aleatoria(copy.deepcopy(sala_atualizada_z),
                                                                        n0, g0.edges(), r0, carteiras_frente0,
                                                                        carteiras_atras0)
                # -------------------------------------------------------------------------------------------------

                # Control solution - if zero, the program stops
                controle = -1

                itersemmelhora = 0

                while (controle != 0) and (iter_ < itermax) and (itersemmelhora < itermaxsemmelhora):
                    iter_ += 1

                    # Perturb the current solution - respecting feasible positions / add randomness when needed
                    nos_a_mover = perturbacao_elementos_remover(converter_sala_para_vetor(s_melhor), 25)
                    s_viz = copy.deepcopy(s_melhor)

                    trocar_nos(s_viz, nos_a_mover, g0, d_min, r0)

                    # Diversification
                    res1_s, res1_f = busca_diversificadora_aleatoria(
                        copy.deepcopy(s_viz),
                        n0,
                        g0.edges(),
                        r0,
                        carteiras_frente0,
                        carteiras_atras0
                    )

                    # Intensification
                    res2_s, res2_f = busca_indiv_back(res1_s, res1_f, n0, frente0, atras0, g0.edges(), carteiras_atras0)
                    res3_s, res3_f = busca_indiv_front(res2_s, res2_f, n0, frente0, atras0, g0.edges(),
                                                       carteiras_frente0)
                    s_melhor_viz, s_melhor_viz_fo = busca_indiv_ativas(res3_s, res3_f, n0, frente0, atras0, g0.edges())

                    # ------------------------------------------------------------------------
                    (fr1ff, at1ff, p2_ff, p3_ff, p1_ff, d_sum_ff) = pre_obj(s_melhor_viz, g0.edges(), frente0, atras0)
                    var_fact2, _ = verify(len(fr1ff), len(at1ff), len(p2_ff), len(p3_ff))
                    # ------------------------------------------------------------------------

                    # Acceptance criterion:
                    if s_melhor_viz_fo > s_melhor_fo:  # and var_fact2 == 1:
                        s_melhor = s_melhor_viz[:]
                        s_melhor_fo = s_melhor_viz_fo
                        itersemmelhora = 0  # Reset the counter of iterations without improvement

                    else:
                        itersemmelhora += 1  # Increment the counter of iterations without improvement
                        # ----------------------------------------------------------------------------------------

                    # If f0 is zero, stop
                    controle = s_melhor_fo

                # ----------------------------------------------------------------------------------------------------

                res_best_ = s_melhor[:]
                fo_res_best_ = s_melhor_fo

                # CHECK IF RESULT CONTAINS ACTIVE EDGE
                aaa, bbb, ccc, ddd, p1_test1_00, _ = pre_obj(res_best_, g0.edges(), frente0, atras0)

                l1, l2, l3, l4, p1_test1_00, _ = pre_obj(res_best_, g0.edges(), frente0, atras0)
                fat, _ = verify(len(l1), len(l2), len(l3), len(l4))

                # PRE-REFINEMENT - id graph, feasibility, result, f(x) objective function
                arq_heur1.write(
                    str(instancia + 1) + str(',') + str(fat) + str(',') + str(res_best_) + str(',') + str(fo_res_best_)
                    + '\n')

                # --------------------------------
                start_time_1 = time.monotonic()

                if p1_test1_00:
                    # REFINEMENT PHASE PART 1 - CALL FUNCTION ARESTA_ATIVA_MIN
                    res_best_, fo_res_best_ = aresta_ativa_min(res_best_, fo_res_best_, g0, g0.edges(), frente0,
                                                               atras0, c, n0)

                    # CHECK IF RESULT STILL CONTAINS ACTIVE EDGE
                    _, _, _, _, p1_test1_2, _ = pre_obj(res_best_, g0.edges(), frente0, atras0)
                    if p1_test1_2:
                        # REFINEMENT PHASE PART 2 - MAXIMIZE DISTANCES - ONLY CALL IF ACTIVE EDGES EXIST
                        res_best_, fo_res_best_ = distancias_max(res_best_, fo_res_best_, g0.edges(), frente0,
                                                                 atras0,
                                                                 p1_test1_2)
                end_time_1 = time.monotonic()
                # --------------------------------

                # CHECK IF RESULT STILL CONTAINS ACTIVE EDGE
                l1, l2, l3, l4, p1_test1_00, _ = pre_obj(res_best_, g0.edges(), frente0, atras0)
                fat2, _ = verify(len(l1), len(l2), len(l3), len(l4))

                # POST-REFINEMENT - graph id, feasibility, result, time
                arq_heur3.write(
                    str(instancia + 1) + str(',') + str(fat2) + str(',') + str(res_best_) + str(',') +
                    str(end_time_1 - start_time_1) + '\n')

                # End time - Total
                end_time_in = time.monotonic()

                # ----------------------------------------------------------------------------------------------

                # Save results -------------------------------------------------------
                part1.append(fo_res_best_)

                part2.append(res_best_)
                part2.append(fo_res_best_)
                part2.append(timedelta(seconds=end_time_in - start_time_in))
                part2.append(end_time_in - start_time_in)

                execucoes.append(part2)
                part2 = []
                # ------------------ -------------------------------------------------------
                # -----------------------------------------------------------------------------------------------------

                # Check best result
                # index of smallest (im)
                im = part1.index(max(part1))

                # CHECK IF RESULT CONTAINS ACTIVE EDGE
                l1, l2, l3, l4, p1_test1_00, _ = pre_obj(execucoes[im][0], g0.edges(), frente0, atras0)
                fat3, _ = verify(len(l1), len(l2), len(l3), len(l4))

                # ----------------------------------------------------------------
                # id graph, fact, class map, f(x) Objective function
                arq_heur.write(str(instancia + 1) + str(',') + str(fat3) + str(',') + str(execucoes[im][0]) + str(',')
                               + str(execucoes[im][1]) + '\n')

                # id graph, fat, f(x) Objective function , time, time
                arq_heur2.write(str(instancia + 1) + str(',') + str(fat3) + str(',') + str(execucoes[im][1]) + str(',')
                                + str(execucoes[im][2]) + str(',') + str(execucoes[im][3]) + '\n')

                # ------------------------------------------------------------------------------------------------------
                # """

        # Close the archive
        arq_heur.close()
        arq_heur2.close()
        arq_heur0.close()
        arq_heur1.close()
        arq_heur3.close()


# Run program
if __name__ == "__main__":
    main()
