from langchain_core.tools import tool


@tool
def mock_search_hotels(
    city: str, check_in: str, check_out: str, budget_inr: int
) -> str:
    """Search for hotels in a city within budget.
    Args:
        city: City name
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        budget_inr: Max budget per night in INR
    """
    return f"""
    Hotels in {city} ({check_in} to {check_out}, budget ₹{budget_inr}/night):
    1. Shinjuku Granbell Hotel | ₹8,500/night | 4★ | Near metro
    2. Dormy Inn Asakusa | ₹6,200/night | 3★ | Traditional area, onsen
    3. Citadines Shinjuku | ₹11,000/night | 4★ | Serviced apartment, kitchen
    """


@tool
def mock_book_hotel(
    hotel_name: str, guest_name: str, check_in: str, check_out: str
) -> str:
    """Book a hotel room. REQUIRES human approval first.
    Args:
        hotel_name: Name of hotel from search results
        guest_name: Guest full name
        check_in: Check-in date
        check_out: Check-out date
    """
    return f"✅ BOOKING CONFIRMED: {hotel_name} for {guest_name} ({check_in} → {check_out}). Ref: HTL{hash(hotel_name) % 99999:05d}"
