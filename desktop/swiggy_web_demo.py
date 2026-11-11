from __future__ import annotations

import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def first_visible(page, selectors: list[str], timeout: int = 5000):
    for selector in selectors:
        try:
            loc = page.locator(selector).first
            loc.wait_for(state="visible", timeout=timeout)
            return loc
        except Exception:
            continue
    return None


def swiggy_demo(restaurant: str, dish: str, headless: bool = False) -> dict:
    result = {"success": False, "message": ""}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://www.swiggy.com/", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)

            # Search field on homepage / search pages
            search = first_visible(
                page,
                [
                    'input[placeholder*="Search"]',
                    'input[placeholder*="search"]',
                    'input[type="text"]',
                    'input[type="search"]',
                ],
                timeout=7000,
            )

            if search is None:
                result["message"] = "Could not find Swiggy search field."
                browser.close()
                return result

            search.click()
            search.fill(restaurant)
            page.keyboard.press("Enter")
            page.wait_for_timeout(4000)

            # Try opening restaurant result
            restaurant_loc = first_visible(
                page,
                [
                    f'text="{restaurant}"',
                    f'a:has-text("{restaurant}")',
                    f'div:has-text("{restaurant}")',
                ],
                timeout=8000,
            )

            if restaurant_loc is None:
                result["message"] = f"Restaurant result not found: {restaurant}"
                browser.close()
                return result

            restaurant_loc.click()
            page.wait_for_timeout(4000)

            # Try searching dish inside restaurant page
            dish_search = first_visible(
                page,
                [
                    'input[placeholder*="Search"]',
                    'input[placeholder*="search"]',
                    'input[type="search"]',
                    'input[type="text"]',
                ],
                timeout=6000,
            )

            if dish_search is None:
                result["message"] = (
                    f"Opened restaurant '{restaurant}', but could not find in-restaurant search."
                )
                browser.close()
                return result

            dish_search.click()
            dish_search.fill(dish)
            page.keyboard.press("Enter")
            page.wait_for_timeout(3000)

            result["success"] = True
            result["message"] = (
                f"Opened Swiggy, searched restaurant '{restaurant}', and searched dish '{dish}'."
            )
            browser.close()
            return result

        except PlaywrightTimeoutError as e:
            result["message"] = f"Timeout during Swiggy flow: {e}"
            browser.close()
            return result
        except Exception as e:
            result["message"] = f"Swiggy flow error: {e}"
            browser.close()
            return result


def main():
    if len(sys.argv) < 3:
        print('Usage: python desktop\\swiggy_web_demo.py "Sagar Gaire Fast Food" "veg biryani"')
        return

    restaurant = sys.argv[1]
    dish = sys.argv[2]
    print(swiggy_demo(restaurant, dish, headless=False))


if __name__ == "__main__":
    main()