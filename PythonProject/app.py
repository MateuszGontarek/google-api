from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column
import itertools
import genetic

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

@app.route('/delete')
def delete():
    db.session.query(Wspolrzedne).delete()
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_task(id):
    task = Wspolrzedne.query.get(id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

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
    listId = []
    for i in db.session.query(Wspolrzedne.id).all():
        listId.append(list(i)[0])

    for i in listId:
        
        row = list(db.session.query(Wspolrzedne.name).filter(Wspolrzedne.id == i))
        names_list.append(list(row[0]))

        row = list(db.session.query(Wspolrzedne.dlugosc, Wspolrzedne.szerokosc).filter(Wspolrzedne.id == i))
        cordinates_list.append(list(row[0]))

    names_list = oneDArray(names_list)

    cities_dict = { x:y for x,y in zip(names_list, cordinates_list) }

    returnValue = genetic.finish(n_cities, names_list, cities_dict)
     
    tasks = []

    for i in range(len(returnValue)):
        if returnValue[i] in cities_dict.keys():
            row = returnValue[i], cities_dict[returnValue[i]][0], cities_dict[returnValue[i]][1]
            tasks.append(list(row))

    print(tasks)
    url = "https://www.google.pl/maps/dir/"
    for i in range(len(returnValue)):
        url += str(cities_dict[returnValue[i]][0]) + "," + str(cities_dict[returnValue[i]][1]) + "/"
    url +=  str(cities_dict[returnValue[0]][0]) + "," + str(cities_dict[returnValue[0]][1])
    print(url)
    return render_template('result.hbs', task=tasks, url=url)
if __name__ == "__main__":
    app.run(debug=True)
