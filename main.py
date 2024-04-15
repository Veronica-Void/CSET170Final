from flask import Flask, render_template, request, redirect  # imported flask
from sqlalchemy import create_engine, text

c_str = "mysql://root:password@localhost/database"
engine = create_engine(c_str, echo=True)
connection = engine.connect()
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello"

if __name__ == '__main__':
    app.run(debug=True)
    