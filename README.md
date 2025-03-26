# Pinterest Downloader v1.0.0

A professional GUI application built with **PyQt6** and **gallery-dl** that allows you to download Pinterest images, videos, and GIFs with ease.

<p align="center">
  <img src="resources/logo.png" width="300" height="300" alt="SSTube Icon" />
</p>


## Features
![App Screenshot](resources/screenshot.png)
- **Intuitive User Interface:** Built with PyQt6 for a sleek, responsive design.
- **Theme Toggle:** Easily switch between dark and light modes using a custom toggle switch.
- **Simulation Mode:** Preview download details before starting the download process.
- **Download Limit Option:** For links containing over 100 items, choose to download only the first 100 images.
- **Force Download:** Overwrite existing files with a simple click.
- **Status and Progress Updates:** Stay informed about the download status through a responsive status bar and animated loader.

## Prerequisites

- **Python 3.7+** – Ensure you have an appropriate Python version installed.
- **[PyQt6](https://pypi.org/project/PyQt6/)** – For the GUI components.
- **[gallery-dl](https://github.com/mikf/gallery-dl)** – To handle the downloading from Pinterest.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YourUsername/PinterestDownloader.git
   cd PinterestDownloader
   ```

2. **Create and Activate a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application:**
   ```bash
   python app.py
   ```

2. **Download Process:**
   - **Enter** your Pinterest URL into the input field.
   - **Select** a folder for saving the downloaded files by clicking the folder icon.
   - Click on **Download** or **Force Download** to start the process.
   - If the link contains more than 100 images, a prompt will allow you to limit the download to the first 100 images.

3. **Toggle Themes:**
   - Use the toggle switch at the top-right to change between dark and light themes.

## Folder Structure

```
PinterestDownloader/
├─ resources/         # Icons, images, and other static assets
│   ├─ logo.png
│   ├─ moon.png
│   ├─ sun.png
│   └─ loader.gif
├─ app.py             # Main application script
├─ requirements.txt   # List of dependencies
├─ .gitignore         # Git ignore rules
├─ LICENSE            # License file
└─ README.md          # This file
```

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to enhance the project. Please follow standard GitHub flow and code guidelines.

## Support

If you have any questions or need support, please open an issue on GitHub.
