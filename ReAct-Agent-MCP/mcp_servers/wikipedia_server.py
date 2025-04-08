from mcp.server.fastmcp import FastMCP
import httpx


# Initialize server
mcp = FastMCP("WikipediaSearch")

USER_AGENT = "wikipedia-search/1.0 (+https://github.com/your/repo)"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
TIMEOUT = 10.0  # seconds

async def fetch_wikipedia_content(search_term: str) -> str:
    """Fetches content from Wikipedia API asynchronously with proper error handling."""
    params = {
        'action': 'query',
        'format': 'json',
        'titles': search_term,
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
    }
    
    headers = {'User-Agent': USER_AGENT}
    
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                WIKIPEDIA_API_URL,
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return f"No Wikipedia page found for '{search_term}'"
            
            page = next(iter(pages.values()))
            if 'missing' in page:
                return f"No Wikipedia page found for '{search_term}'"
            
            if 'extract' in page:
                return page['extract'] or f"Page exists but has no extractable content for '{search_term}'"
            
            return f"Unexpected API response format for '{search_term}'"
            
    except httpx.HTTPStatusError as e:
        return f"Wikipedia API error: {str(e)}"
    except httpx.RequestError as e:
        return f"Failed to connect to Wikipedia: {str(e)}"
    except (KeyError, StopIteration) as e:
        return f"Error processing Wikipedia response: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
async def search_wikipedia(search_term: str) -> str:
    """
    Searches Wikipedia for a given term and returns a summary from the page.
    
    Args:
        search_term: The topic to search for on Wikipedia
        
    Returns:
        A summary extracted from the Wikipedia page or an error message
    """
    if not search_term.strip():
        return "Please provide a search term"
    
    return await fetch_wikipedia_content(search_term)

if __name__ == "__main__":
    mcp.run(transport="stdio")