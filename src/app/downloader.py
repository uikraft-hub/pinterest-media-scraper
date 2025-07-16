"""
Pinterest Media Downloader Module.

This module defines the PinterestDownloader class, which handles
the core logic for scraping and downloading media from Pinterest.
"""

import os
import re
import zipfile
import requests
from bs4 import BeautifulSoup
from .utils import normalize_pinterest_url, get_higher_res_url, is_valid_media_url


class PinterestDownloader:
    """
    A class to download media from Pinterest.
    """

    def __init__(self):
        """
        Initializes the PinterestDownloader with a requests session.
        """
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
            }
        )

    def get_media_info(self, url):
        """
        Get media information using requests and BeautifulSoup.

        Args:
            url (str): The Pinterest URL to scrape.

        Returns:
            list: A list of media URLs found on the page.
        """
        try:
            # Get normalized URLs
            urls_to_try = normalize_pinterest_url(self.session, url)

            for test_url in urls_to_try:
                try:
                    media_urls = []

                    # Method 1: Direct page scraping
                    response = self.session.get(test_url, timeout=30)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, "html.parser")

                    # Look for Pinterest data in script tags
                    script_tags = soup.find_all("script")

                    for script in script_tags:
                        try:
                            script_content = (
                                script.string if script.string else str(script)
                            )

                            # Skip if script is too small
                            if len(script_content) < 100:
                                continue

                            # Look for image URLs in script content with more patterns
                            img_patterns = [
                                r'"url":"(https://i\.pinimg\.com/[^"]+\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',
                                r'"images":\{[^}]*"orig":\{[^}]*"url":"([^"]+)"',
                                r'"url":"(https://[^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',
                                r'https://i\.pinimg\.com/[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp)',
                                r'"richPinData":[^}]*"url":"([^"]+\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',
                                r'"imageSpec_[^"]*":"([^"]+\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',
                            ]

                            for pattern in img_patterns:
                                matches = re.findall(
                                    pattern, script_content, re.IGNORECASE
                                )
                                for match in matches:
                                    clean_url = match.replace("\\u002F", "/").replace(
                                        "\\", ""
                                    )
                                    clean_url = clean_url.replace(
                                        "\\u003d", "="
                                    ).replace("\\u0026", "&")

                                    if (
                                        clean_url not in media_urls
                                        and is_valid_media_url(clean_url)
                                    ):
                                        # Try to get higher resolution version
                                        clean_url = get_higher_res_url(clean_url)
                                        media_urls.append(clean_url)

                            # Look for video URLs
                            video_patterns = [
                                r'"url":"(https://[^"]*\.(?:mp4|webm|mov)[^"]*)"',
                                r'https://[^\s"\'<>]+\.(?:mp4|webm|mov)',
                                r'"videoUrl":"([^"]+)"',
                                r'"video":\{[^}]*"url":"([^"]+)"',
                            ]

                            for pattern in video_patterns:
                                matches = re.findall(
                                    pattern, script_content, re.IGNORECASE
                                )
                                for match in matches:
                                    clean_url = match.replace("\\u002F", "/").replace(
                                        "\\", ""
                                    )
                                    clean_url = clean_url.replace(
                                        "\\u003d", "="
                                    ).replace("\\u0026", "&")

                                    if (
                                        clean_url not in media_urls
                                        and is_valid_media_url(clean_url)
                                    ):
                                        media_urls.append(clean_url)

                        except Exception as parse_error:
                            continue

                    # Method 2: Look for meta tags
                    if not media_urls:
                        meta_tags = soup.find_all(
                            "meta", {"property": re.compile(r"og:image|twitter:image")}
                        )
                        for meta in meta_tags:
                            content = meta.get("content")
                            if content and is_valid_media_url(content):
                                media_urls.append(get_higher_res_url(content))

                    # Method 3: Direct image and video tags
                    if not media_urls:
                        images = soup.find_all("img", {"src": True})
                        videos = soup.find_all("video", {"src": True})

                        for img in images:
                            src = img.get("src")
                            if src and is_valid_media_url(src):
                                media_urls.append(get_higher_res_url(src))

                        for video in videos:
                            src = video.get("src")
                            if src and is_valid_media_url(src):
                                media_urls.append(src)

                    # Remove duplicates
                    unique_urls = []
                    for url_item in media_urls:
                        if url_item not in unique_urls:
                            unique_urls.append(url_item)

                    if unique_urls:
                        return unique_urls

                except Exception as url_error:
                    continue

            return []

        except Exception as e:
            print(f"Fallback method error: {str(e)}")
            return []

    def download_media(self, urls, output_dir, max_files=None, progress_callback=None):
        """
        Download media files from a list of URLs.

        Args:
            urls (list): A list of media URLs to download.
            output_dir (str): The directory to save the downloaded files.
            max_files (int, optional): The maximum number of files to download. Defaults to None.
            progress_callback (function, optional): A callback function for progress updates. Defaults to None.

        Returns:
            list: A list of file paths for the downloaded files.
        """
        downloaded_files = []

        if max_files:
            urls = urls[:max_files]

        total_files = len(urls)

        for i, url in enumerate(urls):
            try:
                if progress_callback:
                    progress_callback(
                        i + 1, total_files, f"Downloading {i + 1}/{total_files}"
                    )

                response = self.session.get(url, stream=True, timeout=30)
                response.raise_for_status()

                # Determine file extension from URL or content type
                content_type = response.headers.get("content-type", "").lower()

                if ".jpg" in url.lower() or "jpeg" in content_type:
                    ext = ".jpg"
                elif ".png" in url.lower() or "png" in content_type:
                    ext = ".png"
                elif ".gif" in url.lower() or "gif" in content_type:
                    ext = ".gif"
                elif ".webp" in url.lower() or "webp" in content_type:
                    ext = ".webp"
                elif ".mp4" in url.lower() or "mp4" in content_type:
                    ext = ".mp4"
                elif ".webm" in url.lower() or "webm" in content_type:
                    ext = ".webm"
                elif "image" in content_type:
                    ext = ".jpg"  # Default for images
                elif "video" in content_type:
                    ext = ".mp4"  # Default for videos
                else:
                    ext = ".jpg"  # Ultimate fallback

                filename = f"pinterest_media_{i + 1:03d}{ext}"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # Verify file was created and has content
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    downloaded_files.append(filepath)

            except Exception as e:
                if progress_callback:
                    progress_callback(
                        i + 1, total_files, f"Error downloading {i + 1}: {str(e)}"
                    )
                continue

        return downloaded_files

    def create_zip(self, files, zip_path):
        """
        Create a zip file from a list of files.

        Args:
            files (list): A list of file paths to include in the zip file.
            zip_path (str): The path to create the zip file.
        """
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                zipf.write(file_path, os.path.basename(file_path))
