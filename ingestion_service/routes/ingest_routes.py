from flask import Blueprint, request, jsonify

from services.ufsm_ingestor import ingest_ufsm, get_courses_list
from services.general_dataset import ingest_ufsm_geral
from services.hotmart_ingestor import ingest_hotmart
from services.manual_ingestor import ingest_manual

ingest_blueprint = Blueprint("ingest", __name__)


@ingest_blueprint.route("/ingest_ufsm", methods=["POST"])
def route_ingest_ufsm():
    return ingest_ufsm(request)


@ingest_blueprint.route("/get_courses_list", methods=["GET"])
def route_get_courses_list():
    return get_courses_list()


@ingest_blueprint.route("/ingest_ufsm_geral", methods=["POST"])
def route_ingest_ufsm_geral():
    resultado = ingest_ufsm_geral()
    return jsonify(resultado), 200


@ingest_blueprint.route("/ingest_hotmart", methods=["POST"])
def route_ingest_hotmart():
    return ingest_hotmart()


@ingest_blueprint.route("/ingest_manual", methods=["POST"])
def route_ingest_manual():
    return ingest_manual(request)
