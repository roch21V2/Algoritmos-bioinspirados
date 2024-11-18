import numpy as np
import pandas as pd 
import random 
import time





df_distancias = pd.read_excel('matrices_40_reto.xlsx', sheet_name='Hoja1')
nodos = {index: nodo for index, nodo in enumerate(df_distancias.columns[1:])}
nodos_al_reves ={nodo: index for index, nodo in enumerate(df_distancias.columns[1:])} 


class Problema_TSP:

    
    def __init__(self, n_pob_inicial, num_interseccion, prob_mutation, epochs):
        self.n = n_pob_inicial
        self.interseccion = num_interseccion
        self.prob_mut = prob_mutation
        self.epochs = epochs 
        self.generacion_num = [[] for u in range(self.n)]
        self.nodos_iniciales =[]

        



        for u in range(len(self.generacion_num)):
            indices_a_escoger = [u for u in range(len(nodos))]


            for j in range(len(nodos)):
                x = random.choice(indices_a_escoger)
                indices_a_escoger.remove(x)
                self.generacion_num[u].append(nodos[x])
                if(j == 0):
                    self.nodos_iniciales.append(nodos[x])
            
            self.generacion_num[u].insert(len(self.generacion_num[u]),self.nodos_iniciales[u])
            


    def Calcular_costo(self):
        self.costo_dist = [0 for u in range(self.n)]
        self.fitness =[0 for u in range(self.n)]

        for u in range(len(self.generacion_num)):
            nodo_inicio = self.generacion_num[u][0]
            nodo_j_1 = self.generacion_num[u][1]
            self.costo_dist[u] += df_distancias[nodo_inicio].values[nodos_al_reves[nodo_j_1]]

            for j in range(1,len(self.generacion_num[u])-1):
                nodo_j = self.generacion_num[u][j+1]
                self.costo_dist[u] += df_distancias[self.generacion_num[u][j]].values[nodos_al_reves[nodo_j]]
        
        for u in range(self.n):
            self.fitness [u] = 1 / self.costo_dist[u]

    def Seleccionar_padres(self):

        self.prob = [(self.fitness[u] / sum(self.fitness)) for u in range(len(self.fitness))]
        self.prob_li = []
        self.prob_ls =[]
        self.indices_padres = []
        acum_li = 0
        acum_ls = 0


        for u in range(len(self.generacion_num)):
            acum_ls += self.prob[u]
            self.prob_ls.append(acum_ls)
            self.prob_li.append(acum_li)
            acum_li += self.prob[u]

        while True:
            x = random.random()

            for u in range(len(self.prob)):
                if((x>= self.prob_li[u]) and (x< self.prob_ls[u]) and (u not in self.indices_padres)):
                    self.indices_padres.append(u)
                    break
                    
            if(len(self.indices_padres) == 2):
                break



    def Reproducir(self):
        self.hijos = []
        madre = self.generacion_num[self.indices_padres[0]]
        padre = self.generacion_num[self.indices_padres[1]]


        hijo_1 = madre[:self.interseccion]+padre[self.interseccion:]
        hijo_2 = padre[:self.interseccion]+madre[self.interseccion:]
        

        for u in range(self.interseccion, len(hijo_1)):
            if(hijo_1[u] in hijo_1[:self.interseccion]):
                for j in range(len(padre)):
                    if(padre[j] not in hijo_1[:u]):
                        hijo_1[u] = padre[j]
                        break
        nodo_inicio = hijo_1[0] 
        hijo_1[len(hijo_1)-1] = nodo_inicio

        for j in range(self.interseccion, len(hijo_2)):
            if(hijo_2[j] in hijo_2[:self.interseccion]):
                for n in range(len(madre)):
                    if(madre[n] not in hijo_2[:j]):
                        hijo_2[j] = madre[n]
                        break

        nodo_inicio = hijo_2[0]
        hijo_2[len(hijo_2)-1] = nodo_inicio


        self.hijos.append(hijo_1)
        self.hijos.append(hijo_2)

    def Mutar_hijos(self):

        for u in range(len(self.hijos)):
            x = random.random()
            if(x <= self.prob_mut):
                indices_pueden_cambiar = [j for j in range(1, len(self.hijos[0])-2)]
                i1 = random.choice(indices_pueden_cambiar)
                indices_pueden_cambiar.remove(i1)
                i2 = random.choice(indices_pueden_cambiar)
                self.hijos[u][i1], self.hijos[u][i2] = self.hijos[u][i2], self.hijos[u][i1]

        self.costo_hijos = [0,0]
        for u in range(len(self.hijos)):
            nodo_inicio = self.hijos[u][0]
            nodo_j_ = self.hijos[u][1]

            self.costo_hijos[u] += df_distancias[nodo_inicio].values[nodos_al_reves[nodo_j_]]

            for j in range(1, len(self.hijos[u])-1):
                nodo_j = self.hijos[u][j+1] 
                nodo_i = self.hijos[u][j]
                self.costo_hijos[u] += df_distancias[nodo_i].values[nodos_al_reves[nodo_j]]

    def Reemplazar_pob(self):
        dic_costos = {index: costo for index, costo in enumerate(self.costo_dist)}
        self.dic_ord = sorted(dic_costos.items(), key=lambda elemento: elemento[1], reverse=True)

        dic_costos_hijos = {index: costo for index, costo in enumerate(self.costo_hijos)}
        self.dic_ord_hijos = sorted(dic_costos_hijos.items(), key=lambda elemento: elemento[1])


        indice_min_1, costo_maximo_1 = self.dic_ord[0]
        indice_min_2, costo_maximo_2 = self.dic_ord[1]

        indice_min_hijos, costo_maximo_hijos_1 = self.dic_ord_hijos[0]
        indice_min_hijos2, costo_maximo_hijos_2 = self.dic_ord_hijos[1]

        if(costo_maximo_1 > costo_maximo_hijos_1):
            self.generacion_num[indice_min_1] = self.hijos[indice_min_hijos]

        if(costo_maximo_2 > costo_maximo_hijos_2 ):
            self.generacion_num[indice_min_2] = self.hijos[indice_min_hijos2]

    def Mejor_pob(self):
        mejor_indice = self.costo_dist.index(min(self.costo_dist))
        mejor_ruta = self.generacion_num[mejor_indice]
        mejor_distancia = self.costo_dist[mejor_indice]
        mejor_fitness =self.fitness[mejor_indice]

        return mejor_ruta, mejor_distancia, mejor_fitness
    
    def Algoritmo_genetico(self):
        for u in range(self.epochs):
            self.Calcular_costo()
            self.Seleccionar_padres()
            self.Reproducir()
            self.Mutar_hijos()
            self.Reemplazar_pob()

            mejor_ruta, mejor_distancia, mejor_fitness = self.Mejor_pob()
            mejor_ruta_dec = ' -> '.join(map(str,mejor_ruta))


            print(f'Epoca: {u}  |  Mejor distancia: {mejor_distancia}  | Mejor fitness: {mejor_fitness} \n Mejor ruta: {mejor_ruta_dec}')




tiempo_inicio = time.time()
a = Problema_TSP(100, 20, 0.05,10000)
a.Algoritmo_genetico()
tiempo_final = time.time()
print(f'Tiempo en que tardo en correr: {tiempo_final-tiempo_inicio}')


