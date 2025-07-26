"""
Project: pinterest-media-scraper
Author: ukr
License: MIT
Repository: https://github.com/uikraft-hub/pinterest-media-scraper
"""

import streamlit as st
from app.downloader import PinterestDownloader
from app.ui import (
    setup_page,
    render_header,
    render_sidebar,
    render_main_interface,
    render_download_section,
    render_footer,
)


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
