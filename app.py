from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)


class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    count = db.Column(db.Integer, default=0)


with app.app_context():
    db.create_all()

"""
@app.route("/")
def index():
    counters = Counter.query.all()
    return render_template("index.html", counters=counters)

@app.route("/Prijava/<counter_name>", methods=["POST"])
def Prijava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter:
        counter.count += 1
        db.session.commit()
    return redirect(url_for("index"))

"""


@app.route("/")
def index():
    """
    counters = Counter.query.all()
    return render_template("index.html", counters=counters)
    """
    prisutni_brojaci = Counter.query.all()
    ukupno_prisutnih = sum(counter.count for counter in prisutni_brojaci)
    return render_template("index.html", counters=prisutni_brojaci, ukupno_prisutnih=ukupno_prisutnih)



@app.route("/Prijava/<counter_name>", methods=["POST"])
def Prijava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter:
        counter.count += 1
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/Odjava/<counter_name>", methods=["POST"])
def Odjava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter and counter.count > 0:
        counter.count -= 1
        db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
