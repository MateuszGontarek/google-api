from datetime import datetime
from sys import dllhandle
from tkinter import W
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column
import googlemaps
API_KEY = ""
 
 
 
client = googlemaps.Client(API_KEY)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

def Algorytm(lista, lenght):
    obecnaLok = lista[0][1]
    listaReturn = []
    listaLokGood = []
    for i in range(lenght):
        for j in lista:
            if j[1] == obecnaLok:
                listaLokGood.append(j)
                lista.remove(j)

        print(lista)
        print(listaLokGood)
        listaReturn.append(obecnaLok)
        mini = min(listaLokGood, key=lambda x: x[0])
        obecnaLok = mini[2]
        print(obecnaLok)
        listaLokGood = []
    print(listaReturn)
            


class Wspolrzedne(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    dlugosc = db.Column(db.Float(100), nullable=False)
    szerokosc = db.Column(db.Float(100), nullable=False)

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
    lista = []
    DistanceList = []
    for i in range(Wspolrzedne.query.count()):
        row = list(db.session.query(Wspolrzedne.name, Wspolrzedne.dlugosc, Wspolrzedne.szerokosc).filter(Wspolrzedne.id == i + 1))
        lista.append(list(row[0]))

    for i in lista:
        for j in lista:
            if not i == j:
                lok1 = str(i[1]) + ',' + str(i[2])
                lok2 = str(j[1]) + ',' + str(j[2])
                directions_result = client.directions(origin=lok1,
                                      destination=lok2,
                                      mode="driving",
                                      avoid="ferries")

                distance = directions_result[0]['legs'][0]['distance']['text'].split()
                row = float(distance[0]), i[0], j[0]
                DistanceList.append(row)
    Algorytm(DistanceList, len(lista))
    return render_template('result.hbs')
if __name__ == "__main__":
    app.run(debug=True)