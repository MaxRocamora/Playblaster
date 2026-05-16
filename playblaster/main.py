# ----------------------------------------------------------------------------------------
# PLAYBLASTER - A simple Maya playblast tool with FFMpeg integration for easy video conversion.
# ----------------------------------------------------------------------------------------
import os

import maya.cmds as cmds  # type: ignore
from backpack.folder_utils import browse_folder
from PySide6 import QtCore
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QCheckBox, QFileDialog, QMainWindow
from pyside_ui_backpack import Colors, css, style_push_button
from qt_log.qt_ui_logger import QtUILogger
from qt_log.stream_log import get_stream_logger

from playblaster.libs.playblast import playblast
from playblaster.libs.utils import get_maya_main_window
from playblaster.setup_ui import build_main_window
from playblaster.version import __qt__, app_name, version

log = get_stream_logger("Playblaster")
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons", "playblaster.png")


class Playblaster(QMainWindow):
    def __init__(self, parent=get_maya_main_window()):  # noqa: D107
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setObjectName(__qt__)
        self.ui_window = build_main_window()
        self.setFixedSize(self.ui_window.maximumWidth(), self.ui_window.maximumHeight())
        self.setCentralWidget(self.ui_window.centralWidget())
        self.move(parent.geometry().center() - self.ui_window.geometry().center())
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setWindowTitle(app_name)
        css.load_css(self)
        self.loggers = QtUILogger(self, self.ui_window.log_layout, [log])
        self.settings = QSettings("Playblaster", "Playblaster")
        self._ffmpeg_path = None
        self.set_connections()
        self.set_menu()
        self.show()
        self.reset_ui()

    def set_connections(self):
        """Connects ui signals to functions."""
        self.ui_window.btn_publish.clicked.connect(self.do_playblast)
        style_push_button(self, button=self.ui_window.btn_publish, color=Colors.BG_BLUE, shadow=1)
        self.ui_window.btn_browse.clicked.connect(lambda: browse_folder(self.export_path()))

    def set_menu(self):
        """Sets menu."""
        menu = self.menuBar().addMenu("Configuration")
        menu.addAction("FFMpegPath", self.pick_ffmpeg_path)

        # add option widgets checkboxes for playblast settings to options_lyt
        self._chk_green = QCheckBox("Green Background")
        self._chk_green.setToolTip("Set viewport background to green for easier keying in post.")
        self._chk_aa = QCheckBox("Viewport Anti-Aliasing")
        self._chk_aa.setToolTip("Enabling anti-aliasing may increase playblast time.")
        self._chk_mblur = QCheckBox("Motion Blur")
        self._chk_mblur.setToolTip("Enable motion blur in the playblast.")
        self._chk_hud = QCheckBox("HUD Info")
        self._chk_hud.setToolTip(
            "Show frame, camera, and scene info in the viewport HUD during playblast."
        )
        self._use_ffmpeg = QCheckBox("Use FFMpeg to convert to mp4")
        self._use_ffmpeg.setToolTip("Use FFMpeg to convert the playblast to mp4 format.")

        self._chk_aa.setChecked(True)
        self._use_ffmpeg.setChecked(True)
        self.ui_window.options_lyt.addWidget(self._chk_green)
        self.ui_window.options_lyt.addWidget(self._chk_aa)
        self.ui_window.options_lyt.addWidget(self._chk_mblur)
        self.ui_window.options_lyt.addWidget(self._chk_hud)
        self.ui_window.options_lyt.addWidget(self._use_ffmpeg)

    def reset_ui(self):
        """Starts ui & tool."""
        log.ok(f"{app_name} {version}")
        QApplication.processEvents()

        self._ffmpeg_path = self.settings.value("FFMpegPath", None)
        if not self._ffmpeg_path:
            log.info("FFMpeg path not set, please set it in the menu.")

        log.info(self.export_path())

        self.ui_window.lbl_fps.setText(f"FPS: {cmds.currentUnit(query=True, time=True)}")

    def do_playblast(self):
        """Playblast button."""

        if self._use_ffmpeg.isChecked() and not self._ffmpeg_path:
            log.warning("FFMpeg path not set, please set it in the menu.")
            return

        log.process("Generating Playblast")
        QApplication.processEvents()

        playblast(
            vp_green=self._chk_green.isChecked(),
            vp_motion_blur=self._chk_mblur.isChecked(),
            vp_aliasing=self._chk_aa.isChecked(),
            vp_hud=self._chk_hud.isChecked(),
            ffmpeg_path=self._ffmpeg_path if self._use_ffmpeg.isChecked() else None,
        )

        log.done("Playblast Completed.")

    def export_path(self):
        """Returns local maya path + playblast."""
        return os.path.join(cmds.workspace(query=True, rootDirectory=True), "playblast")

    def pick_ffmpeg_path(self):
        """Opens a folder browser qt dialog and saves the selected path to settings."""
        qt_dialgo_window = QFileDialog(self)
        qt_dialgo_window.setFileMode(QFileDialog.Directory)
        if qt_dialgo_window.exec_():
            path = qt_dialgo_window.selectedFiles()[0]
            self.settings.setValue("FFMpegPath", path)
            self._ffmpeg_path = path + "/ffmpeg.exe"
            log.info(f"FFMpeg path set to {self._ffmpeg_path}")

    def closeEvent(self, _):
        """Call close on stdTool."""
        self.loggers.close()
        self.close()


def load():
    """Load Playblaster UI."""
    if cmds.window(__qt__, q=1, ex=1):
        cmds.deleteUI(__qt__)
    Playblaster()
