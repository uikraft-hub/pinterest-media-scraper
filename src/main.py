import streamlit as st
import gallery_dl
import requests
from bs4 import BeautifulSoup
import os
import json
import tempfile
import shutil
import zipfile
from pathlib import Path
import threading
import time
from urllib.parse import urlparse, urljoin
import re
from PIL import Image
import io
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="Pinterest Media Downloader",
    page_icon="📌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
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
""", unsafe_allow_html=True)

class PinterestDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def validate_pinterest_url(self, url):
        """Validate if the URL is a Pinterest URL"""
        pinterest_patterns = [
            r'https?://(?:www\.)?pinterest\.com/.+',
            r'https?://pin\.it/.+',
        ]
        return any(re.match(pattern, url) for pattern in pinterest_patterns)
    
    def get_media_info_gallery_dl(self, url):
        """Get media information using gallery-dl"""
        try:
            # Configure gallery-dl
            config = {
                'extractor': {
                    'pinterest': {
                        'videos': True,
                        'boards': True,
                    }
                }
            }
            
            # Create a temporary directory for testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Set up gallery-dl job
                job = gallery_dl.job.DownloadJob(url, {
                    'base-directory': temp_dir,
                    'skip': True,  # Don't actually download, just get info
                    **config
                })
                
                # Extract URLs
                urls = []
                for msg in job:
                    if hasattr(msg, 'url'):
                        urls.append(msg.url)
                
                return urls
        except Exception as e:
            st.error(f"Gallery-dl failed: {str(e)}")
            return None
    
    def get_media_info_fallback(self, url):
        """Fallback method using requests and BeautifulSoup"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Pinterest data in script tags
            script_tags = soup.find_all('script', {'id': 'initial-state'})
            media_urls = []
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    # Extract media URLs from Pinterest's data structure
                    self._extract_media_from_data(data, media_urls)
                except:
                    continue
            
            # Fallback: look for img and video tags
            if not media_urls:
                images = soup.find_all('img', {'src': True})
                videos = soup.find_all('video', {'src': True})
                
                for img in images:
                    src = img.get('src')
                    if src and ('pinimg.com' in src or 'pinterest' in src):
                        media_urls.append(src)
                
                for video in videos:
                    src = video.get('src')
                    if src:
                        media_urls.append(src)
            
            return media_urls
        except Exception as e:
            st.error(f"Fallback method failed: {str(e)}")
            return []
    
    def _extract_media_from_data(self, data, media_urls):
        """Recursively extract media URLs from Pinterest data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['url', 'src'] and isinstance(value, str):
                    if any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']):
                        media_urls.append(value)
                elif isinstance(value, (dict, list)):
                    self._extract_media_from_data(value, media_urls)
        elif isinstance(data, list):
            for item in data:
                self._extract_media_from_data(item, media_urls)
    
    def download_media(self, urls, output_dir, max_files=None, progress_callback=None):
        """Download media files"""
        downloaded_files = []
        
        if max_files:
            urls = urls[:max_files]
        
        total_files = len(urls)
        
        for i, url in enumerate(urls):
            try:
                if progress_callback:
                    progress_callback(i + 1, total_files, f"Downloading {i + 1}/{total_files}")
                
                response = self.session.get(url, stream=True)
                response.raise_for_status()
                
                # Determine file extension
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    ext = '.jpg' if 'jpeg' in content_type else '.png'
                elif 'video' in content_type:
                    ext = '.mp4'
                else:
                    ext = '.jpg'  # Default
                
                filename = f"pinterest_media_{i + 1:03d}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                downloaded_files.append(filepath)
                
            except Exception as e:
                if progress_callback:
                    progress_callback(i + 1, total_files, f"Error downloading {i + 1}: {str(e)}")
                continue
        
        return downloaded_files
    
    def create_zip(self, files, zip_path):
        """Create a zip file from downloaded files"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files:
                zipf.write(file_path, os.path.basename(file_path))

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📌 Pinterest Media Downloader</h1>
        <p>Professional tool to download images and videos from Pinterest</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize downloader
    downloader = PinterestDownloader()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Quality settings
        quality = st.selectbox(
            "Download Quality",
            ["High", "Medium", "Low"],
            index=0
        )
        
        # Output format
        output_format = st.selectbox(
            "Output Format",
            ["Original", "ZIP Archive"],
            index=1
        )
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            timeout = st.slider("Request Timeout (seconds)", 5, 60, 30)
            max_retries = st.slider("Max Retries", 1, 5, 3)
            concurrent_downloads = st.slider("Concurrent Downloads", 1, 10, 3)
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📥 Download Pinterest Media")
        
        # URL input
        url = st.text_input(
            "Pinterest URL",
            placeholder="https://pinterest.com/pin/... or https://pin.it/...",
            help="Enter a Pinterest pin URL, board URL, or profile URL"
        )
        
        # Validate URL
        if url and not downloader.validate_pinterest_url(url):
            st.markdown("""
            <div class="status-error">
                ❌ Invalid Pinterest URL. Please enter a valid Pinterest link.
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Analyze button
        if st.button("🔍 Analyze URL", type="primary", use_container_width=True):
            if url:
                with st.spinner("Analyzing Pinterest URL..."):
                    # Try gallery-dl first
                    media_urls = downloader.get_media_info_gallery_dl(url)
                    
                    # Fallback to custom method
                    if not media_urls:
                        st.info("Gallery-dl failed, trying alternative method...")
                        media_urls = downloader.get_media_info_fallback(url)
                    
                    if media_urls:
                        st.session_state.media_urls = media_urls
                        st.session_state.analyzed_url = url
                        
                        st.markdown(f"""
                        <div class="status-success">
                            ✅ Found {len(media_urls)} media files
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="status-error">
                            ❌ No media files found or unable to access the URL
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a Pinterest URL")
    
    with col2:
        st.subheader("📊 Media Info")
        
        if hasattr(st.session_state, 'media_urls'):
            media_count = len(st.session_state.media_urls)
            
            st.metric("Total Media Files", media_count)
            
            # Preview some media
            if media_count > 0:
                st.write("**Preview:**")
                preview_urls = st.session_state.media_urls[:3]  # Show first 3
                
                for i, media_url in enumerate(preview_urls):
                    try:
                        if any(ext in media_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                            st.image(media_url, width=150, caption=f"Image {i+1}")
                    except:
                        st.write(f"Media {i+1}: {media_url[:50]}...")
    
    # Download section
    if hasattr(st.session_state, 'media_urls') and st.session_state.media_urls:
        st.subheader("⬇️ Download Options")
        
        media_count = len(st.session_state.media_urls)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            download_count = st.number_input(
                "Number of files to download",
                min_value=1,
                max_value=media_count,
                value=min(media_count, 10),
                help=f"Choose how many files to download (max: {media_count})"
            )
        
        with col2:
            st.write("**Quick Select:**")
            if st.button("📱 First 5", use_container_width=True):
                st.session_state.download_count = min(5, media_count)
            if st.button("📋 First 10", use_container_width=True):
                st.session_state.download_count = min(10, media_count)
        
        with col3:
            st.write("**Download All:**")
            if st.button("📦 All Files", use_container_width=True):
                st.session_state.download_count = media_count
        
        # Update download count if set by buttons
        if hasattr(st.session_state, 'download_count'):
            download_count = st.session_state.download_count
        
        # Download button
        if st.button("🚀 Start Download", type="primary", use_container_width=True):
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total, message):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                # Download files
                with st.spinner("Downloading media files..."):
                    downloaded_files = downloader.download_media(
                        st.session_state.media_urls,
                        temp_dir,
                        max_files=download_count,
                        progress_callback=update_progress
                    )
                
                if downloaded_files:
                    st.markdown(f"""
                    <div class="status-success">
                        ✅ Successfully downloaded {len(downloaded_files)} files
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create ZIP if requested
                    if output_format == "ZIP Archive":
                        zip_path = os.path.join(temp_dir, "pinterest_media.zip")
                        downloader.create_zip(downloaded_files, zip_path)
                        
                        # Provide download link
                        with open(zip_path, "rb") as f:
                            st.download_button(
                                label="📦 Download ZIP Archive",
                                data=f.read(),
                                file_name="pinterest_media.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                    else:
                        # Individual file downloads
                        st.write("**Download Individual Files:**")
                        for file_path in downloaded_files:
                            with open(file_path, "rb") as f:
                                filename = os.path.basename(file_path)
                                st.download_button(
                                    label=f"📄 {filename}",
                                    data=f.read(),
                                    file_name=filename,
                                    use_container_width=True
                                )
                else:
                    st.markdown("""
                    <div class="status-error">
                        ❌ No files were downloaded successfully
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Download failed: {str(e)}")
            
            finally:
                # Cleanup
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>💡 <strong>Tips:</strong> This tool works with Pinterest pins, boards, and profiles. 
        For best results, use direct Pinterest URLs.</p>
        <p>⚠️ <strong>Note:</strong> Please respect Pinterest's terms of service and copyright laws.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()