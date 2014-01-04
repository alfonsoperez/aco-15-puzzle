# coding=utf-8
from colony import *
from puzzle import Puzzle
import sys
import networkx as nx
import random

inicio = ([2,1,3,4,5,6,7,8,9,10,11,12,13,15,14,0],15)
fin = ([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0],15)

i=0
nants = 20
base_attractiveness = 1
initial_tau =  0.1
ratio_de_evaporacion = 0.1
cota = 0.8
ini_est = 100

p1 = Puzzle(inicio, fin, 1, 1, nants, ratio_de_evaporacion, cota, base_attractiveness, initial_tau, ini_est)

p1.run()


''' 
sols = p1.generateAntSolutions()
if sols != [False for _ in range(len(p1.colony.ants))]:
    print ("Sol encontrada.")
    
    for g in sols:
        if g != False:
            print("\t de tamano: "+ str(len(nx.shortest_path(g,p1.generate_node_hash(inicio),p1.generate_node_hash(fin)))))
    
    break
'''