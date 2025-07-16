"""
UI Module for the Pinterest Media Downloader.

This module contains all the Streamlit components for the user interface.
"""

import os
import tempfile
import shutil
import streamlit as st
from .downloader import PinterestDownloader
from .utils import validate_pinterest_url


def setup_page():
    """
    Configures the Streamlit page and applies custom CSS.
    """
    st.set_page_config(
        page_title="pinterest-media-scraper",
        page_icon="📌",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
    <style>
        .main-header {
            background: linear-gradient(90deg, #e60023 0%, #bd081c 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(230, 0, 35, 0.3);
        }
        
        .download-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid #e60023;
        }
        
        .status-success {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }
        
        .status-error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #dc3545;
            margin: 1rem 0;
        }
        
        .status-info {
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 1rem;
            border-radius: 5px;
            border-left: 4px solid #17a2b8;
            margin: 1rem 0;
        }
        
        .media-preview {
            max-width: 200px;
            max-height: 200px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 0.5rem;
        }
        
        .progress-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def render_header():
    """
    Renders the main header of the application.
    """
    st.markdown(
        """
    <div class="main-header">
        <h1>📌 Pinterest Media Downloader</h1>
        <p>Professional tool to download images and videos from Pinterest</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """
    Renders the sidebar with settings.
    """
    with st.sidebar:
        st.header("⚙️ Settings")

        st.selectbox(
            "Download Quality", ["High", "Medium", "Low"], index=0, key="quality"
        )

        st.selectbox(
            "Output Format", ["Original", "ZIP Archive"], index=1, key="output_format"
        )

        with st.expander("Advanced Settings"):
            st.slider("Request Timeout (seconds)", 5, 60, 30, key="timeout")
            st.slider("Max Retries", 1, 5, 3, key="max_retries")
            st.slider("Concurrent Downloads", 1, 10, 3, key="concurrent_downloads")


def render_main_interface(downloader):
    """
    Renders the main interface for URL input and analysis.
    """
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📥 Download Pinterest Media")

        url = st.text_input(
            "Pinterest URL",
            placeholder="https://pinterest.com/pin/... or https://pin.it/... or https://in.pinterest.com/pin/...",
            help="Enter a Pinterest pin URL, board URL, or profile URL",
        )

        if url and not validate_pinterest_url(url):
            st.markdown(
                """
            <div class="status-error">
                ❌ Invalid Pinterest URL. Please enter a valid Pinterest link.
            </div>
            """,
                unsafe_allow_html=True,
            )
            return

        if st.button("🔍 Analyze URL", type="primary", use_container_width=True):
            if url:
                with st.spinner("Analyzing Pinterest URL..."):
                    media_urls = downloader.get_media_info(url)

                    if media_urls:
                        st.session_state.media_urls = media_urls
                        st.session_state.analyzed_url = url

                        image_count = sum(
                            1
                            for u in media_urls
                            if any(
                                ext in u.lower()
                                for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                            )
                        )
                        video_count = len(media_urls) - image_count

                        st.markdown(
                            f"""
                        <div class="status-success">
                            ✅ Found {len(media_urls)} media files<br>
                            📸 Images: {image_count} | 🎥 Videos: {video_count}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        with st.expander("🔍 Debug: Found URLs (first 5)"):
                            for i, media_url in enumerate(media_urls[:5]):
                                st.text(f"{i+1}. {media_url}")
                    else:
                        st.markdown(
                            """
                        <div class="status-error">
                            ❌ No media files found. This could be due to:<br>
                            • Private/restricted Pinterest content<br>
                            • Invalid or expired URL<br>
                            • Pinterest's anti-scraping measures<br>
                            • Network connectivity issues
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        with st.expander("💡 Troubleshooting Tips"):
                            st.write(
                                """
                            **Try these solutions:**
                            1. Make sure the Pinterest URL is publicly accessible
                            2. Try using a pin.it short URL instead
                            3. Check if the pin still exists on Pinterest
                            4. Try a different Pinterest URL
                            5. Wait a few minutes and try again
                            6. For search URLs, try individual pin URLs instead
                            """
                            )
            else:
                st.warning("Please enter a Pinterest URL")

    with col2:
        st.subheader("📊 Media Info")

        if "media_urls" in st.session_state and st.session_state.media_urls:
            media_count = len(st.session_state.media_urls)
            st.metric("Total Media Files", media_count)

            if media_count > 0:
                st.write("**Preview:**")
                preview_urls = st.session_state.media_urls[:3]

                for i, media_url in enumerate(preview_urls):
                    try:
                        if any(
                            ext in media_url.lower()
                            for ext in [".jpg", ".jpeg", ".png", ".gif"]
                        ):
                            st.image(media_url, width=150, caption=f"Image {i+1}")
                        else:
                            st.write(f"Media {i+1}: {os.path.basename(media_url)}")
                    except:
                        st.write(f"Media {i+1}: {media_url[:50]}...")


def render_download_section(downloader):
    """
    Renders the download options and handles the download process.
    """
    if "media_urls" in st.session_state and st.session_state.media_urls:
        st.subheader("⬇️ Download Options")

        media_count = len(st.session_state.media_urls)

        col1, col2, col3 = st.columns(3)

        with col1:
            if "download_count" not in st.session_state:
                st.session_state.download_count = min(media_count, 10)

            current_value = min(st.session_state.download_count, media_count)

            download_count = st.number_input(
                "Number of files to download",
                min_value=1,
                max_value=media_count,
                value=current_value,
                key="download_count_input",
            )
            st.session_state.download_count = download_count

        with col2:
            st.write("**Quick Select:**")
            if st.button("📱 First 5", use_container_width=True):
                st.session_state.download_count = min(5, media_count)
                st.rerun()
            if st.button("📋 First 10", use_container_width=True):
                st.session_state.download_count = min(10, media_count)
                st.rerun()

        with col3:
            st.write("**Download All:**")
            if st.button("📦 All Files", use_container_width=True):
                st.session_state.download_count = media_count
                st.rerun()

        st.info(
            f"📊 Will download: {st.session_state.download_count} out of {media_count} files"
        )

        if st.button("🚀 Start Download", type="primary", use_container_width=True):
            temp_dir = tempfile.mkdtemp()

            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(current, total, message):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(message)

                with st.spinner("Downloading media files..."):
                    downloaded_files = downloader.download_media(
                        st.session_state.media_urls,
                        temp_dir,
                        max_files=st.session_state.download_count,
                        progress_callback=update_progress,
                    )

                progress_bar.empty()
                status_text.empty()

                if downloaded_files:
                    st.markdown(
                        f"""
                    <div class="status-success">
                        ✅ Successfully downloaded {len(downloaded_files)} files
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    if st.session_state.output_format == "ZIP Archive":
                        zip_path = os.path.join(temp_dir, "pinterest_media.zip")
                        downloader.create_zip(downloaded_files, zip_path)

                        with open(zip_path, "rb") as f:
                            st.download_button(
                                label="📦 Download ZIP Archive",
                                data=f.read(),
                                file_name="pinterest_media.zip",
                                mime="application/zip",
                                use_container_width=True,
                            )
                    else:
                        st.write("**Download Individual Files:**")
                        for file_path in downloaded_files:
                            with open(file_path, "rb") as f:
                                filename = os.path.basename(file_path)
                                st.download_button(
                                    label=f"📄 {filename}",
                                    data=f.read(),
                                    file_name=filename,
                                    use_container_width=True,
                                )
                else:
                    st.markdown(
                        """
                    <div class="status-error">
                        ❌ No files were downloaded successfully. Please check the URLs and try again.
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                st.error(f"Download failed: {str(e)}")

            finally:
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass


def render_footer():
    """
    Renders the footer section of the application.
    """
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>💡 <strong>Tips:</strong> This tool works with Pinterest pins, boards, and profiles. 
        For best results, use direct Pinterest URLs.</p>
        <p>⚠️ <strong>Note:</strong> Please respect Pinterest's terms of service and copyright laws.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
