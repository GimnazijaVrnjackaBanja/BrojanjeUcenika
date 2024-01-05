from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    count = db.Column(db.Integer, default=0)
    datumvreme = db.Column(db.DateTime, default=datetime.now)

class Detaljno(db.Model):
    iddetaljno = db.Column(db.Integer, primary_key=True)
    imebrojaca = db.Column(db.String(20), nullable=False, unique=False)
    vrednostbrojaca = db.Column(db.Integer, default=0)
    datumvreme = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    prisutni_brojaci = Counter.query.all()
    ukupno_prisutnih = sum(counter.count for counter in prisutni_brojaci)
    return render_template(
        "index.html", counters=prisutni_brojaci, ukupno_prisutnih=ukupno_prisutnih
    )


@app.route("/Prijava/<counter_name>", methods=["POST"])
def Prijava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter:
        counter.count += 1
        counter.datumvreme = datetime.now()
        db.session.commit()

        # Dodavanje novog reda u bazi za svaku prijavu
        new_entry = Detaljno(imebrojaca=counter_name, vrednostbrojaca=1, datumvreme=datetime.now())
        db.session.add(new_entry)
        db.session.commit()

    return redirect(url_for("index"))


@app.route("/Odjava/<counter_name>", methods=["POST"])
def Odjava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter and counter.count > 0:
        counter.count -= 1
        counter.datumvreme = datetime.now()

        # Dodavanje novog reda u bazi za svaku odjavu
        new_entry = Detaljno(imebrojaca=counter_name, vrednostbrojaca=-1, datumvreme=datetime.now())
        db.session.add(new_entry)
        db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
