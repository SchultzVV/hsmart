from flask import Blueprint, request, jsonify
from services.ufsm_ingestor import (
    ingest_from_sitemap,
    ingest_all_courses_text,
    ingest_via_crawling,
    get_all_courses,
    ingest_ufsm_cursos_rag
)
from services.hotmart_ingestor import ingest_hotmart
from services.vector_ops import ingest_manual_text, list_collections, list_all_documents, delete_collection
from services.reprocess_log import reprocess_from_log
from services.ingest_faq_from_json import ingest_faq_from_jsonl

from services.ingest_from_web_loader import ingest_from_web_loader

ingest_blueprint = Blueprint("ingest", __name__)

## endpoint for ingestion operations with json data
@ingest_blueprint.route("/process_faq_json", methods=["POST"])
def process_faq_json():
    return ingest_faq_from_jsonl("data/ufsm_geral_dataset.jsonl", collection_name="ufsm_faqs")

@ingest_blueprint.route("/reprocess_log", methods=["POST"])
def reprocess_log_endpoint():
    return reprocess_from_log()

## endpoint for ingestion info from all ufsm web pages
@ingest_blueprint.route("/ingest_ufsm_cursos_rag", methods=["POST"])
def ingest_rag_ufsm():
    try:
        total = ingest_ufsm_cursos_rag()
        return jsonify({"message": f"Ingestão RAG finalizada com {total} chunks"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------------------
#### PRINCIPAL ENDPOINT PARA INGESTÃO DE DADOS WEB
## endpoint for ingestion operations with web loader
@ingest_blueprint.route("/ingest_from_url", methods=["POST"])
def ingest_from_url():
    return ingest_from_web_loader(request)

# -------------------------------------------------------------------------------


## endpoint for ingestion operations with sitemap
@ingest_blueprint.route("/ingest_ufsm", methods=["POST"])
def ingest_ufsm():
    return ingest_from_sitemap(request)

## endpoint for ingestion operations with all ufsm courses text
@ingest_blueprint.route("/ingest_ufsm_geral", methods=["POST"])
def ingest_ufsm_geral():
    return ingest_all_courses_text()

## endpoint for ingestion operations with crawling
@ingest_blueprint.route("/ingest_ufsm2", methods=["POST"])
def ingest_ufsm2():
    return ingest_via_crawling()



## endpoint for ingestion operations with Hotmart
@ingest_blueprint.route("/ingest_hotmart", methods=["POST"])
def ingest_hotmart_route():
    return ingest_hotmart()

## endpoint for manual ingestion of text
@ingest_blueprint.route("/ingest_manual", methods=["POST"])
def ingest_manual():
    return ingest_manual_text(request)

#-------------------------------------------------------------------------------
## endpoint for vector operations
@ingest_blueprint.route("/get_courses_list", methods=["GET"])
def get_courses_list():
    return get_all_courses()

## endpoint for listing all 
@ingest_blueprint.route("/list_collections", methods=["GET"])
@ingest_blueprint.route("/get_all_collections", methods=["GET"])
def list_all():
    return list_collections()

## endpoint for listing all documents in a collection
@ingest_blueprint.route("/get_all_documents", methods=["GET"])
def get_docs():
    return list_all_documents()

## endpoint for deleting a collection
@ingest_blueprint.route("/delete_collection", methods=["POST"])
def delete():
    return delete_collection(request)
