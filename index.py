from flask import Flask, redirect, render_template, request, url_for
from codecs import open
import os
from json import loads, dumps
import smtplib

app = Flask(__name__)

def link(*args):
    return os.path.join(os.path.dirname(__file__), *args)

def change_status(status):
    with open(link("status.json"), "w", encoding="utf-8") as f:
        f.write( status )

def get_status():
    with open(link("status.json"), "r", encoding="utf-8") as f:
        return f.read()

def pot_request( data ):
    if data["status"] == "was_watered":
        change_status("not_need")
    if data["status"] == "not_enough_water":
        change_status("no_water")
    
    
    with open(link("data.json"), "w", encoding="utf-8") as f:
        f.write( dumps(data) )
        
    with open(link("status.json"), "r", encoding="utf-8") as f:
        status = f.read()
        
    if status == "need" or status == "no_water":
        return "success-go"
    else:
        return "success-clear"
    

@app.route("/")
def index():
    status = get_status()
    return render_template("change-button.html", status = status)
    return "<a href='/change_status?status=water'>need watering</a><br><a href='/change_status?status=clear'>doesnt need water</a>"
    return redirect("http://super-pot.ru")

@app.route("/stats")
def stats():
    with open(link("data.json"), "r", encoding="utf-8") as f:
        data = loads(f.read())
    return render_template("stats.html", data=data)

@app.route("/r", methods=["POST"])
def r():
    """ requests from pot """
    try:
        json = request.get_json()
        return pot_request( json )
    except Exception as e:
        return "error " + str(e)

@app.route("/change_status")
def change_s():
    change_status(request.args['status'])
    return redirect("/")
    return "success"

@app.route("/mail", methods=["POST", "GET"])
def mail():
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login("vlzhr.nots", "gorshok2018")
    msg = "\r\n".join([
  "From: vlzhr.nots@gmail.com",
  "To: vlzhr.nots@gmail.com",
  "Subject: smart-pot notification",
  "",
  request.get_json()["text"]
  ])
    server.sendmail("vlzhr.nots@gmail.com", "vlzhr.nots@gmail.com", msg)
    return ""

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response


if __name__ == "__main__":
    app.run()

