from pypdf import PdfReader
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(pdf_path):
    """
    Extract text from uploaded PDF file.
    """
    text = ""

    reader = PdfReader(pdf_path)

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def split_text_into_chunks(text, chunk_size=1000, overlap=150):
    """
    Split large text into smaller chunks.
    """
    chunks = []

    text = re.sub(r'\s+', ' ', text).strip()

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks


def search_relevant_chunks(question, chunks, top_k=10):
    """
    Lightweight RAG search using TF-IDF + cosine similarity.
    Returns more chunks so multi-topic questions work better.
    """

    chunk_list = list(chunks)

    if not chunk_list:
        return []

    chunk_texts = [chunk.chunk_text for chunk in chunk_list]

    documents = [question] + chunk_texts

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 3)
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    question_vector = tfidf_matrix[0:1]
    chunk_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(question_vector, chunk_vectors)[0]

    ranked_indexes = similarities.argsort()[::-1]

    relevant_chunks = []

    for index in ranked_indexes[:top_k]:
        if similarities[index] > 0.01:
            relevant_chunks.append(chunk_texts[index])

    return relevant_chunks