
from mcp.server.fastmcp import FastMCP
from log import logger
from search import search_flights
from config import DEFAULT_PORT, DEFAULT_CONNECTION_TYPE


mcp = FastMCP("FlightSearchService", port=DEFAULT_PORT)
    

@mcp.tool()
async def search_flights_tool(origin: str, destination: str, outbound_date: str, return_date: str = None):
    """
    Search for flights using SerpAPI Google Flights.
    
    This MCP tool allows AI models to search for flight information by specifying
    departure and arrival airports and travel dates.
    
    Args:
        origin: Departure airport code (e.g., ATL, JFK)
        destination: Arrival airport code (e.g., LAX, ORD)
        outbound_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trips (YYYY-MM-DD)
        
    Returns:
        A list of available flights with details
    """
    return await search_flights(origin, destination, outbound_date, return_date)

@mcp.tool()
def server_status():
    """
    Check if the Model Context Protocol server is running.
    
    This MCP tool provides a simple way to verify the server is operational.
    
    Returns:
        A status message indicating the server is online
    """
    return {"status": "online", "message": "MCP Flight Search server is running"}

logger.debug("Model Context Protocol tools registered")


if __name__ == "__main__":
    mcp.run('sse')