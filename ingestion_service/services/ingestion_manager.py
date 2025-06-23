import os
import json
import logging
from pathlib import Path
from datetime import datetime
from langchain_core.documents import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader, PlaywrightURLLoader
from shared.langchain_container import LangChainContainer

logger = logging.getLogger(__name__)


class IngestionManager:
    def __init__(self, collection_name="web_geral_loader", chunk_size=800, chunk_overlap=100):
        self.container = LangChainContainer()
        self.client = self.container.qdrant_client
        self.embedding_model = self.container.embedding_model
        self.vectorstore = self.container.vectorstore
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.collection_name = collection_name
        self.skipped_docs = []
        self.log_dir = Path("logs/ingest")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def load_url(self, url):
        try:
            logger.info(f"🌐 Trying UnstructuredURLLoader: {url}")
            loader = UnstructuredURLLoader(urls=[url])
            return loader.load(), "unstructured"
        except Exception as e1:
            logger.warning(f"⚠️ UnstructuredURLLoader failed: {e1}")
            try:
                logger.info("🔁 Fallback to PlaywrightURLLoader...")
                loader = PlaywrightURLLoader(urls=[url], remove_selectors=["nav", "footer", "script"])
                return loader.load(), "playwright"
            except Exception as e2:
                raise RuntimeError(f"🛑 Failed both loaders. Unstructured: {e1} | Playwright: {e2}")

    def ingest_url(self, url):
        try:
            docs, loader_used = self.load_url(url)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar URL {url}: {e}")
            return {"error": str(e)}, 500
    
        if not docs:
            return {"error": "❌ Nenhum documento extraído."}, 204
    
        logger.info(f"📄 {len(docs)} documentos carregados de {url}")
        logger.info(f"🔍 Iniciando ingestão na coleção: {self.collection_name}")
    
        chunks = []
        for doc in docs:
            doc_chunks = self.splitter.split_documents([doc])
            if not doc_chunks or all(len(c.page_content.strip()) < 20 for c in doc_chunks):
                self.skipped_docs.append({
                    "url": url,
                    "reason": "Empty or too short after chunking",
                    "timestamp": datetime.now().isoformat()
                })
                continue
            chunks.extend(doc_chunks)
    
        if not chunks:
            return {"error": "Todos os documentos foram descartados após o chunking."}, 204
    
        try:
            self.container.set_collection(self.collection_name)
            vectorstore = self.container.vectorstore
    
            if vectorstore is None:
                raise RuntimeError("Vectorstore não foi inicializado corretamente.")
    
            vectorstore.add_documents(chunks)
            self._save_skipped_log()
    
            return {
                "message": f"{len(chunks)} chunks ingeridos na coleção `{self.collection_name}`.",
                "loader": loader_used,
                "skipped": len(self.skipped_docs)
            }, 200
    
        except Exception as e:
            logger.error(f"❌ Falha ao salvar documentos na coleção `{self.collection_name}`: {e}")
            return {"error": "Erro ao salvar documentos."}, 500

    # def ingest_url(self, url):
    #     try:
    #         docs, loader_used = self.load_url(url)
    #     except Exception as e:
    #         return {"error": str(e)}, 500

    #     if not docs:
    #         return {"error": "❌ No documents extracted."}, 204

    #     logger.info(f"📄 {len(docs)} documents loaded from {url}")
    #     # self.container.set_collection(self.collection_name)
    #     logger.info(f"🔍 Ingesting into collection: {self.collection_name}")
    #     chunks = []
    #     for doc in docs:
    #         doc_chunks = self.splitter.split_documents([doc])
    #         if not doc_chunks or all(len(c.page_content.strip()) < 20 for c in doc_chunks):
    #             self.skipped_docs.append({
    #                 "url": url,
    #                 "reason": "Empty or too short after chunking",
    #                 "timestamp": datetime.now().isoformat()
    #             })
    #             continue
    #         chunks.extend(doc_chunks)

    #     if not chunks:
    #         return {"error": "Todos os documentos foram descartados após chunking."}, 204

    #     self.container.set_collection(self.collection_name)
        
    #     self.vectorstore.add_documents(chunks)
        
    #     self._save_skipped_log()

    #     return {
    #         "message": f"{len(chunks)} chunks ingeridos na coleção `{self.collection_name}`.",
    #         "loader": loader_used,
    #         "skipped": len(self.skipped_docs)
    #     }, 200

    def _save_skipped_log(self):
        if self.skipped_docs:
            log_path = self.log_dir / f"skipped_docs_{self.collection_name}.json"
            with log_path.open("w", encoding="utf-8") as f:
                json.dump(self.skipped_docs, f, indent=2, ensure_ascii=False)
            logger.info(f"📝 Skipped docs log salvo em {log_path}")
    
    def batch_ingest_urls(self, urls, max_workers=5):
        """Ingesta múltiplas URLs em paralelo"""
        results = []
        logger.info(f"🚀 Iniciando ingestão paralela de {len(urls)} URLs...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.ingest_url, url): url for url in urls}
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result, status = future.result()
                    logger.info(f"✅ Ingestão de {url} finalizada com status {status}")
                    results.append({
                        "url": url,
                        "status": status,
                        "result": result
                    })
                except Exception as e:
                    logger.error(f"❌ Falha na ingestão de {url}: {e}")
                    results.append({
                        "url": url,
                        "status": 500,
                        "result": {"error": str(e)}
                    })
        return results
