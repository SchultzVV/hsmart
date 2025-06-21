# from flask import Blueprint, jsonify, request
# from qdrant_client import QdrantClient
# import logging

# utils_blueprint = Blueprint("utils", __name__)
# client = QdrantClient(host="vector_db", port=6333)


# @utils_blueprint.route('/get_all_collections', methods=['GET'])
# def get_all_collections():
#     try:
#         collections = client.get_collections()
#         collection_names = [collection.name for collection in collections.collections]
#         return jsonify({"collections": collection_names}), 200
#     except Exception as e:
#         logging.error(f"Erro ao listar coleções: {e}")
#         return jsonify({"error": str(e)}), 500


# @utils_blueprint.route('/get_all_documents', methods=['GET'])
# def get_all_documents():
#     try:
#         collections = client.get_collections()
#         resultado = {}

#         for collection in collections.collections:
#             collection_name = collection.name
#             scroll_result = client.scroll(collection_name=collection_name, limit=100)
#             documents = [point.payload for point in scroll_result[0]]
#             resultado[collection_name] = documents

#         return jsonify({"collections": resultado}), 200

#     except Exception as e:
#         logging.error(f"Erro ao buscar documentos: {e}")
#         return jsonify({"error": str(e)}), 500


# @utils_blueprint.route('/delete_collection', methods=['POST'])
# def delete_collection():
#     data = request.get_json()

#     if not data or "collection" not in data:
#         return jsonify({"error": "O campo 'collection' é obrigatório"}), 400

#     collection_name = data["collection"]

#     try:
#         if client.collection_exists(collection_name):
#             client.delete_collection(collection_name=collection_name)
#             return jsonify({"message": f"Coleção `{collection_name}` deletada com sucesso."}), 200
#         else:
#             return jsonify({"error": f"A coleção `{collection_name}` não existe."}), 404

#     except Exception as e:
#         logging.error(f"Erro ao deletar coleção: {e}")
#         return jsonify({"error": str(e)}), 500