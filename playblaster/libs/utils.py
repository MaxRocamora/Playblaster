import os

import maya.api.OpenMaya as om  # type: ignore
import maya.api.OpenMayaUI as omui  # type: ignore
import maya.cmds as cmds  # type: ignore
from PySide6 import QtWidgets  # type: ignore
from qt_log.stream_log import get_stream_logger

log = get_stream_logger("Playblaster")


def get_maya_main_window():
    """Returns the main Maya window as a QtWidgets.QWidget."""
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return omui.wrapInstance(int(ptr), QtWidgets.QWidget)


def restore_colors(top: tuple, bg: tuple, bottom: tuple) -> None:
    """Sets green maya bg color or restores it."""
    cmds.displayRGBColor("background", *top)
    cmds.displayRGBColor("backgroundTop", *bg)
    cmds.displayRGBColor("backgroundBottom", *bottom)


def set_green_bg() -> None:
    """Sets green maya bg color or restores it."""
    cmds.displayRGBColor("background", 0, 1, 0)
    cmds.displayRGBColor("backgroundTop", 0, 1, 0)
    cmds.displayRGBColor("backgroundBottom", 0, 1, 0)


def get_camera_lens() -> str:
    """Reads camera values from current maya window."""

    focal_length = ""
    try:
        view = omui.M3dView.active3dView()
        camera_path = om.MDagPath()
        view.getCamera(camera_path)
        focal_length = om.MFnCamera(camera_path).focalLength
    except RuntimeError:
        log.warning("Unable to read maya current panel.")
        log.warning("Make sure a camera model panel is active first.")
    except ValueError:
        pass

    lens = f"FocalLength: {focal_length}.mm"
    log.info(lens)
    return lens


def version_from_file() -> str:
    """Returns version from current file."""
    workfile = cmds.file(sn=1, q=1)
    f, _ = os.path.splitext(os.path.split(workfile)[1])
    try:
        version = f.split(".")[1]
    except IndexError:
        log.warning("Unable to resolve version from file")
        return "0000"
    try:
        int(version)
        return version
    except ValueError:
        log.warning("Unable to resolve file version number %s", version)
        return "0000"
