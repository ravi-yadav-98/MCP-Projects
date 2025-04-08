from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

# Global configuration
MODEL = ChatOllama(model="llama3.2")

# Server configurations
MATH_SERVER = StdioServerParameters(
    command="python",
    args=["math_server.py"],
)

MULTI_SERVER_CONFIG = {
    "math": {
        "command": "python",
        "args": ["mcp_servers/math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "command": "python",
        "args": ["mcp_servers/weather_server.py"],
        "transport": "stdio",
    },
    "string_tools":{
        "command":"python",
        "args":["mcp_servers/string_tools_server.py"],
        "transport": "stdio",
    },
    "datetime": {
            "command": "python",
            "args": ["mcp_servers/datetime_tools_server.py"],  # Update path
            "transport": "stdio",
    },
    "wikipedia": {
            "command": "python",
            "args": ["mcp_servers/wikipedia_server.py"],  # Update path
            "transport": "stdio",
    },
    "yfinance": {
            "command": "python",
            "args": ["mcp_servers/yfinance_server.py"],  # Update path
            "transport": "stdio",
    }
}


def get_tool_calls(response: dict) -> str:
    """Extract tool call information from response"""
    tools_used = []
    for msg in response['messages']:
        if isinstance(msg, ToolMessage):
            tools_used.append({'name':msg.name, 'result':msg.content})
    return "\n".join([str(tool) for tool in tools_used]) if tools_used else ""



async def run_agent(
    question: str,
    multiple_mcp_server: bool = True
) -> str:
    """
    Query the agent with a question using either single or multiple MCP servers.
    
    Args:
        question: The input question for the agent
        multiple_mcp_server: Flag to use multiple servers (False for single server)
        
    Returns:
        The agent's text response
    """
    if multiple_mcp_server:
        # Multiple server mode
        async with MultiServerMCPClient(MULTI_SERVER_CONFIG) as client:
            agent = create_react_agent(MODEL, tools=client.get_tools())
            response = await agent.ainvoke({"messages": question})
            # return response['messages'][-1].content
            return response
    else:
        # Single server mode
        async with stdio_client(MATH_SERVER) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                agent = create_react_agent(MODEL, tools)
                response = await agent.ainvoke({"messages": question})
                # return response['messages'][-1].content
                return response


if __name__ == "__main__":
    
    questions = [
        "what's (3 + 5) x 12?"
        "what's the temperature in NYC ?",  
        "what's the weather in Mumbai?",
        "Reverse the string 'hello world'",
        "How many words are in the sentence 'Model Context Protocol is powerful'?",
        "What is the current date and time?"
        "What is age of virat kohli? ",
        "what is stock price of Apple?"
        "What are recent stock news for Apple?"
    ]
    response = asyncio.run(run_agent(question=questions[-1]))
    # print(get_tool_calls(response))
    
    for msg in response['messages']:
        msg.pretty_print()

# 
# https://modelcontextprotocol.io/quickstart/client