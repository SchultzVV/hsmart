from flask import Flask
from routes.query_routes import query_blueprint
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.register_blueprint(query_blueprint)

if __name__ == "__main__":
    print("🚀 Inicializando serviço de recuperação...")
    app.run(host="0.0.0.0", port=5004, debug=DEBUG_MODE)
