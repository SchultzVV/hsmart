from flask import Flask
from routes.ingest_routes import ingest_blueprint
import logging
import sys
import os

# Configuração de logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Inicialização do app
app = Flask(__name__)
app.register_blueprint(ingest_blueprint)

if __name__ == '__main__':
    print("🚀 Inicializando serviço de ingestão...")
    app.run(host="0.0.0.0", port=5003, debug=DEBUG_MODE)
