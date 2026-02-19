from flask import Flask, render_template

from pipeline import run_all

app = Flask(__name__)


@app.route("/api/cron", methods=["GET"])
def cron():
    run_all()
    return {"status": "ok"}


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")
