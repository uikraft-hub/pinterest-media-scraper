"""
Pinterest Media Downloader - Professional Pinterest Media Files Downloader
==============================================

Pinterest Media Downloader with Graphical User Interface
Streamlit-based desktop/web app to download images and videos from Pinterest.

Author: Ujjwal Nova
License: MIT
Repository: https://github.com/ukr-projects/pinterest-media-scraper

What's New:
- Improved URL normalization and validation
- Enhanced fallback scraping for more robust media extraction
- Better error handling and user feedback
- Cleaner UI: Includes quick-select buttons (e.g., "First 5", "First 10", "All Files") and improved download options for easier selection and downloading of media files

Features:
- Download images and videos from Pinterest pins, boards, and profiles
- Uses a custom scraping method to find media
- Download as original files or ZIP archive
- Quality and advanced settings (timeout, retries, concurrency)
- Professional UI with media preview and progress tracking

Dependencies:
- streamlit>=1.28.0
- requests>=2.31.0
- beautifulsoup4>=4.12.0
- Pillow>=10.0.0
- lxml>=4.9.0

Usage:s
- cd src
- streamlit run main.py
"""

import streamlit as st
from app.downloader import PinterestDownloader
from app.ui import setup_page, render_header, render_sidebar, render_main_interface, render_download_section, render_footer

def main():
    """
    Main function to run the Streamlit application.
    """
    setup_page()
    render_header()
    
    downloader = PinterestDownloader()
    
    render_sidebar()
    render_main_interface(downloader)
    render_download_section(downloader)
    
    render_footer()

if __name__ == "__main__":
    main()
