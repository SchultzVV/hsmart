import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from flask import jsonify
from urllib.parse import urljoin
from collections import deque
# from unidecode import unidecode
from langchain_community.vectorstores import Qdrant
from shared.langchain_container import LangChainContainer

container = LangChainContainer()
client = container.qdrant_client
embedding_model = container.embedding_model

import json
import logging
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from shared.langchain_container import LangChainContainer

logger = logging.getLogger(__name__)

def extract_xml_urls(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        return [
            (loc.text, root.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"))
            for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        ]
    except Exception as e:
        logger.warning(f"Erro ao processar {sitemap_url}: {e}")
        return []

def is_recent(lastmod_text, years=2):
    if not lastmod_text:
        return True
    try:
        lastmod = datetime.fromisoformat(lastmod_text.replace("Z", "+00:00"))
        return (datetime.now() - lastmod).days < years * 365
    except Exception:
        return True

def extract_page_text(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, ""
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "Sem título"
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 50]
        return title, "\n".join(paragraphs)
    except Exception as e:
        logger.warning(f"Erro ao extrair texto de {url}: {e}")
        return None, ""

def get_course_type_from_url(url):
    if "/graduacao/" in url:
        return "graduacao"
    if "/pos-graduacao/" in url or "/posgraduacao/" in url:
        return "posgraduacao"
    if "/educacao-a-distancia/" in url:
        return "ead"
    return "desconhecido"

def get_campus_from_url(url):
    parts = url.split("/cursos/graduacao/")
    if len(parts) > 1:
        sub = parts[1].split("/")
        return sub[0].replace("-", " ").title()
    return "Desconhecido"

def get_course_name_from_url(url):
    try:
        return url.split("/cursos/graduacao/")[-1].split("/")[1].replace("-", " ").title()
    except Exception:
        return "Desconhecido"

def ingest_ufsm_cursos_rag():# esse é o bolado que tá rolando  certo
    print("🚀 Iniciando ingestão RAG de cursos da UFSM via sitemap...")
    container = LangChainContainer()
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    all_chunks = []
    curso_logs = {}
    stop = False

    response = requests.get("https://www.ufsm.br/robots.txt")
    sitemap_links = [line.split(": ")[1] for line in response.text.splitlines() if line.lower().startswith("sitemap:")]
    course_sitemaps = [url for url in sitemap_links if "/cursos/" in url]

    print(f"🔎 Encontrados {len(course_sitemaps)} sitemaps de cursos...")
    a,b,c = 0,0,0
    for sitemap in course_sitemaps:
        if stop:
            print("🔴 Ingestão interrompida pelo usuário.")
            break
        curso = get_course_name_from_url(sitemap)
        campus = get_campus_from_url(sitemap)
        tipo = get_course_type_from_url(sitemap)
        a+=1
        logger.debug(a)
        curso_logs[curso] = {
            "campus": campus,
            "nivel": tipo,
            "urls_acessadas": []
        }

        print(f"➡️ Processando curso: {curso} | campus: {campus} | tipo: {tipo}")
        logger.info(f"🎓 Curso: {curso} | Campus: {campus} | Nível: {tipo}")

        sub_sitemaps = extract_xml_urls(sitemap)
        logger.debug(f"🔍 {len(sub_sitemaps)} sub-sitemaps encontrados para {curso}")

        for sub_url, _ in sub_sitemaps:
            b+=1
            logger.debug(b)
            if not sub_url or not sub_url.endswith(".xml"):
                continue

            sub_sub_sitemaps = extract_xml_urls(sub_url)
            logger.debug(f"🔍 {len(sub_sub_sitemaps)} sub-sub-sitemaps em {sub_url}")

            for page_url, lastmod in sub_sub_sitemaps:
                c+=1
                logger.debug(c)
                if not page_url or page_url.endswith(".xml"):
                    continue
                if not is_recent(lastmod.text if lastmod is not None else None):
                    continue

                title, content = extract_page_text(page_url)
                if not content:
                    continue
                if c == 100:
                    logger.debug("🔴 Limite de 100 páginas atingido, interrompendo ingestão.")
                    logger.debug("🔴(DESLIGADO O STOP, pra ligar faz stop=true)🔴")
                    stop=False
                    break
                print(f"  ✅ Página acessada: {page_url}")
                logger.debug(f"📄 {title} | URL: {page_url}")
                logger.debug(f"a = {a} ")
                logger.debug(f"b = {b} ")
                logger.debug(f"c = {c} ")

                curso_logs[curso]["urls_acessadas"].append(page_url)

                metadados = [{
                    "curso": curso,
                    "campus": campus,
                    "nivel": tipo,
                    "document_title": title,
                    "source": page_url,
                    "timestamp": datetime.now().isoformat()
                }]

                docs = splitter.create_documents([content], metadatas=metadados)
                all_chunks.extend(docs)

    if not all_chunks:
        print("⚠️ Nenhum conteúdo válido encontrado para ingestão.")
        return {"message": "Nenhum conteúdo válido encontrado para ingestão."}

    print(f"💾 Armazenando {len(all_chunks)} documentos na coleção `ufsm_knowledge`...")
    container.set_collection("ufsm_knowledge")
    container.vectorstore.add_documents(all_chunks)

    os.makedirs("logs/ufsm", exist_ok=True)
    with open("logs/ufsm/cursos_links_acessados.json", "w", encoding="utf-8") as f:
        json.dump(curso_logs, f, indent=2, ensure_ascii=False)

    print("✅ Log salvo em logs/ufsm/cursos_links_acessados.json")
    logger.info("✅ Log JSON salvo com URLs acessadas dos cursos.")

    return {"message": f"Ingestão RAG finalizada com {len(all_chunks)} chunks"}

#---------------- olds
def get_all_sitemap_urls():
    r = requests.get("https://www.ufsm.br/robots.txt")
    if r.status_code != 200:
        return []
    return [line.split(": ", 1)[1] for line in r.text.splitlines() if line.lower().startswith("sitemap:")]

def extract_urls_from_sitemap(url):
    r = requests.get(url)
    if r.status_code != 200:
        return []
    root = ET.fromstring(r.content)
    return [u.text for u in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
#---------------- olds

def filter_course_urls(urls, filtro=None):
    return [url for url in urls if "/cursos/graduacao/" in url and (not filtro or filtro.lower() in url.lower())]

def extract_sentences_from_url(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        return [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
    except:
        return []

def ingest_from_sitemap(request):
    data = request.get_json() or {}
    filtro = data.get("filtro_nome")
    urls = []
    for sitemap in get_all_sitemap_urls():
        urls += extract_urls_from_sitemap(sitemap)
    cursos = filter_course_urls(urls, filtro)

    if not cursos:
        return jsonify({"error": "Nenhum curso encontrado"}), 404

    sentences = []
    metadata = []
    for url in cursos:
        for s in extract_sentences_from_url(url):
            sentences.append(s)
            metadata.append({"source": url})

    embeddings = embedding_model.embed_documents(sentences)
    container.store(collection_name="ufsm_cursos", sentences=sentences, embeddings=embeddings, metadata=metadata)

    return jsonify({"message": f"{len(sentences)} sentenças ingeridas na coleção ufsm_cursos"}), 200

def ingest_all_courses_text():
    all_urls = []
    for sitemap in get_all_sitemap_urls():
        all_urls += extract_urls_from_sitemap(sitemap)
    cursos = sorted(set(url.split("/cursos/graduacao/")[-1].split("/")[-2].replace("-", " ").title()
                        for url in filter_course_urls(all_urls)))

    frases = [f"A UFSM oferece o curso de {curso}." for curso in cursos]
    embeddings = embedding_model.embed_documents(frases)
    metadata = [{"source": "ufsm_geral"} for _ in frases]
    container.store(collection_name="ufsm_geral_knowledge", sentences=frases, embeddings=embeddings, metadata=metadata)
    return jsonify({"message": f"{len(frases)} frases ingeridas em ufsm_geral_knowledge"}), 200

def ingest_via_crawling():
    base = "https://www.ufsm.br"
    visited = set()
    queue = deque([base])
    textos = []

    while queue and len(visited) < 50:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            texto = "\n".join(p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40)
            if texto:
                textos.append({"url": url, "text": texto})
            for a in soup.find_all("a", href=True):
                next_url = urljoin(url, a["href"])
                if next_url.startswith(base) and next_url not in visited:
                    queue.append(next_url)
        except:
            continue

    sentences = []
    metadata = []
    for item in textos:
        for sent in item["text"].split(". "):
            if len(sent.strip()) >= 40:
                sentences.append(sent.strip())
                metadata.append({"source": item["url"]})

    embeddings = embedding_model.embed_documents(sentences)
    container.store("ufsm_knowledge", sentences, embeddings, metadata)
    return jsonify({"message": f"{len(sentences)} sentenças ingeridas via crawling"}), 200

def ingest_from_web_loader(request):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import WebBaseLoader
    from langchain_community.vectorstores import Qdrant

    data = request.get_json()
    url = data.get("url")
    collection = data.get("collection", "ufsm_geral_knowledge")
    if not url:
        return jsonify({"error": "URL obrigatória"}), 400

    loader = WebBaseLoader(url)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    vectordb = Qdrant(
        client=client,
        collection_name=collection,
        embeddings=embedding_model
    )
    vectordb.add_documents(chunks)

    return jsonify({"message": f"{len(chunks)} chunks adicionados à coleção `{collection}`."}), 200

def get_all_courses():
    urls = []
    for sitemap in get_all_sitemap_urls():
        urls += extract_urls_from_sitemap(sitemap)

    cursos = sorted(set(url.split("/cursos/graduacao/")[-1].split("/")[-2].replace("-", " ").title()
                        for url in filter_course_urls(urls)))
    return jsonify({"quantidade": len(cursos), "cursos": cursos}), 200
