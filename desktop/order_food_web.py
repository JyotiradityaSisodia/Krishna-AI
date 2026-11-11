from __future__ import annotations

import sys
import time
from typing import Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


ZOMATO_URL = "https://www.zomato.com/"


def safe_fill(page, selectors: list[str], value: str, timeout: int = 5000) -> bool:
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            locator.fill(value)
            return True
        except Exception:
            continue
    return False


def safe_click(page, selectors: list[str], timeout: int = 5000) -> bool:
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            return True
        except Exception:
            continue
    return False


def click_restaurant_result(page, restaurant_name: str, timeout: int = 8000) -> bool:
    candidates = [
        f"text={restaurant_name}",
        f'a:has-text("{restaurant_name}")',
        f'div:has-text("{restaurant_name}")',
    ]

    for selector in candidates:
        try:
            locator = page.locator(selector).first
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            return True
        except Exception:
            continue

    # partial match fallback
    words = [w for w in restaurant_name.split() if w.strip()]
    if not words:
        return False

    partial = words[0]
    fallback_candidates = [
        f'text={partial}',
        f'a:has-text("{partial}")',
        f'div:has-text("{partial}")',
    ]

    for selector in fallback_candidates:
        try:
            locator = page.locator(selector).first
            locator.wait_for(state="visible", timeout=timeout)
            locator.click()
            return True
        except Exception:
            continue

    return False


def search_dish_inside_restaurant(page, dish_name: str, timeout: int = 7000) -> bool:
    selectors = [
        'input[placeholder*="Search"]',
        'input[placeholder*="search"]',
        'input[type="search"]',
        'input[type="text"]',
    ]

    if not safe_fill(page, selectors, dish_name, timeout=timeout):
        return False

    page.keyboard.press("Enter")
    return True


def order_food_web(item: str, restaurant: str, headless: bool = False) -> dict:
    result = {
        "success": False,
        "message": "",
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto(ZOMATO_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2500)

            # Handle common popups/buttons if present
            safe_click(page, [
                'button:has-text("Accept")',
                'button:has-text("I agree")',
                'button:has-text("Not now")',
                'button:has-text("Close")',
            ], timeout=2000)

            restaurant_query = restaurant.strip()

            # Global search
            filled = safe_fill(page, [
                'input[placeholder*="Search"]',
                'input[placeholder*="search"]',
                'input[type="search"]',
                'input[type="text"]',
            ], restaurant_query, timeout=6000)

            if not filled:
                result["message"] = "Could not find the Zomato search field on web."
                browser.close()
                return result

            page.keyboard.press("Enter")
            page.wait_for_timeout(4000)

            opened_restaurant = click_restaurant_result(page, restaurant_query, timeout=8000)

            if not opened_restaurant:
                result["message"] = f"Restaurant result not found on web: {restaurant_query}"
                browser.close()
                return result

            page.wait_for_timeout(4000)

            dish_query = item.strip()
            typed_dish = search_dish_inside_restaurant(page, dish_query, timeout=7000)

            if not typed_dish:
                result["message"] = (
                    f"Opened restaurant '{restaurant_query}', but could not find an internal dish search box."
                )
                browser.close()
                return result

            page.wait_for_timeout(2500)

            result["success"] = True
            result["message"] = (
                f"Opened Zomato web, searched restaurant '{restaurant_query}', and searched dish '{dish_query}'."
            )
            browser.close()
            return result

        except PlaywrightTimeoutError as e:
            result["message"] = f"Timeout during Zomato web flow: {e}"
            browser.close()
            return result
        except Exception as e:
            result["message"] = f"Web food flow error: {e}"
            browser.close()
            return result


def main():
    if len(sys.argv) < 3:
        print("Usage: python desktop/order_food_web.py \"dish\" \"restaurant\"")
        sys.exit(1)

    dish = sys.argv[1]
    restaurant = sys.argv[2]

    result = order_food_web(dish, restaurant, headless=False)
    print(result)


if __name__ == "__main__":
    main()