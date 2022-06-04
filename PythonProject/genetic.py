import numpy as np
from datetime import datetime
import googlemaps
import itertools

n_population = 100
mutation_rate = 0.3
DistanceList = []
API_KEY = "API"

client = googlemaps.Client(API_KEY)

def oneDArray(x):
    return list(itertools.chain(*x))

def compute_city_distance_coordinates(a,b):
    for i in range(len(DistanceList)):
        if a == DistanceList[i][1] and b == DistanceList[i][2]:
            return DistanceList[i][0]
    lok1 = str(a[0])+','+str(a[1])
    lok2 = str(b[0])+','+str(b[1])
    directions_result = client.directions(origin=lok1,
                                      destination=lok2,
                                      mode="driving",
                                      avoid="ferries")
                                      
    toAppend = directions_result[0]['legs'][0]['distance']['value'], a, b
    toAppend = list(toAppend)
    DistanceList.append(toAppend)

    return directions_result[0]['legs'][0]['distance']['value'] 

def compute_city_distance_names(city_a, city_b, cities_dict):
    return compute_city_distance_coordinates(cities_dict[city_a], cities_dict[city_b])

def genesis(city_list, n_population, n_cities):

    population_set = []
    for i in range(n_population):
        city_list = np.array(city_list)
        #Randomly generating a new solution
        sol_i = city_list[np.random.choice(list(range(n_cities)), n_cities, replace=False)]
        population_set.append(sol_i)
    return np.array(population_set)

def fitness_eval(city_list, cities_dict, n_cities):
    total = 0
    for i in range(n_cities-1):
        a = city_list[i]
        b = city_list[i+1]
        total += compute_city_distance_names(a,b, cities_dict)
    return total

def get_all_fitnes(population_set, cities_dict, n_cities):
    fitnes_list = np.zeros(n_population)

    #Looping over all solutions computing the fitness for each solution
    for i in  range(n_population):
        fitnes_list[i] = fitness_eval(population_set[i], cities_dict, n_cities)

    return fitnes_list

def progenitor_selection(population_set,fitnes_list):
    total_fit = fitnes_list.sum()
    prob_list = fitnes_list/total_fit

    #Notice there is the chance that a progenitor. mates with oneself
    progenitor_list_a = np.random.choice(list(range(len(population_set))), len(population_set),p=prob_list, replace=True)
    progenitor_list_b = np.random.choice(list(range(len(population_set))), len(population_set),p=prob_list, replace=True)
    
    progenitor_list_a = population_set[progenitor_list_a]
    progenitor_list_b = population_set[progenitor_list_b]
    
    
    return np.array([progenitor_list_a,progenitor_list_b])

def mate_progenitors(prog_a, prog_b):
    offspring = prog_a[0:5]

    for city in prog_b:

        if not city in offspring:
            offspring = np.concatenate((offspring,[city]))

    return offspring
            
def mate_population(progenitor_list):
    new_population_set = []
    for i in range(progenitor_list.shape[1]):
        prog_a, prog_b = progenitor_list[0][i], progenitor_list[1][i]
        offspring = mate_progenitors(prog_a, prog_b)
        new_population_set.append(offspring)
        
    return new_population_set

def mutate_offspring(offspring , n_cities):
    for q in range(int(n_cities*mutation_rate)):
        a = np.random.randint(0,n_cities)
        b = np.random.randint(0,n_cities)

        offspring[a], offspring[b] = offspring[b], offspring[a]

    return offspring
      
def mutate_population(new_population_set, n_cities):
    mutated_pop = []
    for offspring in new_population_set:
        mutated_pop.append(mutate_offspring(offspring, n_cities))
    return mutated_pop
def finish(n_cities, names_list, cities_dict):

    population_set = genesis(names_list, n_population, n_cities)

    fitnes_list = get_all_fitnes(population_set,cities_dict, n_cities)

    progenitor_list = progenitor_selection(population_set,fitnes_list)

    new_population_set = mate_population(progenitor_list)

    mutated_pop = mutate_population(new_population_set, n_cities)

    best_solution = [-1,np.inf,np.array([])]
    for i in range(100):
        if i%100==0: print(i, fitnes_list.min(), fitnes_list.mean(), datetime.now().strftime("%d/%m/%y %H:%M"))
        fitnes_list = get_all_fitnes(mutated_pop,cities_dict, n_cities)
        
        #Saving the best solution
        if fitnes_list.min() < best_solution[1]:
            best_solution[0] = i
            best_solution[1] = fitnes_list.min()
            best_solution[2] = np.array(mutated_pop)[fitnes_list.min() == fitnes_list]
        
        progenitor_list = progenitor_selection(population_set,fitnes_list)
        new_population_set = mate_population(progenitor_list)
        
        mutated_pop = mutate_population(new_population_set, n_cities)
    best_solution[2]  = best_solution[2].tolist()

    return best_solution[2][0]
