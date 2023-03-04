from flask import Flask, request, render_template, current_app
from api import api as api_bp

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(api_bp)


@app.route('/')
def hello_world():
    return render_template("map.html", config=current_app.config)


if __name__ == '__main__':
    app.run()
