from os import makedirs
from sentence_transformers import SentenceTransformer
import requests
import json
import re

# Split into chunks (e.g. 500 words)
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def save_embeddings_for_gcp(chunks, embeddings, filename):
    with open("data/embeddings/" + filename + ".json", "w") as f:
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Format each record according to GCP Vector Search requirements
            record = {
                "id": f"chunk_{i}",
                "embedding": embedding.tolist(),
                "metadata": {
                    "text": chunk
                }
            }
            # Write each JSON object on a separate line (JSONL format)
            f.write(json.dumps(record) + "\n")

book_ids = [
    11,
    98,
    1342,
    41445,
]

makedirs("data/embeddings", exist_ok=True)
makedirs("data/texts", exist_ok=True)

for book_id in book_ids:
    # Download a book (e.g. Alice in Wonderland)
    book_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    response = requests.get(book_url)
    plain_text = response.text

    # Extract content between Gutenberg markers
    content = re.search(
        r'\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*?\n(.*?)\*\*\* END OF THE PROJECT GUTENBERG EBOOK',
        plain_text,
        re.DOTALL
    )
    text = content.group(1).strip() if content else ""

    chunks = chunk_text(text)

    # Generate embeddings
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)

    filename = f"pg{book_id}"
    save_embeddings_for_gcp(chunks, embeddings, filename)

    with open("data/texts/" + filename + ".txt", "w") as f:
        f.write(text)
