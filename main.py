from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from google.cloud import storage

# Create an MCP server
mcp = FastMCP("Demo")
bucket_name = "mcp-demo"

@mcp.resource("file://list")
def file_list() -> list[str]:
    """List all files in the bucket"""
    storage_client = storage.Client()

    blobs = storage_client.list_blobs(bucket_name, prefix="texts/")

    files = [blob.name.replace("texts/", "") for blob in blobs if not blob.name.endswith("/")]
    return sorted(files)

@mcp.resource("file://text/{filename}")
def file(filename: str) -> str:
    """Read a file"""
    storage_client = storage.Client()

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(f"texts/{filename}")

    if not blob.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return blob.download_as_string().decode("utf-8")

app = FastAPI()
app.mount("/mcp", mcp.sse_app())

@app.get("/")
def root():
    return {"message": "Welcome to the MCP Demo API"}
