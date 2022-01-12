from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from guides_sql import *
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db: SQLAlchemy = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text(200))
    last_name = db.Column(db.Text(200))
    age =  db.Column(db.Integer)
    email = db.Column(db.Text(30))
    role = db.Column(db.Text(200))
    phone = db.Column(db.Text(20))


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    order = db.relationship("Order")
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor = db.relationship("User")


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(200))
    description = db.Column(db.Text(300))
    start_date = db.Column(db.Text(300))
    end_date = db.Column(db.Text(300))
    address = db.Column(db.Text(300))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer = db.relationship("User")


def load_data(model, table):
    with open(table, 'r') as f:
        data = json.load(f)
    for el in data:
        element = model(**el)
        db.session.add(element)
    db.session.commit()


@app.route('/<string:model>/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def get_element(model, id):
    if model == "users":
        Model = User
    elif model == "orders":
        Model = Order
    elif model == "offers":
        Model = Offer
    else:
        return "Нет такой страницы"
    columns = [el.name for el in Model.__table__.columns if el.name != "id"]
    if request.method == "PUT":
        request_data = json.load(request.data)
        element =  Model.query.get(id)
        for column in columns:
            element.column = request_data[column]
        db.session.add(element)
        db.session.commit()
    elif request.method == "DELETE":
        element = Model.query.get(id)
        db.session.delete(element)
        db.session.commit()
    return render_template('element.html', columns = columns, element = Model.query.get(id))


@app.route('/<string:model>',  methods=['GET', 'POST'])
def elements(model):
    Model = db.Model
    if model == "users":
        Model = User
    elif model == "orders":
        Model = Order
    elif model == "offers":
        Model = Offer
    else:
        return "Нет такой страницы"
    columns = [el.name for el in Model.__table__.columns]
    if request.method == "POST":
        new_element = {}
        for column in columns:
            new_element[column] = request.form.get(column)
        db.session.add(Model(**new_element))
        db.session.commit()
    return render_template('table.html', columns=columns, elements =[row.__dict__ for row in db.session.query(Model)])


if __name__ == "__main__":
    db.create_all()
    session = db.session()
    load_data(User, "Users.json")
    load_data(Offer,"Offers.json")
    load_data(Order,"Orders.json")
    app.run(debug=True)



