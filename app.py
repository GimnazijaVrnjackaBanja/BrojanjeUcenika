from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, time
import schedule
import threading
from threading import Timer

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "secret!"
db = SQLAlchemy(app)
socketio = SocketIO(app)


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


@socketio.on("update")
def handle_update():
    print("Server received update request")
    prisutni_brojaci = Counter.query.all()
    ukupno_prisutnih = sum(counter.count for counter in prisutni_brojaci)
    emit(
        "update",
        {"counters": prisutni_brojaci, "ukupno_prisutnih": ukupno_prisutnih},
        broadcast=True,
    )


@app.route("/Prijava/<counter_name>", methods=["POST"])
def Prijava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter:
        counter.count += 1
        counter.datumvreme = datetime.now()
        db.session.commit()

        # Dodavanje novog reda u bazi za svaku prijavu
        new_entry = Detaljno(
            imebrojaca=counter_name, vrednostbrojaca=1, datumvreme=datetime.now()
        )
        db.session.add(new_entry)
        db.session.commit()

    socketio.emit("update")
    print("Emitting update prijave")  # Provera prijave

    return redirect(url_for("index"))


@app.route("/Odjava/<counter_name>", methods=["POST"])
def Odjava(counter_name):
    counter = Counter.query.filter_by(name=counter_name).first()
    if counter and counter.count > 0:
        counter.count -= 1
        counter.datumvreme = datetime.now()

        # Dodavanje novog reda u bazi za svaku odjavu
        new_entry = Detaljno(
            imebrojaca=counter_name, vrednostbrojaca=-1, datumvreme=datetime.now()
        )
        db.session.add(new_entry)
        db.session.commit()

    socketio.emit("update")
    print("Emitting update odjave")  # Provera odjave

    return redirect(url_for("index"))


def reset_counters():
    with app.app_context():
        counters = Counter.query.all()
        for counter in counters:
            counter.count = 0
            counter.datumvreme = datetime.now()
        db.session.commit()
        socketio.emit("update")
        print("Brojači su resetovani.")


# Funkcija za postavljanje periodičnog zadatka za resetovanje brojača u ponoć
def set_midnight_reset():
    now = datetime.now()
    midnight = datetime(now.year, now.month, now.day, 20, 33, 0)
    delta = midnight - now
    seconds_until_midnight = delta.total_seconds()

    # Postavljanje periodičnog zadatka
    timer = Timer(seconds_until_midnight, reset_counters)
    timer.start()


# Pozivamo funkciju da postavi periodični zadatak
set_midnight_reset()

# Ovo je bila prva varijanta sa schedule modulom
# Postavljanje rasporeda za resetovanje brojača svaki dan u ponoć
# schedule.every().day.at("00:00").do(reset_counters)


# Funkcija za pokretanje redovnih zadataka u odvojenom thread-u
# def run_scheduler():
#    while True:
#        schedule.run_pending()
#        time.sleep(1)


if __name__ == "__main__":
    # scheduler_thread = threading.Thread(target=run_scheduler)
    # scheduler_thread.start()

    # app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0')
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
