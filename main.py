import json
from os import environ
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from google.cloud import storage
from google.cloud import aiplatform_v1
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware


# Create an MCP server
mcp = FastMCP("Demo")

# Set variables for the current deployed index.
# TODO: Make these configurable from environment variables
API_ENDPOINT="1568100902.europe-north1-54087748514.vdb.vertexai.goog"
INDEX_ENDPOINT="projects/54087748514/locations/europe-north1/indexEndpoints/4890522167231381504"
DEPLOYED_INDEX_ID="mcp_demo_index_deployment_1745438280521"

@mcp.resource("vector://search/{query}")
def vector_search(query: str) -> str:
    """Search for a query in the vector database"""

    client_options = {
        "api_endpoint": API_ENDPOINT
    }
    vector_search_client = aiplatform_v1.MatchServiceClient(
        client_options=client_options,
    )

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(query)

    datapoint = aiplatform_v1.IndexDatapoint(
        feature_vector=embeddings
    )

    query = aiplatform_v1.FindNeighborsRequest.Query(
        datapoint=datapoint,
        neighbor_count=10
    )

    request = aiplatform_v1.FindNeighborsRequest(
        index_endpoint=INDEX_ENDPOINT,
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[query],
        return_full_datapoint=False,
    )

    response = vector_search_client.find_neighbors(request)

    results = []
    # TODO: map chunk_id to text metadata
    for neighbor in response.nearest_neighbors[0].neighbors:
        results.append({
            "chunk_id": neighbor.datapoint.datapoint_id,
            "distance": neighbor.distance,
        })

    return json.dumps(results)

@mcp.resource("file://list")
def file_list() -> list[str]:
    """List all files in the bucket"""
    storage_client = storage.Client()

    bucket_name = environ.get("BUCKET_NAME", "mcp-demo")
    blobs = storage_client.list_blobs(bucket_name, prefix="texts/")

    files = [blob.name.replace("texts/", "") for blob in blobs if not blob.name.endswith("/")]
    return sorted(files)

@mcp.resource("file://text/{filename}")
def file(filename: str) -> str:
    """Read a file"""
    storage_client = storage.Client()

    bucket_name = environ.get("BUCKET_NAME", "mcp-demo")
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"texts/{filename}")

    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return blob.download_as_string().decode("utf-8")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.mount("/mcp", mcp.sse_app())

@app.get("/")
def root():
    return {"message": "Welcome to the MCP Demo API"}
