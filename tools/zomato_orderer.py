from tools.android_controller import (
    is_device_connected,
    open_app,
    tap_element,
    type_text,
    keyevent,
    sleep,
    swipe,
)

ZOMATO_PACKAGE = "com.application.zomato"

# Fallback coordinates only for stubborn inside-restaurant actions
MENU_SEARCH_BAR_X = 752
MENU_SEARCH_BAR_Y = 114
RESTAURANT_ADD_X = 749
RESTAURANT_ADD_Y = 337
CART_BUTTON_X = 764
CART_BUTTON_Y = 650
PLACE_ORDER_X = 764
PLACE_ORDER_Y = 650


def _open_home_search() -> bool:
    # Exact Zomato home search field from your UI dump
    ok, _ = tap_element(resource_id_contains="search_edit_text")
    if ok:
        sleep(2)
        return True

    # Fallback to description
    ok, _ = tap_element(content_desc_contains="open search page")
    if ok:
        sleep(2)
        return True

    return False


def _open_restaurant_by_name(restaurant: str) -> bool:
    # Try exact/partial restaurant match from content-desc
    ok, _ = tap_element(content_desc_contains=restaurant)
    if ok:
        sleep(5)
        return True

    # Fallback with common shortened forms
    words = [w for w in restaurant.split() if len(w) > 2]
    for word in words:
        ok, _ = tap_element(content_desc_contains=word)
        if ok:
            sleep(5)
            return True

    return False


def _search_inside_restaurant(item_or_cuisine: str):
    # For now, restaurant-page search still uses your manual coordinates
    from tools.android_controller import tap
    tap(MENU_SEARCH_BAR_X, MENU_SEARCH_BAR_Y)
    sleep(2)

    type_text(item_or_cuisine)
    sleep(2)
    keyevent(66)
    sleep(5)


def _add_first_item():
    # Try UI text first
    ok, _ = tap_element(text_contains="ADD")
    if ok:
        sleep(3)
        return True

    ok, _ = tap_element(content_desc_contains="ADD")
    if ok:
        sleep(3)
        return True

    # Fallback to your restaurant-page ADD coordinate
    from tools.android_controller import tap
    tap(RESTAURANT_ADD_X, RESTAURANT_ADD_Y)
    sleep(3)
    return True


def _open_cart():
    ok, _ = tap_element(text_contains="Cart")
    if ok:
        sleep(3)
        return True

    ok, _ = tap_element(text_contains="View Cart")
    if ok:
        sleep(3)
        return True

    from tools.android_controller import tap
    tap(CART_BUTTON_X, CART_BUTTON_Y)
    sleep(3)
    return True


def prepare_zomato_order(item_or_cuisine: str, restaurant: str = "") -> dict:
    if not is_device_connected():
        return {"status": "failed", "message": "No Android device connected."}

    item_or_cuisine = item_or_cuisine.strip()
    restaurant = restaurant.strip()

    if not item_or_cuisine:
        return {"status": "failed", "message": "No food item or cuisine was provided."}

    ok, msg = open_app(ZOMATO_PACKAGE)
    if not ok:
        return {"status": "failed", "message": f"Could not open Zomato: {msg}"}

    sleep(7)

    # Step 1: open the real home search element
    if not _open_home_search():
        return {"status": "failed", "message": "Could not find Zomato home search element."}

    # Step 2: search restaurant if given, else search dish
    query = restaurant if restaurant else item_or_cuisine
    type_text(query)
    sleep(2)
    keyevent(66)
    sleep(5)

    # Step 3: open matching restaurant/result
    if restaurant:
        if not _open_restaurant_by_name(restaurant):
            # Fallback generic tap if exact match not found
            from tools.android_controller import tap
            tap(550, 350)
            sleep(5)
    else:
        from tools.android_controller import tap
        tap(550, 350)
        sleep(5)

    # Step 4: if restaurant was provided, search dish inside it
    if restaurant:
        _search_inside_restaurant(item_or_cuisine)

    # Step 5: add item
    if not _add_first_item():
        # Small scroll and retry
        swipe(500, 1600, 500, 900, 350)
        sleep(2)
        if not _add_first_item():
            return {"status": "failed", "message": "Could not add the item automatically."}

    # Step 6: open cart
    _open_cart()

    return {
        "status": "awaiting_final",
        "message": f"{item_or_cuisine} is ready in Zomato cart. Say 'final approve' to place the order."
    }


def finalize_zomato_order() -> str:
    if not is_device_connected():
        return "No Android device connected."

    ok, _ = tap_element(text_contains="Place Order")
    if ok:
        sleep(3)
        return "Order placed via Zomato."

    ok, _ = tap_element(text_contains="Proceed")
    if ok:
        sleep(3)
        return "Order placement step triggered via Zomato."

    ok, _ = tap_element(text_contains="Checkout")
    if ok:
        sleep(3)
        return "Checkout triggered via Zomato."

    ok, _ = tap_element(text_contains="Pay")
    if ok:
        sleep(3)
        return "Payment step triggered via Zomato."

    from tools.android_controller import tap
    tap(PLACE_ORDER_X, PLACE_ORDER_Y)
    sleep(3)
    return "Order placement tap sent via fallback coordinates."