from mcp.server.fastmcp import FastMCP
import re
mcp = FastMCP("StringTools")

@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverses the given string."""
    return text[::-1]
@mcp.tool()
def count_words(text: str) -> int:
    """Counts the number of words in a sentence."""
    return len(text.split())

@mcp.tool()
def is_palindrome(text: str) -> bool:
    """
    Checks if a string is a palindrome (reads the same forwards and backwards).
    Ignores case, spaces and punctuation.
    """
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    return cleaned == cleaned[::-1]
if __name__ == "__main__":
    mcp.run(transport="stdio")