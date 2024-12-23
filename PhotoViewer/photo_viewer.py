import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSpacerItem, QSizePolicy, QDialog, QScrollArea, QGridLayout
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt
from PIL import Image

class PhotoViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NurOS - Просмотр Фото")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2E3436;")
        self.current_index = -1
        self.image_files = []
        self.scale_factor = 1.0  # Начальный масштаб изображения

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout(self.centralWidget)

        self.photoPanel = QWidget(self)
        self.photoPanel.setStyleSheet("background-color: #1C1C1C;")

        self.photoLayout = QHBoxLayout(self.photoPanel)
        self.photoLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self.photoPanel)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #FFFFFF;")
        self.label.setScaledContents(True)
        self.photoLayout.addWidget(self.label)

        self.mainLayout.addStretch()

        self.prevButton = QPushButton('<', self)
        self.prevButton.clicked.connect(self.showPrevImage)
        self.prevButton.setStyleSheet("background-color: #1C1C1C; color: #FFFFFF;")

        self.nextButton = QPushButton('>', self)
        self.nextButton.clicked.connect(self.showNextImage)
        self.nextButton.setStyleSheet("background-color: #1C1C1C; color: #FFFFFF;")

        self.zoomInButton = QPushButton('Zoom In', self)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomInButton.setStyleSheet("background-color: #1C1C1C; color: #FFFFFF;")

        self.zoomOutButton = QPushButton('Zoom Out', self)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.zoomOutButton.setStyleSheet("background-color: #1C1C1C; color: #FFFFFF;")

        self.fullScreenButton = QPushButton('Fullscreen', self)
        self.fullScreenButton.clicked.connect(self.showFullScreenImage)
        self.fullScreenButton.setStyleSheet("background-color: #1C1C1C; color: #FFFFFF;")

        self.photoPanelContainer = QHBoxLayout()
        self.photoPanelContainer.addWidget(self.createButtonWithSpacer(self.prevButton), 0, Qt.AlignVCenter)
        self.photoPanelContainer.addWidget(self.photoPanel, 1, Qt.AlignCenter)
        self.photoPanelContainer.addWidget(self.createButtonWithSpacer(self.nextButton), 0, Qt.AlignVCenter)
        self.mainLayout.addLayout(self.photoPanelContainer)

        self.mainLayout.addStretch()

        self.zoomLayout = QHBoxLayout()
        self.zoomLayout.addWidget(self.zoomInButton)
        self.zoomLayout.addWidget(self.zoomOutButton)
        self.mainLayout.addLayout(self.zoomLayout)

        self.fullScreenLayout = QHBoxLayout()
        self.fullScreenLayout.addStretch()
        self.fullScreenLayout.addWidget(self.fullScreenButton, 0, Qt.AlignRight | Qt.AlignBottom)
        self.mainLayout.addLayout(self.fullScreenLayout)

        self.thumbnailLayout = QHBoxLayout()
        self.thumbnailScrollArea = QScrollArea(self)
        self.thumbnailScrollArea.setWidgetResizable(True)
        self.thumbnailContainer = QWidget()
        self.thumbnailGrid = QGridLayout(self.thumbnailContainer)
        self.thumbnailScrollArea.setWidget(self.thumbnailContainer)
        self.thumbnailLayout.addWidget(self.thumbnailScrollArea)
        self.mainLayout.addLayout(self.thumbnailLayout)

        self.infoLabel = QLabel(self)
        self.infoLabel.setStyleSheet("color: #FFFFFF;")
        self.mainLayout.addWidget(self.infoLabel, 0, Qt.AlignCenter)

        self.createMenu()

    def createButtonWithSpacer(self, button):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(button, 0, Qt.AlignCenter)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        return container

    def createMenu(self):
        menubar = self.menuBar()
        menubar.clear()

        fileMenu = menubar.addMenu("Файл")
        openAction = QAction("Открыть", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.openImage)
        fileMenu.addAction(openAction)

        appMenu = menubar.addMenu("Программа")
        quitAction = QAction("Выход", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.close)
        appMenu.addAction(quitAction)

    def openImage(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", "Все файлы (*);;Изображения (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if fileName:
            directory = os.path.dirname(fileName)
            self.image_files = [os.path.abspath(os.path.join(directory, f)) for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            fileName = os.path.abspath(fileName)
            self.current_index = self.image_files.index(fileName)
            self.showImage(fileName)
            self.updateThumbnails()

    def showImage(self, fileName):
        self.pixmap = QPixmap(fileName)
        self.scale_factor = min(1.0, 512 / max(self.pixmap.width(), self.pixmap.height()))
        self.label.setPixmap(self.pixmap.scaled(self.pixmap.size() * self.scale_factor, Qt.KeepAspectRatio))
        self.updateImageInfo(fileName, self.pixmap)

    def zoomIn(self):
        self.scale_factor = min(self.scale_factor * 1.2, 512 / max(self.pixmap.width(), self.pixmap.height()))
        self.label.setPixmap(self.pixmap.scaled(self.pixmap.size() * self.scale_factor, Qt.KeepAspectRatio))

    def zoomOut(self):
        self.scale_factor /= 1.2
        self.label.setPixmap(self.pixmap.scaled(self.pixmap.size() * self.scale_factor, Qt.KeepAspectRatio))

    def showFullScreenImage(self):
        dialog = FullScreenDialog(self.pixmap, self)
        dialog.exec()

    def updateThumbnails(self):
        for i in reversed(range(self.thumbnailGrid.count())):
            widget = self.thumbnailGrid.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        for index, fileName in enumerate(self.image_files):
            thumbnail = QPixmap(fileName).scaled(64, 64, Qt.KeepAspectRatio)
            thumbLabel = QLabel()
            thumbLabel.setPixmap(thumbnail)
            thumbLabel.mousePressEvent = lambda event, idx=index: self.thumbnailClicked(idx)
            self.thumbnailGrid.addWidget(thumbLabel, 0, index)

    def thumbnailClicked(self, index):
        self.clearOldImage()
        self.current_index = index
        self.showImage(self.image_files[self.current_index])

    def clearOldImage(self):
        self.label.clear()

    def updateImageInfo(self, fileName, pixmap):
        imageSize = pixmap.size()
        fileWidth = imageSize.width()
        fileHeight = imageSize.height()
        aspectRatio = fileWidth / fileHeight

        img = Image.open(fileName)
        bitDepth = img.mode
        fileSize = os.path.getsize(fileName)
        fileModifiedTime = datetime.fromtimestamp(os.path.getmtime(fileName)).strftime('%Y-%m-%d %H:%M:%S')
        dpi = img.info.get('dpi', (72, 72))  # По умолчанию 72 dpi если информация недоступна

        infoText = f"Размер изображения: {fileWidth}x{fileHeight} пикселей\n"
        infoText += f"Соотношение сторон: {aspectRatio:.2f}\n"
        infoText += f"Битность изображения: {bitDepth}\n"
        infoText += f"Последняя дата изменения: {fileModifiedTime}\n"
        infoText += f"Размер файла: {fileSize} байт\n"
        infoText += f"Количество точек на дюйм: {dpi[0]}"

        self.infoLabel.setText(infoText)

    def showPrevImage(self):
        self.clearOldImage()
        if self.current_index > 0:
            self.current_index -= 1
            self.showImage(self.image_files[self.current_index])

    def showNextImage(self):
        self.clearOldImage()
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.showImage(self.image_files[self.current_index])

class FullScreenDialog(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.setWindowState(Qt.WindowFullScreen)

        layout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio))
        layout.addWidget(self.label)

    def mousePressEvent(self, event):
        self.close()

def main():
    global app
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#2E3436"))
    palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Base, QColor("#2E3436"))
    palette.setColor(QPalette.AlternateBase, QColor("#2E3436"))
    palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Text, QColor("#FFFFFF"))
    palette.setColor(QPalette.Button, QColor("#2E3436"))
    palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Highlight, QColor("#729FCF"))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)

    viewer = PhotoViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
