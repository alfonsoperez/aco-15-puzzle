from colony import *
from puzzle import Puzzle
import sys


inicio = ([2,1,3,4,5,6,7,8,9,10,11,12,13,14,15,0],15)
fin = ([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0],15)

ratio_de_evaporacion = 0.89

p1 = Puzzle(inicio, fin, 0.5, 0.5, 8, ratio_de_evaporacion, 0.5)
p1.start()

hormiga = p1.colony.ants[0]

print(hormiga)

#hormiga.draw_graph()

hormiga.__call__()

#hormiga.draw_graph()

#print(p1.colony)
#p1.drawGraph()
