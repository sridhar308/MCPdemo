from mcp.server.fastmcp import FastMCP

mcp=FastMCP("math")

@mcp.tool()
def add(a:int,b:int)->int:
    """_sumary_ Add to numbers"""
    return a+b

@mcp.tool()
def multiply(a:int,b:int)->int:
    """_summary_ Multiply two numbers"""
    return a*b

#The transport="stdio" argument tells the server to:
#Use standarad input/output (Stdin and stdout) to receive and respond to tool funcation calls

if __name__=="__main__":
    # Run the math MCP server over stdio so it can be launched by the client
    mcp.run(transport="stdio")