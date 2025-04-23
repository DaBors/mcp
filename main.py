from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import uvicorn

# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

app = FastAPI()
app.mount("/mcp", mcp.sse_app())

@app.get("/")
def root():
    return {"message": "Welcome to the MCP Demo API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
