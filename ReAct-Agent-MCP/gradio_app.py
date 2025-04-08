import gradio as gr
from mcp_client import run_agent
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

examples = [
    "what's (3 + 5) x 12?",
    "what is the weather in california?",
    "What is current time and date?",
    "Reverse the string 'Hello World'",
    "Who is virat kohli?",
    "What is stock price of Apple?"
    
    ]


def get_tool_calls(response: dict) -> str:
    """Extract tool call information from response"""
    tools_used = []
    for msg in response['messages']:
        if isinstance(msg, ToolMessage):
            tools_used.append({'tool_called':msg.name, 'result':msg.content})
    return "\n".join([str(tool) for tool in tools_used]) if tools_used else ""

async def respond(message: str):
    """Handle chat interaction with the agent"""
    try:
         
        response = await run_agent(message)
        ai_response = response['messages'][-1].content
        tool_details =  get_tool_calls(response)
        
        # # Format the sources
        sources_html = "<details><summary><b>See Details</b></summary><ul>"
        sources_html += f"\n\n{tool_details}"
        sources_html += "</ul></details>"
        
        # Append the sources to the AI response
        ai_response += f"\n\n{sources_html}"
    
        return ai_response
    except Exception as e:
        return f"Error: {str(e)}"

async def chat(query, history):
    
    
    history.append({'role': 'user', 'content': query})
    
    # Generate response
    response = await run_agent(query)
    ai_response = response['messages'][-1].content
    tool_details =  get_tool_calls(response)
    sources_html = "<details><summary><b>See Details</b></summary><ul>"
    sources_html += f"\n\n{tool_details}"
    
    ai_response += f"\n\n{sources_html}"
    
    # Update the chat history
    history.append({'role': 'assistant', 'content': ai_response})
    return "", history 


# Create the Gradio interface
with gr.Blocks(title="ReAct Agent") as demo:
    gr.Markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h1 style='font-weight: bold;'>🤖 ReAct AI Agent powered by MCP</h1>
    </div>
    """)
    chatbot = gr.Chatbot(label="Chatbot", height=500, layout="bubble")
    with gr.Row():
        msg = gr.Textbox(label="Your Question", 
                       placeholder="Type your question here...",
                       scale=20,
                       autofocus=True,
                       container=False)
        submit_btn = gr.Button("Ask", variant="primary", min_width=100)

    clear = gr.ClearButton([msg, chatbot])

    def add_message(history, message):
        history.append((message, None))
        return history, ""

    async def generate_response(history):
        if not history or history[-1][1] is not None:
            return history
            
        message = history[-1][0]
        response = await respond(message)
        history[-1] = (message, response)
        return history

    # Handle both textbox submit and button click
    msg.submit(
        add_message, [chatbot, msg], [chatbot, msg], queue=False
    ).then(
        generate_response, chatbot, chatbot
    )
    
    submit_btn.click(
        add_message, [chatbot, msg], [chatbot, msg], queue=False
    ).then(
        generate_response, chatbot, chatbot
    )
    
    # Add accordion with server information
    with gr.Accordion("📡 Available MCP Servers", open=False):
        gr.Markdown("""
        ### Currently Connected Services:
        
        - **Math Server**: Basic arithmetic and calculations
        - **Weather Server**: Current weather information
        - **String Tools**: Text manipulation utilities
        - **Datetime Server**: Date and time queries
        - **Wikipedia Server**: General knowledge searches
        - **yFinence Server**: Stock Price Related Quries
        
        *All servers run locally via MCP protocol*
        """)

    gr.Examples(
        examples=examples,
        inputs=msg
    )

if __name__ == "__main__":
    demo.launch()