# pip install llama-index llama-index-llms-ollama llama-index-tools-mcp langchain-community
import asyncio
import sys
import os
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.ollama import Ollama
from prompt_template import FLIGHT_SEARCH_PROMPT

# Configuration variables
MCP_URL = os.environ.get("MCP_URL", "http://127.0.0.1:3001/sse")
MODEL_NAME = os.environ.get("LLM_MODEL", "llama3.2")
TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.7"))


def display_welcome_message():
    """Display the welcome message and instructions."""
    print("\n✈️ Natural Language Flight Search Assistant ✈️")
    print("-" * 50)
    print("Ask me anything about flights using natural language!")
    print("Examples:")
    print("  • Find flights from Atlanta to New York tomorrow")
    print("  • I need a flight to Paris next week")
    print("\nType 'exit' or 'quit' to end the session.")
    print("-" * 50)


async def setup_agent():
    """Setup and return the flight assistant agent."""
    mcp_client = BasicMCPClient(MCP_URL)
    tools = await McpToolSpec(client=mcp_client).to_tool_list_async()
    llm = Ollama(model=MODEL_NAME, temperature=TEMPERATURE)
    
    system_prompt = FLIGHT_SEARCH_PROMPT.template.replace("{tools}", "")\
                                               .replace("{tool_names}", "")\
                                               .replace("{input}", "")
    return ReActAgent(
        name="FlightAgent",
        llm=llm,
        tools=tools,
        system_prompt=system_prompt,
        temperature=TEMPERATURE
    )


async def handle_user_query(agent, query):
    """Process a single user query and return the response."""
    if not query.strip():
        return None
    try:
        return await agent.run(query)
    except Exception as e:
        print(f"Error processing query: {e}")
        return None


async def main():
    """Main function to run the flight search application."""
    display_welcome_message()
    
    try:
        agent = await setup_agent()
        print("Ready to search flights!")
        
        while True:
            user_query = input("\n🔍 Your flight query: ").strip()
            
            if user_query.lower() in {'exit', 'quit', 'q'}:
                print("\nThank you for using the Flight Search Assistant. Goodbye!")
                break
                
            response = await handle_user_query(agent, user_query)
            if response:
                print(f"\n{response}")
                
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Make sure the flight server is running at {MCP_URL}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))