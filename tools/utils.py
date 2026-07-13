"""
utils.py
--------
Common helper functions shared across tools (web_search.py, scraper.py, and
the agents that use them).

Includes:
- Text cleaning
- URL validation
- Text truncation (for token/length limits)
- Retry decorator (for flaky network calls)
"""

import re
import time
from functools import wraps
from urllib.parse import urlparse


def clean_text(text: str) -> str:
    # Removes messy formatting left over from scraping (extra blank lines,
    # repeated spaces, weird invisible unicode characters)
    if not text:
        return ""

    text = re.sub(r"\n\s*\n+", "\n", text)   
    text = re.sub(r"[ \t]+", " ", text)      
    text = text.replace("\u200b", "").replace("\xa0", " ")  

    return text.strip()


def is_valid_url(url: str) -> bool:
    # Checks a URL is well-formed (has http/https + a domain) before
    # wasting a request trying to scrape it
    if not url:
        return False

    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except ValueError:
        return False


def truncate_text(text: str, max_chars: int = 4000) -> str:
    if not text or len(text) <= max_chars:
        return text

    truncated = text[:max_chars]

    last_period = truncated.rfind(". ")
    if last_period != -1 and last_period > max_chars * 0.5:
        truncated = truncated[: last_period + 1]

    return truncated.strip() + " [truncated]"


def retry(max_attempts: int = 3, delay_seconds: float = 1.0, backoff: float = 2.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay_seconds
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(current_delay)
                        current_delay *= backoff 

            raise last_exception  

        return wrapper
    return decorator


def dedupe_urls(urls: list[str]) -> list[str]:
    # Removes duplicate URLs (e.g. "site.com" and "site.com/") from a list
    # while keeping the original order
    seen = set()
    unique_urls = []
    for url in urls:
        normalized = url.rstrip("/")
        if normalized not in seen:
            seen.add(normalized)
            unique_urls.append(url)
    return unique_urls