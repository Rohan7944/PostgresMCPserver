from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeatherServer")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the weather location"""
    return f"The weather in Tokyo is sunny"

if __name__=="__main__":
    mcp.run(transport="streamable-http")