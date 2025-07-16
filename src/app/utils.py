"""
Utility functions for the Pinterest Media Downloader.

This module contains helper functions for URL validation, normalization,
and other miscellaneous tasks.
"""

import re
import requests
from urllib.parse import urlparse


def validate_pinterest_url(url):
    """
    Validate if the URL is a valid Pinterest URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is a valid Pinterest URL, False otherwise.
    """
    pinterest_patterns = [
        r"https?://(?:www\.)?pinterest\.com/.+",
        r"https?://(?:[a-z]{2}\.)?pinterest\.com/.+",  # Support country-specific domains
        r"https?://pin\.it/.+",
    ]
    return any(re.match(pattern, url) for pattern in pinterest_patterns)


def normalize_pinterest_url(session, url):
    """
    Normalize Pinterest URLs to handle different formats and resolve short URLs.

    Args:
        session: The requests.Session object to use for resolving short URLs.
        url (str): The URL to normalize.

    Returns:
        list: A list of normalized URLs to try.
    """
    try:
        # If it's a short URL, resolve it first
        if "pin.it" in url:
            try:
                response = session.head(url, allow_redirects=True, timeout=10)
                url = response.url
            except requests.exceptions.RequestException:
                # If resolving fails, proceed with the original URL
                pass

        # Convert in.pinterest.com or other country-specific domains to www.pinterest.com
        url = re.sub(
            r"https?://[a-z]{2}\.pinterest\.com", "https://www.pinterest.com", url
        )

        # Ensure www prefix for pinterest.com
        url = re.sub(r"https?://pinterest\.com", "https://www.pinterest.com", url)

        # Extract pin ID from various Pinterest URL formats
        pin_id = None

        # Handle pinterest.com/pin/ URLs
        pin_match = re.search(r"pinterest\.com/pin/(\d+)", url)
        if pin_match:
            pin_id = pin_match.group(1)
            # Return both original and pin.it format for testing
            return [url, f"https://pin.it/{pin_id}"]

        # Handle search URLs - extract individual pins if possible
        if "search/pins" in url:
            return [url]  # Return as-is, will be handled by scraping

        return [url]

    except Exception as e:
        return [url]


def get_higher_res_url(url):
    """
    Convert Pinterest image URLs to higher resolution versions.

    Args:
        url (str): The image URL.

    Returns:
        str: The URL modified to point to a higher resolution version, if possible.
    """
    try:
        # Replace common size indicators with originals
        size_patterns = [
            (r"/236x/", "/originals/"),
            (r"/474x/", "/originals/"),
            (r"/564x/", "/originals/"),
            (r"/736x/", "/originals/"),
            (r"_\d+x\d+\.", "_original."),
        ]

        for pattern, replacement in size_patterns:
            url = re.sub(pattern, replacement, url)

        return url
    except:
        return url


def is_valid_media_url(url):
    """
    Check if a URL is a valid media URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a valid media URL, False otherwise.
    """
    try:
        if not url or len(url) < 10:
            return False

        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check for image/video extensions or known Pinterest domains
        valid_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".mp4",
            ".webm",
            ".mov",
        ]
        valid_domains = ["pinimg.com", "pinterest.com"]

        url_lower = url.lower()

        return (
            (
                any(ext in url_lower for ext in valid_extensions)
                or any(domain in parsed.netloc for domain in valid_domains)
            )
            and "placeholder" not in url_lower
            and "default" not in url_lower
        )
    except:
        return False
