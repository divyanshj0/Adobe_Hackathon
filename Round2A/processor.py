# processor.py
import os
import json
import datetime
import pdfplumber
from sentence_transformers import SentenceTransformer, util
import numpy as np

model = SentenceTransformer("./local_model")  # small model for fast CPU inference

def extract_text_from_pdfs(document_list, base_path="data"):
    doc_text = {}
    for doc in document_list:
        path = os.path.join(base_path, doc["filename"])
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
            doc_text[doc["filename"]] = pages
    return doc_text

def rank_sections(text_blocks, query, top_k=5):
    section_texts = [tb["text"] for tb in text_blocks]
    embeddings = model.encode(section_texts + [query], convert_to_tensor=True)
    scores = util.pytorch_cos_sim(embeddings[-1], embeddings[:-1]).squeeze().tolist()
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [text_blocks[i] | {"score": scores[i]} for i in top_indices]

def process_documents(input_payload):
    documents = input_payload["documents"]
    persona = input_payload["persona"]["role"]
    job = input_payload["job_to_be_done"]["task"]
    query = f"As a {persona}, {job}"

    # Extract text
    raw_text = extract_text_from_pdfs(documents)

    # Prepare blocks: doc, page_number, text
    all_blocks = []
    for doc, pages in raw_text.items():
        for i, text in enumerate(pages):
            if text:
                all_blocks.append({
                    "document": doc,
                    "page_number": i + 1,
                    "text": text.strip().replace("\n", " ")
                })

    # Rank relevance
    top_blocks = rank_sections(all_blocks, query)

    # Prepare JSON output
    timestamp = datetime.datetime.now().isoformat()
    extracted = []
    analysis = []

    for rank, block in enumerate(top_blocks, 1):
        title_guess = block["text"].split(". ")[0][:80]  # crude section title guess
        extracted.append({
            "document": block["document"],
            "section_title": title_guess,
            "importance_rank": rank,
            "page_number": block["page_number"]
        })
        analysis.append({
            "document": block["document"],
            "refined_text": block["text"][:1000],
            "page_number": block["page_number"]
        })

    return {
        "metadata": {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": timestamp
        },
        "extracted_sections": extracted,
        "subsection_analysis": analysis
    }
