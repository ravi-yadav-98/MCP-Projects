from mcp.server.fastmcp import FastMCP
import yfinance as yf
import httpx
from typing import List, Dict, Any

# Initialize server
mcp = FastMCP("YFinanceService")

TIMEOUT = 10.0  # seconds
USER_AGENT = "yfinance-service/1.0 "

async def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch stock data using yfinance with proper error handling."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info:
            return {"error": f"No data found for ticker '{ticker}'"}
            
        return {
            "price": info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
            "currency": info.get('currency', 'N/A'),
            "name": info.get('longName', info.get('shortName', ticker)),
            "change": info.get('regularMarketChange', 'N/A'),
            "change_percent": info.get('regularMarketChangePercent', 'N/A')
        }
        
    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}

@mcp.tool()
async def get_stock_price(ticker: str) -> str:
    """
    Gets the current price and related information for a stock.
    
    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL' for Apple)
        
    Returns:
        A formatted string with stock price information or error message
    """
    if not ticker.strip():
        return "Please provide a stock ticker symbol"
    
    data = await fetch_stock_data(ticker)
    
    if "error" in data:
        return data["error"]
    
    return (
        f"{data['name']} ({ticker}): {data['price']} {data['currency']}\n"
        f"Change: {data['change']} ({data['change_percent']}%)"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")