################
### PREAMBLE ###
################
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

###############
### GLOBALS ###
###############
filetypes = {
    "all": ["jpg", "jpeg", "bmp", "png", "webp", "svg", "gif"],
    "still": ["jpg", "jpeg", "bmp", "png", "webp", "svg"],
    "anim": ["gif"],
    "normal": ["jpg", "jpeg", "bmp", "png", "webp"],
}
source_folder: str
source_filelist: list[str] = []
source_count: int = 0
current_file: str = ""
current_count: int = 0
shortcuts = {  # key : (path, text)
    "Q": ("", "--None--"),
    "W": ("", "--None--"),
    "E": ("", "--None--"),
    "R": ("", "--None--"),
    "T": ("", "--None--"),
    "A": ("", "--None--"),
    "S": ("", "--None--"),
    "D": ("", "--None--"),
    "F": ("", "--None--"),
    "G": ("", "--None--"),
    "Z": ("", "--None--"),
    "X": ("", "--None--"),
    "C": ("", "--None--"),
    "V": ("", "--None--"),
    "B": ("", "--None--"),
}
shortcut_colors = [
    "QPushButton { background-color: thistle; }",
    "QPushButton { background-color: lightgreen; }",
    "QPushButton { background-color: lightblue; }",
]


##########################
### DEFINING FUNCTIONS ###
##########################
debug = True


def dprint(text: str):  # debug print
    if debug:
        print(text)


def update_source_filelist(_change_to_folder: str = ""):
    global source_folder, source_filelist, filetypes, source_count

    if _change_to_folder != "":
        source_folder = _change_to_folder
        os.chdir(source_folder)
    srcfiles: list[str] = os.listdir(source_folder)

    to_remove: list[int] = []
    for i in range(len(srcfiles)):
        itest = srcfiles[i].split(".")
        if itest[-1].lower() not in filetypes["all"] or len(itest) != 2:
            to_remove.append(i)
    to_remove.reverse()
    for i in to_remove:
        srcfiles.pop(i)
    source_filelist = srcfiles
    source_count = len(source_filelist)


########################
### DEFINING CLASSES ###
########################
class ImageDisplay(QLabel):
    empty: str = """Welcome!

    Currently, you either have no source folder selected or the source folder contains
    no files with recognized image formats.

    Choose a source folder (button in top-left) to start viewing image files.
    Use the left and right cursor keys to skip files.
    Choose target folders for each of the keyboard shortcuts (along the left).
    You can choose whether the shortcut is moving or copying the file.
    You can also delete files as you go (shortcut key Delete)"""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(self.empty)

    def loadImage(self):
        global current_count, current_file
        if current_count == 0 or current_file == "":
            self.setText(self.empty)
            return

        filetype = current_file.split(".")[-1].lower()
        if filetype in ["jpg", "jpeg", "bmp", "webp", "png", "svg"]:
            p = QPixmap(current_file)
            self.setPixmap(p)
        elif filetype == "gif":
            # for some reason, including a setText() here makes it change instantly to a gif
            self.setText("Loading GIF file")
            m = QMovie(current_file)
            m.start()
            self.setMovie(m)
        else:  # should never happen
            self.setText(self.empty)


class ShortcutButton(QPushButton):
    shortcut_key: str

    def __init__(self, _key: str):
        super().__init__()
        self.shortcut_key = _key
        _color = shortcut_colors[0]
        if _key in "ASDFG":
            _color = shortcut_colors[1]
        elif _key in "ZXCVB":
            _color = shortcut_colors[2]
        self.clicked.connect(self.shortcutKeyClicked)
        self.setText(self.shortcut_key)
        self.setStyleSheet(_color)
        self.setMinimumSize(50, 24)
        self.setMaximumSize(50, 24)

    def shortcutKeyClicked(self):
        if debug:
            print("Shortcut clicked: " + self.shortcut_key)


class ChangeTargetButton(QPushButton):
    shortcut_key: str
    clear = False

    def __init__(self, _key: str):
        super().__init__()
        if _key.startswith("Clear_"):
            self.clear = True
            _key = _key[-1]
        self.shortcut_key = _key
        _color = shortcut_colors[0]
        if _key in "ASDFG":
            _color = shortcut_colors[1]
        elif _key in "ZXCVB":
            _color = shortcut_colors[2]
        if self.clear:
            self.setText("X")
            self.setMinimumSize(24, 24)
            self.setMaximumSize(24, 24)
        else:
            self.setText("--No target selected--")
            self.setMinimumSize(200, 24)
            self.setMaximumSize(200, 24)
        self.setStyleSheet(_color)
        self.clicked.connect(self.changeButtonClicked)

    def changeButtonClicked(self):
        if debug:
            text = "Changed clicked: " + self.shortcut_key
            if self.clear:
                text += ", CLEAR"
            print(text)


class FilenameLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Current filename: --no file loaded--")

    def setFilename(self, _text: str):
        if _text == "":
            self.setText("Current filename: --no file loaded--")
        else:
            self.setText(f"Current filename: {_text}")


class FileCounter(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("File - / -")
        self.setStyleSheet("QLabel {color: white }")

    # do not call this function directly
    def _updateCounter(
        self,
        _counter_reset: bool = False,
        _counter_change: int = 0,
    ):
        global current_count, source_filelist, source_count

        if source_count == 0:
            current_count = 0
            self.setText("File - / -")
            return

        if _counter_reset:
            current_count = 1

        current_count += _counter_change

        if current_count > source_count:
            current_count = 1

        if current_count == 0:
            current_count = source_count

        self.setText(f"File {current_count} / {source_count}")

    def nextPressed(self):
        global source_count
        if source_count == 0:
            return
        self._updateCounter(False, 1)

    def prevPressed(self):
        global source_count
        if source_count == 0:
            return
        self._updateCounter(False, -1)

    def delPressed(self):
        global source_count
        if source_count == 0:
            return
        self._updateCounter(False, 0)

    def sourceChanged(self):
        global source_count
        if source_count == 0:
            return
        self._updateCounter(True, 0)


###################
### MAIN LAYOUT ###
###################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Sorter")
        self.setStyleSheet(
            """QMainWindow {background-color: #303030 }
            QPushButton {color: black; background-color: gray }
            QLabel {color:white }"""
        )

        global current_count, source_count

        lay_vcore = QVBoxLayout()
        lay_htop = QHBoxLayout()
        lay_hbtm = QHBoxLayout()
        lay_vleft = QVBoxLayout()
        lay_vright = QVBoxLayout()

        ### TOP ROW (source folder, file counter, other controls)
        # source button
        source_btn = QPushButton("Change Source")
        source_btn.setObjectName("Source Button")
        if debug:
            source_btn.setToolTip("Source Button")
        source_btn.clicked.connect(self.selectSourceFolder)
        source_btn.setMinimumSize(300, 24)

        # File Counter
        file_counter = FileCounter()
        file_counter.setObjectName("File Counter")
        if debug:
            file_counter.setToolTip("File Counter")
        file_counter.setStyleSheet("QLabel {color: white }")
        file_counter.setMinimumSize(100, 24)
        file_counter.setMaximumSize(100, 24)
        file_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # buttons
        prev_btn = QPushButton("<<")
        prev_btn.setObjectName("Previous")
        prev_btn.setToolTip("Previous")
        prev_btn.setMinimumSize(100, 24)
        prev_btn.setMaximumSize(100, 24)
        prev_btn.clicked.connect(self.prevClicked)

        next_btn = QPushButton(">>")
        next_btn.setObjectName("Next")
        next_btn.setToolTip("Next")
        next_btn.setMinimumSize(100, 24)
        next_btn.setMaximumSize(100, 24)
        next_btn.clicked.connect(self.nextClicked)

        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("Delete")
        if debug:
            delete_btn.setToolTip("Delete")
        delete_btn.setMinimumSize(100, 24)
        delete_btn.setMaximumSize(100, 24)
        delete_btn.clicked.connect(self.delClicked)
        # shortcut mode
        shortcut_mode = QComboBox()
        shortcut_mode.setObjectName("Shortcut Mode")
        if debug:
            shortcut_mode.setToolTip("Shortcut Mode")
        shortcut_mode.setMinimumSize(100, 24)
        shortcut_mode.setMaximumSize(100, 24)
        shortcut_mode.addItems(["Move", "Copy"])

        lay_htop.addWidget(source_btn)
        lay_htop.addWidget(prev_btn)
        lay_htop.addWidget(file_counter)
        lay_htop.addWidget(next_btn)
        lay_htop.addWidget(shortcut_mode)
        lay_htop.addWidget(delete_btn)

        lay_vcore.addLayout(lay_htop)

        ### LEFT COLUMN (shortcut keys)

        for i in shortcuts.keys():
            lay_vleft.addLayout(self.addShortcutRow(i))
        lay_vleft.setAlignment(Qt.AlignmentFlag.AlignTop)
        lay_hbtm.addLayout(lay_vleft)

        ### RIGHT SIDE (image display)

        image = ImageDisplay()
        image.setObjectName("Image")
        qsp = QSizePolicy()
        qsp.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        qsp.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        image.setSizePolicy(qsp)
        if debug:
            image.setToolTip("Image")
        filename_label = FilenameLabel()
        filename_label.setObjectName("Filename")
        if debug:
            filename_label.setToolTip("Filename")
        filename_label.setStyleSheet("QLabel {color: white }")
        lay_vright.addWidget(image, alignment=Qt.AlignmentFlag.AlignCenter)
        lay_vright.addWidget(filename_label, alignment=Qt.AlignmentFlag.AlignBottom)
        lay_hbtm.addLayout(lay_vright)
        lay_vcore.addLayout(lay_hbtm)

        ### FINAL ASSEMBLY
        widget = QWidget()
        widget.setLayout(lay_vcore)
        self.setCentralWidget(widget)

    def addShortcutRow(self, shortcut_key: str):
        row = QHBoxLayout()
        short_btn = ShortcutButton(shortcut_key)
        short_btn.setObjectName("Shortcut " + shortcut_key)
        if debug:
            short_btn.setToolTip("Shortcut " + shortcut_key)
        change_btn = ChangeTargetButton(shortcut_key)
        change_btn.setObjectName("Change Target " + shortcut_key)
        if debug:
            change_btn.setToolTip("Change Target " + shortcut_key)
        clear_btn = ChangeTargetButton("Clear_" + shortcut_key)
        clear_btn.setObjectName("Clear Target " + shortcut_key)
        if debug:
            change_btn.setToolTip("Clear Target " + shortcut_key)
        row.addWidget(short_btn)
        row.addWidget(change_btn)
        row.addWidget(clear_btn)
        return row

    def selectSourceFolder(self):
        global source_filelist, source_folder, current_count, current_file

        response = QFileDialog.getExistingDirectory(
            self, "Select Source Folder", os.getcwd()
        )
        source_folder = response
        update_source_filelist()
        if len(source_filelist) > 0:
            current_count = 1
            current_file = source_filelist[current_count - 1]
        else:
            current_count = 0
            current_file = ""

        self.findChild(
            QPushButton, "Source Button", Qt.FindChildOption.FindChildrenRecursively
        ).setText(f"Source Folder: {source_folder.split('/')[-1]}")
        self.findChild(
            FileCounter, "File Counter", Qt.FindChildOption.FindChildrenRecursively
        ).sourceChanged()
        self.findChild(
            ImageDisplay, "Image", Qt.FindChildOption.FindChildrenRecursively
        ).loadImage()

    def selectTargetFolder(self, shortcut_key: str):
        global shortcuts

        response = QFileDialog.getExistingDirectory(
            self, "Select Target Folder", os.getcwd()
        )
        target_text: str = ""

        self.findChild(
            QPushButton, "Target Button", Qt.FindChildOption.FindChildrenRecursively
        ).setText(target_text)
        self.findChild(
            ImageDisplay, "Image", Qt.FindChildOption.FindChildrenRecursively
        ).loadImage()

    def nextClicked(self):
        global current_file, source_filelist, current_count
        if len(source_filelist) <= 0:
            return
        self.findChild(
            FileCounter, "File Counter", Qt.FindChildOption.FindChildrenRecursively
        ).nextPressed()
        current_file = source_filelist[current_count - 1]
        self.findChild(
            ImageDisplay, "Image", Qt.FindChildOption.FindChildrenRecursively
        ).loadImage()

    def prevClicked(self):
        global current_file, source_filelist, current_count
        if len(source_filelist) <= 0:
            return
        self.findChild(
            FileCounter, "File Counter", Qt.FindChildOption.FindChildrenRecursively
        ).prevPressed()
        current_file = source_filelist[current_count - 1]
        self.findChild(
            ImageDisplay, "Image", Qt.FindChildOption.FindChildrenRecursively
        ).loadImage()

    def delClicked(self):
        global current_file, source_filelist, current_count
        if current_count <= 0:
            return
        os.remove(source_filelist[current_count - 1])
        self.findChild(
            FileCounter, "File Counter", Qt.FindChildOption.FindChildrenRecursively
        ).delPressed()
        self.findChild(
            ImageDisplay, "Image", Qt.FindChildOption.FindChildrenRecursively
        ).loadImage()


#################
### EXECUTION ###
#################
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
