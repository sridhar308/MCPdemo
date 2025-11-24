from mcp.server.fastmcp import FastMCP

mcp=FastMCP("weather")

@mcp.tool()
async def get_current_weather(location: str) -> str:
    """Get the current weather for a given location.

    This tool is implemented as a synchronous function so agents that
    attempt synchronous invocation (i.e., call `.run(...)`) will succeed.
    If you prefer an async implementation, change this to `async def`
    and ensure clients await tool invocations.
    """
    # Placeholder implementation (sync)
    return f"The current weather in {location} is sunny with a temperature of 35°C."

if __name__=="__main__":
    # Use the hyphen transport name for MCP server (mcp.run expects 'streamable-http')
    mcp.run(transport="streamable-http")