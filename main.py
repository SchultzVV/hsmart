from flask import Flask
from routes.ingest_routes import ingest_blueprint
from routes.utils_routes import utils_blueprint

app = Flask(__name__)
app.register_blueprint(ingest_blueprint)
app.register_blueprint(utils_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
