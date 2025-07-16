import unittest
import os
import requests_mock
from src.app.downloader import PinterestDownloader


class TestPinterestDownloader(unittest.TestCase):
    def setUp(self):
        self.downloader = PinterestDownloader()
        self.test_dir = "test_images"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)

    @requests_mock.Mocker()
    def test_get_media_info(self, m):
        # Mock the response from Pinterest
        test_url = "https://www.pinterest.com/pin/12345/"
        mock_html = """
        <html>
            <script>
                // This is a dummy script to make the content length > 100 characters.
                // The important part is the URL below.
                {"some_json_key": "some_value", "url":"https://i.pinimg.com/originals/test.jpg"}
            </script>
        </html>
        """
        m.get(test_url, text=mock_html)

        media_urls = self.downloader.get_media_info(test_url)
        self.assertIn("https://i.pinimg.com/originals/test.jpg", media_urls)

    @requests_mock.Mocker()
    def test_download_media(self, m):
        # Mock the image download
        image_url = "https://i.pinimg.com/originals/test.jpg"
        m.get(image_url, content=b"test image data")

        downloaded_files = self.downloader.download_media([image_url], self.test_dir)
        self.assertEqual(len(downloaded_files), 1)
        self.assertTrue(os.path.exists(downloaded_files[0]))


if __name__ == "__main__":
    unittest.main()
