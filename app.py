import sys
import os
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPoint, QPropertyAnimation
from PyQt6.QtGui import QIcon, QFont, QMovie, QPainter, QColor, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QMenuBar,
    QStatusBar,
)


# Custom ToggleSwitch widget with sliding knob and animated icon change.
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(100, 50)
        self.knob_size = 25
        self.margin = 10  # margin from left/right edge
        self._checked = False

        # Create knob as a QLabel; its pixmap will show the icon.
        self.knob = QLabel(self)
        self.knob.setFixedSize(self.knob_size, self.knob_size)
        self.knob.setScaledContents(True)
        self.knob.setPixmap(
            QIcon("resources/moon.png").pixmap(self.knob_size, self.knob_size)
        )

        # Position knob at initial (unchecked/dark) state.
        self.knob.move(self.margin, (self.height() - self.knob_size) // 2)

        # Create an animation for the knob movement.
        self.anim = QPropertyAnimation(self.knob, b"pos", self)
        self.anim.setDuration(300)

    @property
    def checked(self):
        return self._checked

    def setChecked(self, state):
        if self._checked == state:
            return
        self._checked = state
        self.animate_knob()
        self.toggled.emit(self._checked)
        self.update()

    def animate_knob(self):
        # Compute start and end positions.
        y = (self.height() - self.knob_size) // 2
        if self._checked:
            # Slide to right for light theme.
            end_pos = QPoint(self.width() - self.knob_size - self.margin, y)
        else:
            # Slide to left for dark theme.
            end_pos = QPoint(self.margin, y)
        self.anim.stop()
        self.anim.setStartValue(self.knob.pos())
        self.anim.setEndValue(end_pos)
        self.anim.start()
        # Change icon during the animation (for a smooth effect, you might update at halfway).
        # Here we simply update immediately.
        if self._checked:
            self.knob.setPixmap(
                QIcon("resources/sun.png").pixmap(self.knob_size, self.knob_size)
            )
        else:
            self.knob.setPixmap(
                QIcon("resources/moon.png").pixmap(self.knob_size, self.knob_size)
            )

    def mousePressEvent(self, event):
        # Toggle state when the user clicks on the widget.
        self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        # Draw the background of the toggle switch.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        radius = self.height() // 2
        # Set background colors based on state.
        if self._checked:
            bg_color = QColor("#d8dbe0")
        else:
            bg_color = QColor("#28292c")
        pen = QPen(bg_color, 3)
        painter.setPen(pen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(self.rect(), radius, radius)
        painter.end()


# Threads for simulation and download (same as before).
class SimulationThread(QThread):
    finished_signal = pyqtSignal(bool, int, str)

    def __init__(self, url, timeout=120, parent=None):
        super().__init__(parent)
        self.url = url
        self.timeout = timeout

    def run(self):
        try:
            simulate_cmd = ["gallery-dl", "--simulate", "--ignore-config", self.url]
            process = subprocess.run(
                simulate_cmd, capture_output=True, text=True, timeout=self.timeout
            )
            output = process.stdout
            items = [line for line in output.splitlines() if line.strip()]
            count = len(items)
            self.finished_signal.emit(True, count, output)
        except Exception as e:
            self.finished_signal.emit(False, 0, str(e))


class DownloadThread(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url, save_path, force=False, limit=None, parent=None):
        super().__init__(parent)
        self.url = url
        self.save_path = save_path
        self.force = force
        self.limit = limit

    def run(self):
        try:
            cmd = ["gallery-dl", "--ignore-config"]
            if self.force:
                cmd.append("--force-overwrites")
            if self.limit:
                cmd.extend(["--range", f"1-{self.limit}"])
            cmd.extend(["-d", self.save_path, self.url])
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            for line in iter(process.stdout.readline, ""):
                line = line.strip()
                if line:
                    self.progress_signal.emit(line)
            process.wait()
            if process.returncode == 0:
                self.finished_signal.emit(True, "Download completed successfully!")
            else:
                error_output = process.stderr.read()
                self.finished_signal.emit(False, f"Error: {error_output}")
        except Exception as e:
            self.finished_signal.emit(False, f"Error: {e}")


class PinterestDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pinterest Downloader v1.0.0")
        self.setWindowIcon(QIcon("resources/logo.png"))
        self.setMinimumSize(600, 500)
        self.save_folder = ""

        # Create Menu Bar and Status Bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        help_menu = self.menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.initUI()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Toggle Switch Layout (placed at top right)
        toggle_layout = QHBoxLayout()
        toggle_layout.addStretch()  # push toggle switch to the right
        self.theme_toggle = ToggleSwitch()
        self.theme_toggle.toggled.connect(self.toggle_theme)
        toggle_layout.addWidget(self.theme_toggle)
        main_layout.addLayout(toggle_layout)

        # Title Label
        self.title_label = QLabel("Pinterest Downloader")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        main_layout.addWidget(self.title_label)

        # Subtitle / Instruction
        self.instruction_label = QLabel(
            "Download Pinterest videos, images, and GIFs online"
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(self.instruction_label)

        # URL Input Field
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste your Pinterest link here...")
        self.url_input.setFont(QFont("Arial", 12))
        self.url_input.setFixedHeight(40)
        self.url_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #424242;
                color: #ffffff;
                border: 2px solid #616161;
                border-radius: 8px;
                padding: 0 8px;
            }
            QLineEdit:focus {
                border: 2px solid #90CAF9;
            }
        """
        )
        main_layout.addWidget(self.url_input)

        # Download Buttons Layout
        buttons_layout = QHBoxLayout()
        self.download_btn = QPushButton()
        self.download_btn.setFixedSize(220, 50)
        self.download_btn.setIcon(QIcon("resources/download.svg"))
        self.download_btn.setIconSize(QSize(40, 40))
        self.download_btn.setText("Download")
        self.download_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.download_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3; 
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
        )
        self.download_btn.clicked.connect(self.download_media)
        buttons_layout.addWidget(self.download_btn)
        self.force_download_btn = QPushButton()
        self.force_download_btn.setFixedSize(220, 50)
        self.force_download_btn.setIcon(QIcon("resources/download.svg"))
        self.force_download_btn.setIconSize(QSize(40, 40))
        self.force_download_btn.setText("Force Download")
        self.force_download_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.force_download_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #F44336; 
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 5px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """
        )
        self.force_download_btn.clicked.connect(self.force_download_media)
        buttons_layout.addWidget(self.force_download_btn)
        main_layout.addLayout(buttons_layout)

        # Save Folder Layout (compulsory)
        folder_layout = QHBoxLayout()
        self.save_folder_label = QLabel("Save to: [Not selected]")
        self.save_folder_label.setFont(QFont("Arial", 10))
        self.save_folder_label.setStyleSheet("color: #ffffff;")
        folder_layout.addWidget(self.save_folder_label)
        self.folder_btn = QPushButton()
        self.folder_btn.setIcon(QIcon("resources/folder.png"))
        self.folder_btn.setFixedSize(40, 40)
        self.folder_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #616161;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """
        )
        self.folder_btn.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_btn)
        main_layout.addLayout(folder_layout)

        # Loader (Animated GIF) for processing
        self.loader_label = QLabel()
        self.loader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie = QMovie("resources/loader.gif")
        self.loader_label.setMovie(self.movie)
        self.loader_label.hide()
        main_layout.addWidget(self.loader_label)

        # Status Message Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        main_layout.addWidget(self.status_label)

        # Apply default dark theme
        self.applyDarkTheme()

    def toggle_theme(self, state):
        # Toggle the theme based on the switch's state.
        if state:
            self.applyLightTheme()
        else:
            self.applyDarkTheme()

    def applyLightTheme(self):
        self.setStyleSheet(
            """
            QMainWindow { background-color: #d8dbe0; }
            QLabel { color: #28292c; }
            QMenuBar { background-color: #ffffff; color: #28292c; }
            QMenuBar::item { background-color: #ffffff; color: #28292c; }
            QMenuBar::item:selected { background-color: #d8dbe0; }
            QStatusBar { background-color: #ffffff; color: #28292c; }
            QLineEdit {
                background-color: #e0e0e0;
                color: #28292c;
                border: 2px solid #bdbdbd;
                border-radius: 8px;
                padding: 0 8px;
            }
            QLineEdit:focus {
                border: 2px solid #90CAF9;
            }
            QPushButton { color: #28292c; }
        """
        )

    def applyDarkTheme(self):
        self.setStyleSheet(
            """
            QMainWindow { background-color: #2E2E2E; }
            QLabel { color: #ffffff; }
            QMenuBar { background-color: #424242; color: #ffffff; }
            QMenuBar::item { background-color: #424242; color: #ffffff; }
            QMenuBar::item:selected { background-color: #616161; }
            QStatusBar { background-color: #424242; color: #ffffff; }
            QLineEdit {
                background-color: #424242;
                color: #ffffff;
                border: 2px solid #616161;
                border-radius: 8px;
                padding: 0 8px;
            }
            QLineEdit:focus {
                border: 2px solid #90CAF9;
            }
            QPushButton { color: #ffffff; }
        """
        )

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Save Folder", os.path.expanduser("~")
        )
        if folder:
            self.save_folder = folder
            self.save_folder_label.setText(f"Save to: {self.save_folder}")

    def download_media(self):
        self.prepare_download(force=False)

    def force_download_media(self):
        self.prepare_download(force=True)

    def prepare_download(self, force):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a valid Pinterest link.")
            return
        if not self.save_folder:
            QMessageBox.warning(self, "Warning", "Please choose a save folder first.")
            self.choose_folder()
            if not self.save_folder:
                return
        self.loader_label.show()
        self.movie.start()
        self.status_label.setText("Processing link, please wait...")
        self.status_bar.showMessage("Processing...")
        self.download_btn.setEnabled(False)
        self.force_download_btn.setEnabled(False)
        self.simulation_thread = SimulationThread(url, timeout=120)
        self.simulation_thread.finished_signal.connect(
            lambda success, count, output: self.simulation_finished(
                success, count, output, force
            )
        )
        self.simulation_thread.start()

    def simulation_finished(self, success, count, output, force):
        self.movie.stop()
        self.loader_label.hide()
        self.download_btn.setEnabled(True)
        self.force_download_btn.setEnabled(True)
        if not success:
            QMessageBox.warning(
                self, "Simulation Error", f"Simulation failed: {output}"
            )
            self.status_label.setText("Simulation error.")
            self.status_bar.showMessage("Simulation error.", 5000)
            return
        limit = None
        if count > 100:
            reply = QMessageBox.question(
                self,
                "Download Limit",
                f"This link contains {count} images.\nDo you want to download only the first 100 images?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                limit = 100
        self.start_download(self.url_input.text().strip(), force, limit)

    def start_download(self, url, force, limit):
        self.loader_label.show()
        self.movie.start()
        self.status_label.setText("Downloading, please wait...")
        self.status_bar.showMessage("Downloading...")
        self.download_thread = DownloadThread(
            url, self.save_folder, force=force, limit=limit
        )
        self.download_thread.progress_signal.connect(self.on_progress)
        self.download_thread.finished_signal.connect(self.on_finished)
        self.download_thread.start()

    def on_progress(self, msg):
        self.status_label.setText(msg)

    def on_finished(self, success, message):
        self.loader_label.hide()
        self.movie.stop()
        self.status_label.setText(message)
        if success:
            self.status_bar.showMessage("Download complete", 5000)
        else:
            self.status_bar.showMessage("Download failed", 5000)

    def show_about(self):
        QMessageBox.information(
            self,
            "About Pinterest Downloader",
            "Pinterest Downloader v1.0\n\n"
            "A professional GUI application built with PyQt6 and gallery-dl to download Pinterest images, videos, and GIFs.\n\n"
            "If the link contains more than 100 images, you will be given the option to download only the first 100 images only.",
        )


def main():
    app = QApplication(sys.argv)
    window = PinterestDownloader()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
