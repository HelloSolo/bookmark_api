from flask import Flask

app = Flask(__name__)


@app.get("/")
def index():
    return "Hello Word"


@app.get("/hello")
def say_hello():
    return {"message": "Hello World"}
