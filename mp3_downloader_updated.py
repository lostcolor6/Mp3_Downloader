import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFileDialog, QProgressBar, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import yt_dlp


class YouTubeDownloader(QMainWindow):
    download_finished = pyqtSignal(str)  # Signal to indicate download completion
    progress_updated = pyqtSignal(int)   # Signal to update progress bar safely

    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube MP3 Downloader")
        self.setGeometry(100, 100, 500, 300)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # URL Input
        self.url_label = QLabel("YouTube-URL (Video/Playlist):")
        self.layout.addWidget(self.url_label)
        self.url_input = QLineEdit()
        self.layout.addWidget(self.url_input)
        
        # Output Directory
        self.dir_label = QLabel("Choose Download Directory:")
        self.layout.addWidget(self.dir_label)
        self.dir_input = QLineEdit()
        self.layout.addWidget(self.dir_input)
        self.dir_button = QPushButton("Choose Folder")
        self.dir_button.clicked.connect(self.select_output_dir)
        self.layout.addWidget(self.dir_button)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        
        # Buttons
        self.download_button = QPushButton("Start Download")
        self.download_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.download_button)
        
        self.quit_button = QPushButton("Close")
        self.quit_button.clicked.connect(self.close)
        self.layout.addWidget(self.quit_button)

        self.download_finished.connect(self.on_download_finished)
        self.progress_updated.connect(self.update_progress)

    def select_output_dir(self):
        """Opens Dialoge Window to choose directory"""
        directory = QFileDialog.getExistingDirectory(self, "choose Download-Directory")
        if directory:
            self.dir_input.setText(directory)
    
    def start_download(self):
        """Start download in separate Thread."""
        url = self.url_input.text().strip()
        output_dir = self.dir_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter valid YouTube-URL!")
            return
        if not output_dir:
            QMessageBox.warning(self, "Error", "Please choose a valid Download-Directory")
            return
        
        self.download_thread = threading.Thread(target=self.download, args=(url, output_dir))
        self.download_thread.start()

    def get_ffmpeg_location(self):
        """Use bundled ffmpeg if it exists, otherwise fall back to system PATH."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bundled_bin = os.path.join(
            base_dir,
            'ffmpeg',
            'ffmpeg-2025-01-27-git-959b799c8d-essentials_build',
            'bin'
        )
        return bundled_bin if os.path.isdir(bundled_bin) else None
    
    def download(self, url, output_dir):
        """Download logic happens here"""
        self.update_progress(0)
        ffmpeg_location = self.get_ffmpeg_location()
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
            ],
            'progress_hooks': [self.progress_hook],
            'ffmpeg_location': ffmpeg_location,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 3,
            'skip_unavailable_fragments': True,
            'http_headers': {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/123.0.0.0 Safari/537.36'
                )
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.download_finished.emit("Download finished!")  # Emit signal on success
        except Exception as e:
            error_text = str(e)
            if 'HTTP Error 403' in error_text or 'Forbidden' in error_text:
                error_text = (
                    "YouTube blocked this request (HTTP 403).\n\n"
                    "Please update yt-dlp to the newest version and try again:\n"
                    "pip install -U yt-dlp\n\n"
                    "If it still fails, try again later or test with a different video."
                )
            self.download_finished.emit(f"Error Downloading:\n{error_text}")  # Emit signal on error
    
    def progress_hook(self, d):
        """This gets called while downloading, representing progress of download"""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0)
            
            # Handle cases where total_bytes is None, 0, or unavailable
            if total and total > 0 and downloaded >= 0:
                progress = min(int((downloaded / total) * 100), 100)
                self.update_progress(progress)
            else:
                # If we can't calculate progress, show indeterminate progress
                # Just update to show something is happening
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
        elif d['status'] == 'finished':
            # Reset progress bar to normal range and set to 100%
            self.progress_bar.setRange(0, 100)
            self.update_progress(100)
    
    def update_progress(self, value):
        """Updates progress/status bar"""
        # Ensure value is within valid range (0-100)
        value = max(0, min(100, value))
        self.progress_bar.setValue(value)

    def on_download_finished(self, message):
        QMessageBox.information(self, "Status", message)
        self.update_progress(100 if "finished" in message else 0)


if __name__ == "__main__":
    app = QApplication([])
    window = YouTubeDownloader()
    window.show()
    app.exec_()
