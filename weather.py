from mcp.server.fastmcp import FastMCP

mcp=FastMCP("weather")

@mcp.tool()
async def get_current_weather(location: str) -> str:
    """_summary_ Get the current weather for a given location"""
    # Placeholder implementation
    return f"The current weather in {location} is sunny with a temperature of 25°C."

if __name__=="__main__":
    # Use the hyphen transport name for MCP server (mcp.run expects 'streamable-http')
    mcp.run(transport="streamable-http")