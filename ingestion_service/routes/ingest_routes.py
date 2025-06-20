from flask import Blueprint, request, jsonify
from services.ufsm_ingestor import (
    ingest_from_sitemap,
    ingest_all_courses_text,
    ingest_via_crawling,
    ingest_from_web_loader,
    get_all_courses,
    ingest_ufsm_cursos_rag
)
from services.hotmart_ingestor import ingest_hotmart
from services.vector_ops import ingest_manual_text, list_collections, list_all_documents, delete_collection

ingest_blueprint = Blueprint("ingest", __name__)

@ingest_blueprint.route("/ingest_ufsm_cursos_rag", methods=["POST"])
def ingest_rag_ufsm():
    try:
        total = ingest_ufsm_cursos_rag()
        return jsonify({"message": f"Ingestão RAG finalizada com {total} chunks"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ingest_blueprint.route("/ingest_ufsm", methods=["POST"])
def ingest_ufsm():
    return ingest_from_sitemap(request)

@ingest_blueprint.route("/ingest_ufsm_geral", methods=["POST"])
def ingest_ufsm_geral():
    return ingest_all_courses_text()

@ingest_blueprint.route("/ingest_ufsm2", methods=["POST"])
def ingest_ufsm2():
    return ingest_via_crawling()

@ingest_blueprint.route("/ingest_from_url", methods=["POST"])
def ingest_from_url():
    return ingest_from_web_loader(request)

@ingest_blueprint.route("/ingest_hotmart", methods=["POST"])
def ingest_hotmart_route():
    return ingest_hotmart()

@ingest_blueprint.route("/ingest_manual", methods=["POST"])
def ingest_manual():
    return ingest_manual_text(request)

@ingest_blueprint.route("/get_courses_list", methods=["GET"])
def get_courses_list():
    return get_all_courses()

@ingest_blueprint.route("/list_collections", methods=["GET"])
@ingest_blueprint.route("/get_all_collections", methods=["GET"])
def list_all():
    return list_collections()

@ingest_blueprint.route("/get_all_documents", methods=["GET"])
def get_docs():
    return list_all_documents()

@ingest_blueprint.route("/delete_collection", methods=["POST"])
def delete():
    return delete_collection(request)
