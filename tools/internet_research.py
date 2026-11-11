import requests


def search_duckduckgo(query: str) -> dict:
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": 1,
            "no_html": 1
        }
        res = requests.get(url, params=params, timeout=20)
        res.raise_for_status()
        data = res.json()

        abstract = data.get("AbstractText", "")
        related = data.get("RelatedTopics", [])

        snippets = []
        for item in related[:5]:
            if isinstance(item, dict):
                text = item.get("Text")
                if text:
                    snippets.append(text)

        return {
            "ok": True,
            "query": query,
            "abstract": abstract,
            "snippets": snippets
        }
    except Exception as e:
        return {
            "ok": False,
            "query": query,
            "error": str(e)
        }