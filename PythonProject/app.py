from sys import dllhandle
from tkinter import W
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column
import googlemaps
import numpy as np
import datetime
import random
import itertools

def oneDArray(x):
    return list(itertools.chain(*x))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

class Wspolrzedne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    dlugosc = db.Column(db.Float(100), nullable=False)
    szerokosc = db.Column(db.Float(100), nullable=False)


n_population = 100

mutation_rate = 0.3

API_KEY = "API"

client = googlemaps.Client(API_KEY)

def compute_city_distance_coordinates(a,b):
    lok1 = str(a[0])+','+str(a[1])
    lok2 = str(b[0])+','+str(b[1])
    directions_result = client.directions(origin=lok1,
                                      destination=lok2,
                                      mode="driving",
                                      avoid="ferries")

    
    return directions_result[0]['legs'][0]['distance']['value']

def compute_city_distance_names(city_a, city_b, cities_dict):
    return compute_city_distance_coordinates(cities_dict[city_a], cities_dict[city_b])

def fitness_eval(city_list, cities_dict, n_cities):
    total = 0
    for i in range(n_cities-1):
        a = city_list[i]
        b = city_list[i+1]
        total += compute_city_distance_names(a,b, cities_dict)
    return total

def get_all_fitnes(population_set, cities_dict):
    fitnes_list = np.zeros(n_population)

    #Looping over all solutions computing the fitness for each solution
    for i in  range(n_population):
        fitnes_list[i] = fitness_eval(population_set, cities_dict, Wspolrzedne.query.count())
    print(population_set)
    return fitnes_list

def progenitor_selection(population_set,fitnes_list):
    total_fit = fitnes_list.sum()
    prob_list = fitnes_list/total_fit
    
    #Notice there is the chance that a progenitor. mates with oneself
    progenitor_list_a = np.random.choice(population_set, len(population_set), p = prob_list, replace = True)
    progenitor_list_b = np.random.choice(population_set, len(population_set), p = prob_list, replace = True)
    
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

def mutate_offspring(offspring, n_cities):
    for q in range(int(n_cities*mutation_rate)):
        a = np.random.randint(0,n_cities)
        b = np.random.randint(0,n_cities)

        offspring[a], offspring[b] = offspring[b], offspring[a]

    return offspring
      
def mutate_population(new_population_set):
    mutated_pop = []
    for offspring in new_population_set:
        mutated_pop.append(mutate_offspring(offspring))
    return mutated_pop

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
       name = request.form['name']
       dlugosc = request.form['dlugosc']
       szerokosc = request.form['szerokosc']
       task = Wspolrzedne(name=name, dlugosc=dlugosc, szerokosc=szerokosc) 

       db.session.add(task)
       db.session.commit()
       return redirect('/')
    else:
        tasks = Wspolrzedne.query.all()
        return render_template("index.hbs", tasks=tasks)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update (id):
    task = Wspolrzedne.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        db.session.commit()
        return redirect('/')
    else:
        return render_template('update.hbs', task=task)

@app.route('/result', methods=['GET', 'POST'])
def result():
    n_cities = Wspolrzedne.query.count()
    names_list  = []
    cordinates_list = []
    population_set = []
    for i in range(Wspolrzedne.query.count()):
        row = list(db.session.query(Wspolrzedne.name).filter(Wspolrzedne.id == i + 1))
        names_list.append(list(row[0]))
        row = list(db.session.query(Wspolrzedne.dlugosc, Wspolrzedne.szerokosc).filter(Wspolrzedne.id == i + 1))
        cordinates_list.append(list(row[0]))
    
    names_list = oneDArray(names_list)

    cities_dict = { x:y for x,y in zip(names_list, cordinates_list) }

    population_set = names_list * n_population

    fitnes_list = get_all_fitnes(population_set,cities_dict)

    progenitor_list = progenitor_selection(population_set,fitnes_list)

    new_population_set = mate_population(progenitor_list)

    mutated_pop = mutate_population(new_population_set)

    best_solution = [-1,np.inf,np.array([])]

    for i in range(1000):
        if i%100==0: print(i, fitnes_list.min(), fitnes_list.mean(), datetime.now().strftime("%d/%m/%y %H:%M"))
        fitnes_list = get_all_fitnes(mutated_pop,cities_dict)
        
        #Saving the best solution
        if fitnes_list.min() < best_solution[1]:
            best_solution[0] = i
            best_solution[1] = fitnes_list.min()
            best_solution[2] = np.array(mutated_pop)[fitnes_list.min() == fitnes_list]
        
        progenitor_list = progenitor_selection(population_set,fitnes_list)
        new_population_set = mate_population(progenitor_list)
        
        mutated_pop = mutate_population(new_population_set)
    print(best_solution)
    return render_template('result.hbs')
if __name__ == "__main__":
    app.run(debug=True)
