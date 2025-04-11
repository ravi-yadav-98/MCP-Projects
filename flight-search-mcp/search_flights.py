"""
Flight search service implementation using SerpAPI Google Flights.
"""
from typing import List, Dict, Optional, Any
from log import logger
from serp_api import run_search, prepare_flight_search_params


async def search_flights(
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str] = None
) -> List[Dict[str, str]]:
    """Search for flights using SerpAPI Google Flights.
    
    Args:
        origin: Departure airport code (e.g., ATL, JFK)
        destination: Arrival airport code (e.g., LAX, ORD)
        outbound_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trips (YYYY-MM-DD)
        
    Returns:
        List of available flights with details or error dict if search fails
    """
    logger.info(
        f"Searching flights: {origin} to {destination}, "
        f"dates: {outbound_date} - {return_date}"
    )
    logger.debug(
        f"Function called with: origin={origin}, destination={destination}, "
        f"outbound_date={outbound_date}, return_date={return_date}"
    )
    
    params = prepare_flight_search_params(origin, destination, outbound_date, return_date)
    logger.debug("Executing SerpAPI search...")
    search_results = await run_search(params)
    
    if "error" in search_results:
        logger.error(f"Flight search error: {search_results['error']}")
        return {"error": search_results["error"]}
    
    return format_flight_results(search_results)


def format_flight_results(search_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """Format raw flight search results into standardized format.
    
    Args:
        search_results: Raw search results from SerpAPI
        
    Returns:
        Formatted list of flight information
    """
    best_flights = search_results.get("best_flights", [])
    logger.debug(f"Search complete. Found {len(best_flights)} best flights")
    
    if not best_flights:
        logger.warning("No flights found in search results")
        return []
    
    formatted_flights = []
    for idx, flight in enumerate(best_flights, start=1):
        logger.debug(f"Processing flight {idx} of {len(best_flights)}")
        
        if not flight.get("flights"):
            logger.debug(f"Skipping flight {idx} as it has no flight segments")
            continue
            
        first_leg = flight["flights"][0]
        logger.debug(
            f"Flight {idx} has airline: {first_leg.get('airline', 'Unknown')}, "
            f"price: {flight.get('price', 'N/A')}"
        )
        
        departure_info = _get_airport_info(first_leg, "departure")
        arrival_info = _get_airport_info(first_leg, "arrival")
        
        formatted_flights.append({
            "airline": first_leg.get("airline", "Unknown Airline"),
            "price": str(flight.get("price", "N/A")),
            "duration": f"{flight.get('total_duration', 'N/A')} min",
            "stops": _get_stops_description(len(flight["flights"])),
            "departure": departure_info,
            "arrival": arrival_info,
            "travel_class": first_leg.get("travel_class", "Economy"),
            "airline_logo": first_leg.get("airline_logo", "")
        })
    
    logger.info(f"Returning {len(formatted_flights)} formatted flights")
    return formatted_flights


def _get_airport_info(flight_leg: Dict[str, Any], direction: str) -> str:
    """Helper to get formatted airport information."""
    airport = flight_leg.get(f"{direction}_airport", {})
    time_key = f"{direction}_time"
    
    if isinstance(airport, dict):
        name = airport.get("name", "Unknown")
        code = airport.get("id", "???")
        time = airport.get("time", "N/A")
        return f"{name} ({code}) at {time}"
    return flight_leg.get(time_key, "Unknown")


def _get_stops_description(num_flights: int) -> str:
    """Helper to get stops description."""
    return "Nonstop" if num_flights == 1 else f"{num_flights - 1} stop(s)"


# import asyncio
# 
# if __name__ == "__main__":
#     res = asyncio.run(search_flights('Atlanta', 'new york', '13-04-2025'))
#     print(res)