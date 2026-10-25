import re
import json
import requests
from langchain_core.tools import tool
from api import get_searchapi_key, convert_currency

@tool
def search_flight(origin: str, destination: str, outbound_date: str, return_date: str, currency: str = "USD") -> str:
    """Search for round-trip flights between two cities for specific dates (YYYY-MM-DD)."""
    api_key = get_searchapi_key()
    if not api_key:
        return json.dumps({"error": "SearchApi key is not initialized. Please check credentials."})
    
    try:
        # SearchApi Google Flights endpoint
        params = {
            "engine": "google_flights",
            "api_key": api_key,
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "currency": currency
        }
        
        response = requests.get("https://www.searchapi.io/api/v1/search", params=params)
        
        if response.status_code != 200:
            return json.dumps({"error": f"SearchApi Error: {response.text}"})
            
        data = response.json()
        flights = data.get("best_flights", []) or data.get("other_flights", [])
        
        if not flights:
            return json.dumps({"message": "No flights found for the given criteria."})
            
        flight_results = []
        for flight in flights[:5]:
            try:
                # Get total price
                flight_price = flight.get("price", 0)
                
                # Get airlines
                flights_list = flight.get("flights", [])
                airline = flights_list[0].get("airline", "Unknown") if flights_list else "Unknown"
                departure_time = flights_list[0].get("departure_airport", {}).get("time", "Unknown") if flights_list else "Unknown"
                arrival_time = flights_list[-1].get("arrival_airport", {}).get("time", "Unknown") if flights_list else "Unknown"
                
                flight_info = {
                    "airline": airline,
                    "route": f"{origin} -> {destination}",
                    # We search for 1 adult (SearchApi's default), so this is the round-trip fare for ONE traveler
                    # (both directions are already included)
                    "round_trip_price_per_person": flight_price,
                    "currency": currency,
                    "departure": departure_time,
                    "arrival": arrival_time,
                    "outbound_date": outbound_date,
                    "return_date": return_date,
                    "link": f"https://www.google.com/travel/flights?q=Flights%20to%20{destination}%20from%20{origin}%20on%20{outbound_date}%20through%20{return_date}"
                }
                
                flight_results.append(flight_info)
            except Exception:
                continue
                
        return json.dumps(flight_results)
    
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@tool
def search_hotel(location: str, checkin_date: str, checkout_date: str, currency: str = "USD") -> str:
    """Search for hotels in a city for specific dates (YYYY-MM-DD)."""
    api_key = get_searchapi_key()
    if not api_key:
        return json.dumps({"error": "SearchApi key is not initialized. Please check credentials."})
    
    try:
        params = {
            "engine": "google_hotels",
            "api_key": api_key,
            "q": location,
            "check_in_date": checkin_date,
            "check_out_date": checkout_date,
            "currency": currency
        }
        
        response = requests.get("https://www.searchapi.io/api/v1/search", params=params)
        
        if response.status_code != 200:
            return json.dumps({"error": f"SearchApi Error: {response.text}"})
            
        data = response.json()
        properties = data.get("properties", [])
        
        if not properties:
            return json.dumps({"message": "No hotels found for the given criteria."})
            
        hotel_results = []
        for hotel in properties[:5]:
            try:
                # SearchApi's fields: price_per_night / total_price, each with a numeric "extracted_price"
                price_per_night = hotel.get("price_per_night", {}).get("extracted_price", "See website")
                total_price = hotel.get("total_price", {}).get("extracted_price", "See website")

                hotel_info = {
                    "name": hotel.get("name", "Unknown Hotel"),
                    "price_per_night": price_per_night,
                    "total_price_for_stay": total_price,  # already covers every night, no multiplying needed
                    "currency": currency,
                    "rating": hotel.get("overall_rating", "N/A"),
                    "reviews": hotel.get("reviews", "N/A"),
                    "link": hotel.get("link", "#")
                }
                hotel_results.append(hotel_info)
            except Exception:
                continue
                
        return json.dumps(hotel_results)
    
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@tool
def search_restaurants(location: str, query: str = "best restaurants") -> str:
    """Search for highly-rated restaurants in a specific location."""
    api_key = get_searchapi_key()
    if not api_key:
        return json.dumps({"error": "SearchApi key is not initialized."})
    
    try:
        params = {
            "engine": "google_local",
            "api_key": api_key,
            "q": f"{query} in {location}"
        }
        
        response = requests.get("https://www.searchapi.io/api/v1/search", params=params)
        
        if response.status_code != 200:
            return json.dumps({"error": f"SearchApi Error: {response.text}"})
            
        data = response.json()
        local_results = data.get("local_results", [])
        
        if not local_results:
            return json.dumps({"message": "No restaurants found."})
            
        restaurants = []
        for res in local_results[:5]:
            restaurants.append({
                "name": res.get("title", "Unknown"),
                "rating": res.get("rating", "N/A"),
                "reviews": res.get("reviews", "N/A"),
                "price": res.get("price", "N/A"),
                "address": res.get("address", "N/A"),
                "description": res.get("description", "")
            })
                
        return json.dumps(restaurants)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

@tool
def calculate_trip_cost(items: list[dict], budget: float, travelers: int = 1, currency: str = "INR") -> str:
    """
    Adds up the trip cost so the totals are exact (LLMs are bad at arithmetic).
    items: list of {"category": "travel|stay|food|activities|other", "description": str, "amount": number, "quantity": int}
    amount is the price of ONE unit and quantity how many units (e.g. a per-person flight fare with quantity = travelers).
    quantity defaults to 1, so a line that is already a group total needs no quantity. budget: total budget for the whole group.
    """
    totals = {}
    unpriced = []
    for item in items:
        quantity = item.get("quantity") or 1
        category = item.get("category", "other")
        # Accept 4500, "₹4,500" or a range like "₹200-1,400" (we budget for the higher end)
        numbers = re.findall(r"\d[\d,]*(?:\.\d+)?", str(item.get("amount", "")))
        if not numbers:
            # e.g. "See website": leave it out of the total instead of crashing, and report it
            unpriced.append(item.get("description", category))
            continue
        amount = max(float(n.replace(",", "")) for n in numbers) * float(quantity)
        totals[category] = totals.get(category, 0) + amount

    grand_total = sum(totals.values())
    travelers = max(int(travelers), 1)
    return json.dumps({
        "by_category": totals,
        "unpriced_items": unpriced,
        "total": round(grand_total, 2),
        "per_person": round(grand_total / travelers, 2),
        "budget": budget,
        "remaining": round(budget - grand_total, 2),
        "over_budget": grand_total > budget,
        "currency": currency,
    })

@tool
def search_activities(location: str, query: str = "top things to do") -> str:
    """Search for popular tours, excursions, and activities in a location."""
    api_key = get_searchapi_key()
    if not api_key:
        return json.dumps({"error": "SearchApi key is not initialized."})
    
    try:
        params = {
            "engine": "google_local",
            "api_key": api_key,
            "q": f"{query} in {location}"
        }
        
        response = requests.get("https://www.searchapi.io/api/v1/search", params=params)
        
        if response.status_code != 200:
            return json.dumps({"error": f"SearchApi Error: {response.text}"})
            
        data = response.json()
        local_results = data.get("local_results", [])
        
        if not local_results:
            return json.dumps({"message": "No activities found."})
            
        activities = []
        for res in local_results[:5]:
            activities.append({
                "name": res.get("title", "Unknown"),
                "rating": res.get("rating", "N/A"),
                "reviews": res.get("reviews", "N/A"),
                "address": res.get("address", "N/A"),
                "description": res.get("description", "")
            })
                
        return json.dumps(activities)
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})
