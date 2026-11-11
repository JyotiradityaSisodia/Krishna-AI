import urllib.parse
import webbrowser


def place_food_order(item_or_cuisine: str, restaurant: str = "") -> dict:
    if not item_or_cuisine.strip():
        return {
            "status": "failed",
            "message": "No food item or cuisine was provided."
        }

    query = item_or_cuisine.strip()
    if restaurant.strip():
        query = f"{item_or_cuisine.strip()} from {restaurant.strip()}"

    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.swiggy.com/search?query={encoded_query}"

    try:
        webbrowser.open(search_url)
        return {
            "status": "success",
            "message": f"I opened Swiggy search for {query}. The website may still ask for verification or login."
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Failed to open Swiggy search: {str(e)}"
        }


def finalize_food_order() -> str:
    return "Swiggy is currently blocking full browser automation, so I opened the search page instead."