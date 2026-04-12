from langchain_core.tools import tool


@tool
def mock_search_flights(origin: str, destination: str, date: str) -> str:
    """Search for available flights between two cities on a given date.
    Args:
        origin: Departure city (e.g. 'Delhi')
        destination: Arrival city (e.g. 'Tokyo')
        date: Travel date (e.g. '2026-06-15')
    """
    # Stub — replace with real flight API (Amadeus, Skyscanner)
    return f"""
    Flights from {origin} to {destination} on {date}:
    1. Air India AI-307 | Departs 08:30 | Arrives 22:45 | ₹45,000 | Direct
    2. JAL JL-752 | Departs 14:20 | Arrives 05:30+1 | ₹52,000 | Direct  
    3. IndiGo 6E-4521 | Departs 06:00 | Arrives 18:30 | ₹38,000 | 1 stop (Bangkok)
    """


@tool
def mock_book_flight(flight_id: str, passenger_name: str) -> str:
    """Book a specific flight for a passenger. REQUIRES human approval first.
    Args:
        flight_id: Flight identifier from search results
        passenger_name: Full name of passenger
    """
    return f"✅ BOOKING CONFIRMED: Flight {flight_id} for {passenger_name}. Confirmation: TRP{hash(flight_id) % 99999:05d}"
