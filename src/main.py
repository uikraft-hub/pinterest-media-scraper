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

Usage:
- cd src
- streamlit run main.py
"""

import streamlit as st
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
    
    def validate_pinterest_url(self, url):
        """Validate if the URL is a Pinterest URL"""
        pinterest_patterns = [
            r'https?://(?:www\.)?pinterest\.com/.+',
            r'https?://(?:[a-z]{2}\.)?pinterest\.com/.+',  # Support country-specific domains
            r'https?://pin\.it/.+',
        ]
        return any(re.match(pattern, url) for pattern in pinterest_patterns)
    
    def normalize_pinterest_url(self, url):
        """Normalize Pinterest URLs to work with different formats"""
        try:
            # If it's a short URL, resolve it first
            if 'pin.it' in url:
                try:
                    response = self.session.head(url, allow_redirects=True, timeout=10)
                    url = response.url
                except requests.exceptions.RequestException:
                    # If resolving fails, proceed with the original URL
                    pass

            # Convert in.pinterest.com or other country-specific domains to www.pinterest.com
            url = re.sub(r'https?://[a-z]{2}\.pinterest\.com', 'https://www.pinterest.com', url)
            
            # Ensure www prefix for pinterest.com
            url = re.sub(r'https?://pinterest\.com', 'https://www.pinterest.com', url)
            
            # Extract pin ID from various Pinterest URL formats
            pin_id = None
            
            # Handle pinterest.com/pin/ URLs
            pin_match = re.search(r'pinterest\.com/pin/(\d+)', url)
            if pin_match:
                pin_id = pin_match.group(1)
                # Return both original and pin.it format for testing
                return [url, f"https://pin.it/{pin_id}"]
            
            # Handle search URLs - extract individual pins if possible
            if 'search/pins' in url:
                return [url]  # Return as-is, will be handled by scraping
            
            return [url]
            
        except Exception as e:
            return [url]

    def get_media_info(self, url):
        """Get media information using requests and BeautifulSoup"""
        try:
            # Get normalized URLs
            urls_to_try = self.normalize_pinterest_url(url)
            
            for test_url in urls_to_try:
                try:
                    media_urls = []
                    
                    # Method 1: Direct page scraping
                    response = self.session.get(test_url, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for Pinterest data in script tags
                    script_tags = soup.find_all('script')
                    
                    for script in script_tags:
                        try:
                            script_content = script.string if script.string else str(script)
                            
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
                                matches = re.findall(pattern, script_content, re.IGNORECASE)
                                for match in matches:
                                    clean_url = match.replace('\\u002F', '/').replace('\\', '')
                                    clean_url = clean_url.replace('\\u003d', '=').replace('\\u0026', '&')
                                    
                                    if clean_url not in media_urls and self._is_valid_media_url(clean_url):
                                        # Try to get higher resolution version
                                        clean_url = self._get_higher_res_url(clean_url)
                                        media_urls.append(clean_url)
                            
                            # Look for video URLs
                            video_patterns = [
                                r'"url":"(https://[^"]*\.(?:mp4|webm|mov)[^"]*)"',
                                r'https://[^\s"\'<>]+\.(?:mp4|webm|mov)',
                                r'"videoUrl":"([^"]+)"',
                                r'"video":\{[^}]*"url":"([^"]+)"',
                            ]
                            
                            for pattern in video_patterns:
                                matches = re.findall(pattern, script_content, re.IGNORECASE)
                                for match in matches:
                                    clean_url = match.replace('\\u002F', '/').replace('\\', '')
                                    clean_url = clean_url.replace('\\u003d', '=').replace('\\u0026', '&')
                                    
                                    if clean_url not in media_urls and self._is_valid_media_url(clean_url):
                                        media_urls.append(clean_url)
                                        
                        except Exception as parse_error:
                            continue
                    
                    # Method 2: Look for meta tags
                    if not media_urls:
                        meta_tags = soup.find_all('meta', {'property': re.compile(r'og:image|twitter:image')})
                        for meta in meta_tags:
                            content = meta.get('content')
                            if content and self._is_valid_media_url(content):
                                media_urls.append(self._get_higher_res_url(content))
                    
                    # Method 3: Direct image and video tags
                    if not media_urls:
                        images = soup.find_all('img', {'src': True})
                        videos = soup.find_all('video', {'src': True})
                        
                        for img in images:
                            src = img.get('src')
                            if src and self._is_valid_media_url(src):
                                media_urls.append(self._get_higher_res_url(src))
                        
                        for video in videos:
                            src = video.get('src')
                            if src and self._is_valid_media_url(src):
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
            st.warning(f"Fallback method error: {str(e)}")
            return []
    
    def _get_higher_res_url(self, url):
        """Convert Pinterest image URLs to higher resolution versions"""
        try:
            # Replace common size indicators with originals
            size_patterns = [
                (r'/236x/', '/originals/'),
                (r'/474x/', '/originals/'),
                (r'/564x/', '/originals/'),
                (r'/736x/', '/originals/'),
                (r'_\d+x\d+\.', '_original.'),
            ]
            
            for pattern, replacement in size_patterns:
                url = re.sub(pattern, replacement, url)
            
            return url
        except:
            return url
    
    def _is_valid_media_url(self, url):
        """Check if URL is a valid media URL"""
        try:
            if not url or len(url) < 10:
                return False
                
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check for image/video extensions or known Pinterest domains
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.mov']
            valid_domains = ['pinimg.com', 'pinterest.com']
            
            url_lower = url.lower()
            
            return (any(ext in url_lower for ext in valid_extensions) or 
                    any(domain in parsed.netloc for domain in valid_domains)) and \
                   'placeholder' not in url_lower and 'default' not in url_lower
        except:
            return False
    
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
                
                response = self.session.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Determine file extension from URL or content type
                content_type = response.headers.get('content-type', '').lower()
                
                if '.jpg' in url.lower() or 'jpeg' in content_type:
                    ext = '.jpg'
                elif '.png' in url.lower() or 'png' in content_type:
                    ext = '.png'
                elif '.gif' in url.lower() or 'gif' in content_type:
                    ext = '.gif'
                elif '.webp' in url.lower() or 'webp' in content_type:
                    ext = '.webp'
                elif '.mp4' in url.lower() or 'mp4' in content_type:
                    ext = '.mp4'
                elif '.webm' in url.lower() or 'webm' in content_type:
                    ext = '.webm'
                elif 'image' in content_type:
                    ext = '.jpg'  # Default for images
                elif 'video' in content_type:
                    ext = '.mp4'  # Default for videos
                else:
                    ext = '.jpg'  # Ultimate fallback
                
                filename = f"pinterest_media_{i + 1:03d}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # Verify file was created and has content
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
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
            placeholder="https://pinterest.com/pin/... or https://pin.it/... or https://in.pinterest.com/pin/...",
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
                    media_urls = downloader.get_media_info(url)
                    
                    if media_urls:
                        st.session_state.media_urls = media_urls
                        st.session_state.analyzed_url = url
                        
                        # Show success with media type breakdown
                        image_count = sum(1 for url in media_urls if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']))
                        video_count = len(media_urls) - image_count
                        
                        st.markdown(f"""
                        <div class="status-success">
                            ✅ Found {len(media_urls)} media files<br>
                            📸 Images: {image_count} | 🎥 Videos: {video_count}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show first few URLs for debugging
                        with st.expander("🔍 Debug: Found URLs (first 5)"):
                            for i, media_url in enumerate(media_urls[:5]):
                                st.text(f"{i+1}. {media_url}")
                    else:
                        st.markdown("""
                        <div class="status-error">
                            ❌ No media files found. This could be due to:<br>
                            • Private/restricted Pinterest content<br>
                            • Invalid or expired URL<br>
                            • Pinterest's anti-scraping measures<br>
                            • Network connectivity issues
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Provide troubleshooting tips
                        with st.expander("💡 Troubleshooting Tips"):
                            st.write("""
                            **Try these solutions:**
                            1. Make sure the Pinterest URL is publicly accessible
                            2. Try using a pin.it short URL instead
                            3. Check if the pin still exists on Pinterest
                            4. Try a different Pinterest URL
                            5. Wait a few minutes and try again
                            6. For search URLs, try individual pin URLs instead
                            """)
            else:
                st.warning("Please enter a Pinterest URL")
    
    with col2:
        st.subheader("📊 Media Info")
        
        if hasattr(st.session_state, 'media_urls') and st.session_state.media_urls:
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
                        else:
                            st.write(f"Media {i+1}: {os.path.basename(media_url)}")
                    except:
                        st.write(f"Media {i+1}: {media_url[:50]}...")
    
    # Download section
    if hasattr(st.session_state, 'media_urls') and st.session_state.media_urls:
        st.subheader("⬇️ Download Options")
        
        media_count = len(st.session_state.media_urls)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Initialize download_count safely - Fixed the value error
            if 'download_count' not in st.session_state:
                st.session_state.download_count = min(media_count, 10)
            
            # Ensure the value doesn't exceed the media count
            current_value = min(st.session_state.download_count, media_count)
            
            download_count = st.number_input(
                "Number of files to download",
                min_value=1,
                max_value=media_count,
                value=current_value,
                key="download_count_input",
                help=f"Choose how many files to download (max: {media_count})"
            )
            
            # Update session state when number input changes
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
        
        # Display current selection
        st.info(f"📊 Will download: {st.session_state.download_count} out of {media_count} files")
        
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
                        max_files=st.session_state.download_count,
                        progress_callback=update_progress
                    )
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
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
                        ❌ No files were downloaded successfully. Please check the URLs and try again.
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
