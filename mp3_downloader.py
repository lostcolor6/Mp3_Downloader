import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFileDialog, QProgressBar, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
import yt_dlp


class YouTubeDownloader(QMainWindow):
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
        self.dir_label = QLabel("Download-Verzeichnis:")
        self.layout.addWidget(self.dir_label)
        self.dir_input = QLineEdit()
        self.layout.addWidget(self.dir_input)
        self.dir_button = QPushButton("Ordner wählen")
        self.dir_button.clicked.connect(self.select_output_dir)
        self.layout.addWidget(self.dir_button)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        
        # Buttons
        self.download_button = QPushButton("Download starten")
        self.download_button.clicked.connect(self.start_download)
        self.layout.addWidget(self.download_button)
        
        self.quit_button = QPushButton("Beenden")
        self.quit_button.clicked.connect(self.close)
        self.layout.addWidget(self.quit_button)
    
    def select_output_dir(self):
        """Öffnet einen Dialog, um das Download-Verzeichnis auszuwählen."""
        directory = QFileDialog.getExistingDirectory(self, "Download-Verzeichnis auswählen")
        if directory:
            self.dir_input.setText(directory)
    
    def start_download(self):
        """Startet den Download in einem separaten Thread."""
        url = self.url_input.text().strip()
        output_dir = self.dir_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Fehler", "Bitte eine YouTube-URL eingeben!")
            return
        if not output_dir:
            QMessageBox.warning(self, "Fehler", "Bitte ein Download-Verzeichnis angeben!")
            return
        
        self.download_thread = threading.Thread(target=self.download, args=(url, output_dir))
        self.download_thread.start()
    
    def download(self, url, output_dir):
        """Führt den Download durch."""
        self.update_progress(0)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
            ],
            'progress_hooks': [self.progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.update_progress(100)
            QMessageBox.information(self, "Erfolg", "Download abgeschlossen!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Download:\n{str(e)}")
            self.update_progress(0)
    
    def progress_hook(self, d):
        """Wird während des Downloads aufgerufen, um Fortschritt zu aktualisieren."""
        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            progress = int(downloaded / total * 100)
            self.update_progress(progress)
    
    def update_progress(self, value):
        """Aktualisiert die Fortschrittsanzeige."""
        self.progress_bar.setValue(value)


if __name__ == "__main__":
    app = QApplication([])
    window = YouTubeDownloader()
    window.show()
    app.exec_()
