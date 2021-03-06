# coding=utf-8
from __future__ import division
import networkx as nx
from aconode import ACONode
import random
import math
import sys
import matplotlib.pyplot as plt
import operator

'''
ant.py

@Author: Alfonso Perez-Embid (Twitter: @fonsurfing)

'''
# We have to re-seed our RNG in order to give different results on 
# different tasks

random.seed()

class Ant(object):
    
    def __init__(self, ant_id):
        
        ''' Ant class
        This class is to be run as a multiprocessing Task
        Id: numerical identifier. starts from 0
        startNode: numerical identifier of the start node
        currentNode: numerical identifier of the current node
        '''
        
        self.id = ant_id
        self.start_node_id = None # This is assigned on the start function of ACOProblem
        self.current_node_id = None # This is assigned on the start function of ACOProblem   
        self.last_node_id = None # Last node where we were
        self.solution_nodes_id = [1147797409030816545] # This is assigned on the start function of ACOProblem

        self.possible_new_edges = list()
        
        self.decision_tables = dict() # Decision tables for different nodes
        
        self.aco_specific_problem = None # It's going to be passed by the specific aco problem in the __init__ so the ant knows
        # How to expand the graph, the parameters of the problem and so on
 
        self.graph = None # The initial subgraph is passed from ACOProblem to the set_start_node method
        self.solution_found = None # This is set in expand_node so move_to_another_ant goes there.
        
        self.list_nodes_visited = None # List of node indexes visited
        self.iteration_number = None # To compute pheromone
        
    def set_start_node(self, start_node_id, graph):

        self.start_node_id = start_node_id
        self.current_node_id = start_node_id
        self.last_node_id = None
        self.graph = graph # So it directly updates the global graph
        self.decision_tables = dict()
        self.list_nodes_visited = list()
        self.list_nodes_visited.append(self.current_node_id)
        self.solution_found = None
        
    def __str__(self):
        
        ant_to_string = str(id(self))
        ant_to_string += " [ Ant no:"+ str(self.id) + ", Start node: "+ str(self.start_node_id)
        ant_to_string += ", Current node: " + str(self.current_node_id) +" ]"
        ant_to_string += " Solution nodes list: "+ str(self.solution_nodes_id)

        return ant_to_string

    def __call__(self):
        

        if self.aco_specific_problem == None:
            raise Exception ("You have to pass an instance of your specific ACO problem to every ant of the colony first!")
    
        ''' __call__ (lookForFood)
            Method to be called by Consumer in a multiprocessing Queue
            Parameters:
            none
            
            Return: True?  TODO.
            
            The ant looks for a solution of the ACOProblem and when it does find one, 
            return to it's house, giving a positive feedback (depositing pheromone)
            on the path
        '''

        i = 0
        cota_de_salida = self.aco_specific_problem.estimate
        #print(self)
        while self.current_node_id not in self.solution_nodes_id:     
            
            self.expand_node(self.current_node_id)      
            
            
#             
#              Debug
#              Fallos encontrados del debug:
#              1. vuelve por donde a venido, tenemos que poner q el inmediato anterior
#              no lo visite!
#                
#             print ("=========\nEstamos en "+ str(self.current_node_id))
#             print ("Current: "+ str(self.aco_specific_problem.generateStateFromHash(self.current_node_id)))
#             print ("Podemos ir a: \n\t"+ str(self.possible_new_edges))
#             print("Tabla de costes: "+ str([(self.aco_specific_problem.generate_node_hash(s),self.aco_specific_problem.calculate_cost(s)) for s in self.aco_specific_problem.successors(self.graph.node[self.current_node_id]['node'].state) if self.last_node_id != self.aco_specific_problem.generate_node_hash(s)]))
#             print ("La tabla de decision es: \n\t" + str(self.decision_table(self.current_node_id)))
#             print ("La solucion: "+ str(self.aco_specific_problem.generateStateFromHash(self.solution_nodes_id[0])))
#             print ("Sol id: "+ str(self.solution_nodes_id))
#             print ("=======")
#                      
#             raw_input()


            self.move_to_another_node()
               
            if i != 0 and i % cota_de_salida == 0:
                #print("\t Cota de salida: "+ str(cota_de_salida))
                #print("\t Saliendo con "+ str(len(self.graph.node)) + " nodos")
                #print (str(self.id)+" Saliendo en "+ str(self.current_node_id))

                return (None,False)
            i += 1
        
        # Returns a path of nodes in order
        return ([(node_index,self.graph.node[node_index]) for node_index in self.list_nodes_visited],self.id)
    

    def __iteration__(self):
        ''' Perfoms just one single iteration., This is to simulate concurrency
        '''
        if self.current_node_id in self.solution_nodes_id:
            return ([(node_index,self.graph.node[node_index]) for node_index in self.list_nodes_visited],self.id)
        self.expand_node(self.current_node_id) 
        self.move_to_another_node()
        
        return (None,False)
        
    
    def expand_node(self, node_index_to_expand):
        
        ''' expand_node
            Parameters:
            node_index_to_expand: Index of node to expand
            
            Expands a node. (creates successor nodes
            and add edges from/to their parents and them).
        '''
        
        node_to_expand = self.graph.node[node_index_to_expand]['node']
        successors = self.aco_specific_problem.successors(node_to_expand.state)

        for s in successors:
            successor_index = self.aco_specific_problem.generate_node_hash(s)
            
            self.graph.add_node(successor_index) # we do this anyway to avoid a search
            
            if 'node' not in self.graph.node[successor_index].keys():
                self.graph.node[successor_index]['node'] = ACONode(s)
            
            # If the edge doesnt exists yet
            if successor_index not in self.graph.edge[node_index_to_expand].keys():
                self.graph.add_edge(node_index_to_expand,successor_index, weight=self.aco_specific_problem.initial_tau)    
                
            self.possible_new_edges = [(n1,n2,e) for (n1,n2,e) in self.graph.edges(self.current_node_id, data=True) if n2 != self.last_node_id]
    
            if self.aco_specific_problem.generate_node_hash(s) in self.solution_nodes_id:                
                self.solution_found = self.aco_specific_problem.generate_node_hash(s)

    def move_ant(self, node_index):
        ''' move_ant
        
            Parameters:
            node_index
            
            Moves the ant.
            This is called only by move_to_another_node, because that method has to check
            first for efficiency that the node where the ant is going has not been visited already
        
            Performs a local update of the pheromone
        '''
        # We obviate the last case
        if self.current_node_id not in self.solution_nodes_id:
            
            self.last_node_id = self.current_node_id
            self.current_node_id = node_index
                
            self.list_nodes_visited.append(node_index)
            
            # local update
            
            self.graph.edge[self.last_node_id][self.current_node_id]['weight'] *= (1-self.aco_specific_problem.p) 
            self.graph.edge[self.last_node_id][self.current_node_id]['weight'] += self.aco_specific_problem.p * self.aco_specific_problem.initial_tau
            
    
    def decision_table(self, node_index):
        
        ''' decision table
            (a sub ij)
            
            Parameters:
            node_index
        
            Returns:
            Dictionary (Key: Node, Value: Value of aij associated with that node)
            
            Given the index of a node, calculates and/or returns the decision table for the node.

        '''

        decision_table = dict() 
        summatory_denominator = 0
                  
        for edge in self.possible_new_edges:
         
            next_state = self.graph.node[edge[1]]['node'].state
            pheromone = edge[-1]['weight'] # tau i,j pheromone (evaporated)

            next_state_cost = self.aco_specific_problem.calculate_cost(next_state)

            # inverse of the cost of this potential new state
            # We check if the cost is 0 (hopefully) solution to avoid division by zero
            if next_state_cost != 0:
                nij = 1.0 / next_state_cost
            else:
                nij = sys.maxint
                
            numerator = math.pow(pheromone,self.aco_specific_problem.alpha) * math.pow(nij,self.aco_specific_problem.beta)
            summatory_denominator += numerator
            decision_table[edge[1]] = numerator

        # We apply now the division of the numerators

        decision_table.update((x,y/summatory_denominator) for x,y in decision_table.items())    

        self.decision_tables[node_index] = decision_table
        return decision_table
        
    def positive_feedback(self):
        ''' performs a positive feedback on the path
            once it has finished (found a solution)
        '''
        
        sol = self.list_nodes_visited
        positive_feedback = self.aco_specific_problem.pheromone_update_criteria(sol)
        
        #print ("hola soy "+ str(self.id) + " y voy a dar " + str(positive_feedback) + " de feedback a mi sol de "+ str(len(sol)))
        
        for node_index in range(len(sol)):
            
            if node_index == len(sol)-1:
                break
            
            this_node = sol[node_index]
            next_node = sol[node_index+1]
       
            self.graph.edge[this_node][next_node]['weight'] += positive_feedback

        
    def move_to_another_node(self):
        
        ''' move_to_another_node
            (Rule of transition)
            Parameters: 
            none
        
            Here the ant will decide where to move, based on the following rule of transition:
            
            (Given q, a random number in [0,1]
            and q0, a parameter of the problem:)
            
            if q <= q0 : The ant moves to the edge with more pheromone
            if q > q0  : The ant moves a randomly-chosen edge in proportion with its
            efficacy (eg. Heuristic)
        
        '''
        # If the solution is next, just go to it.
        
        if self.solution_found != None and self.current_node_id not in self.solution_nodes_id:
            self.move_ant(self.solution_found)
           
        q = random.random()

        # Proportional pseudo-random rule
          
        if q <= self.aco_specific_problem.q0:
            #print("Exploitation")
            # arg max aij
            
            decision_table = self.decision_table(self.current_node_id)

            next_node = max(decision_table.iteritems(), key=operator.itemgetter(1))[0]
            self.move_ant(next_node)
        
        
        else:      
            # Otherwise, we create a list of probabilities
            #print("Exploration")
            
            proportion_list = dict()    
            summatory_denominator = 0
            decision_table = self.decision_table(self.current_node_id)
            
            for e in self.possible_new_edges:    
                summatory_denominator += decision_table[e[1]]
            
            for node in decision_table.keys():
                proportion_list[node] = decision_table[node] / summatory_denominator
                         
            self.move_ant(self.get_prop_random_node(proportion_list))

    def get_prop_random_node(self, prop_list):
        
        ''' get_prop_random_node:
            Parameters: 
            prob_list (dictionary of proportions)
           
            This is to be called from "move_to_another_node"
        '''
        
        rand = random.random()
        acc = 0 # accumulator
        
        for node in prop_list.keys():
         
            if prop_list[node] + acc > rand:
                node_ret = node
                break
            acc += prop_list[node]
            
        return node_ret
    
              
    def draw_graph(self):
        
        pos=nx.spring_layout(self.graph)
        nx.draw(self.graph,pos,node_color='#A0CBE2',edge_color='#BB0000',width=2,with_labels=True)
        plt.show()