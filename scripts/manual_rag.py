from elasticsearch import Elasticsearch
import os
import io
import json
import requests
from tqdm.auto import tqdm
import numpy as np
import pandas as pd
import docx
from datetime import datetime


def clean_line(line):
    line = line.strip()
    line = line.strip("\uFEFF")
    return line


def read_faq(file_id):
    url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"

    response = requests.get(url)
    response.raise_for_status()

    with io.BytesIO(response.content) as f_in:
        doc = docx.Document(f_in)

    questions = []

    question_heading_style = "heading 2"
    section_heading_style = "heading 1"

    heading_id = ""
    section_title = ""
    question_title = ""
    answer_text_so_far = ""

    for p in doc.paragraphs:
        style = p.style.name.lower()
        p_text = clean_line(p.text)

        if len(p_text) == 0:
            continue

        if style == section_heading_style:
            section_title = p_text
            continue

        if style == question_heading_style:
            answer_text_so_far = answer_text_so_far.strip()
            if (
                answer_text_so_far != ""
                and section_title != ""
                and question_title != ""
            ):
                questions.append(
                    {
                        "text": answer_text_so_far,
                        "section": section_title,
                        "question": question_title,
                    }
                )
                answer_text_so_far = ""

            question_title = p_text
            continue

        answer_text_so_far += "\n" + p_text

    answer_text_so_far = answer_text_so_far.strip()
    if answer_text_so_far != "" and section_title != "" and question_title != "":
        questions.append(
            {
                "text": answer_text_so_far,
                "section": section_title,
                "question": question_title,
            }
        )

    return questions


def load_documents(faq_documents):
    documents = []

    for course, file_id in faq_documents.items():
        print(course)
        course_documents = read_faq(file_id)
        documents.append({"course": course, "documents": course_documents})

    return documents


def generate_document_id(doc):
    import hashlib

    combined = f"{doc['course']}-{doc['question']}-{doc['text'][:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id


def chunk_documents(data):
    documents = []

    for doc in data["documents"]:
        doc["course"] = data["course"]
        # previously we used just "id" for document ID
        doc["document_id"] = generate_document_id(doc)
        documents.append(doc)

    print(len(documents))

    return documents


def main():
    documents = load_documents(faq_documents=faq_documents_end)

    # Chunk documents
    chunked_documents = chunk_documents(data=documents[0])

    # Open connection to elasticsearch
    es_client = Elasticsearch("http://localhost:9200")
    es_client.info()

    index_name_prefix = "documents"
    current_time = datetime.now().strftime("%Y%m%d_%M%S")
    index_name = f"{index_name_prefix}_{current_time}"
    print("index name:", index_name)

    number_of_shards = 1
    number_of_replicas = 0
    vector_column_name = "embedding"
    dimensions = []

    index_settings = {
        "settings": {"number_of_shards": number_of_shards, "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "text": {"type": "text"},
                "section": {"type": "text"},
                "question": {"type": "text"},
                "course": {"type": "keyword"},
                "document_id": {"type": "keyword"},
            }
        },
    }

    if not es_client.indices.exists(index=index_name):
        es_client.indices.create(index=index_name)
        print("Index created with properties:", index_settings)
        print("Embedding dimensions:", dimensions)

    print(
        f"Indexing {len(chunked_documents)} documents to Elasticsearch index {index_name}"
    )
    for document in chunked_documents:
        print(f'Indexing document {document["document_id"]}')

        es_client.index(index=index_name, document=document)
        print(document)

    # Retrieval
    query = "When is the next cohort?"

    # Search for the question of Q1 using elasticsearch
    def elastic_search(query_text: str, index_name: str):
        search_query = {
            "size": 2,
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["question", "text"],
                            "type": "best_fields",
                        }
                    },
                }
            },
        }

        es_results = es_client.search(index=index_name, body=search_query)

        result_docs = []

        for hit in es_results["hits"]["hits"]:
            result_docs.append(hit["_source"])

        return result_docs

    search_results = elastic_search(query_text=query, index_name=index_name)
    return search_results


if __name__ == "__main__":
    faq_documents_ini = {
        "llm-zoomcamp": "1m2KexowAXTmexfC5rVTCSnaShvdUQ8Ag2IEiwBDHxN0",
    }

    faq_documents_end = {
        "llm-zoomcamp": "1T3MdwUvqCL3jrh3d3VCXQ8xE0UqRzI3bfgpfBq3ZWG0",
    }

    search_results_ini = main(faq_documents=faq_documents_ini)
    search_results_end = main(faq_documents=faq_documents_end)
