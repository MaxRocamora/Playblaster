import os

import maya.cmds as cmds  # type: ignore
from maya import OpenMayaUI  # type: ignore
from PySide6 import QtWidgets  # type: ignore
from qt_log.stream_log import get_stream_logger
from shiboken6 import wrapInstance

log = get_stream_logger("Playblaster")


def get_maya_main_window():
    """Returns wrapped maya main window for qt app's."""
    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


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
        panel = cmds.getPanel(withFocus=True)
        if not panel or cmds.getPanel(typeOf=panel) != "modelPanel":
            visible_panels = cmds.getPanel(visiblePanels=True) or []
            model_panels = [p for p in visible_panels if cmds.getPanel(typeOf=p) == "modelPanel"]
            panel = model_panels[0] if model_panels else None

        if not panel:
            raise RuntimeError

        camera = cmds.modelEditor(panel, query=True, camera=True)
        if not camera:
            raise RuntimeError

        if cmds.nodeType(camera) == "camera":
            camera_shape = camera
        else:
            camera_shapes = cmds.listRelatives(camera, shapes=True, noIntermediate=True) or []
            camera_shape = next(
                (shape for shape in camera_shapes if cmds.nodeType(shape) == "camera"), None
            )

        if not camera_shape:
            raise RuntimeError

        focal_length = cmds.getAttr(f"{camera_shape}.focalLength")
    except RuntimeError:
        log.warning("Unable to read maya current panel.")
        log.warning("Make sure a camera model panel is active first.")
    except (TypeError, ValueError):
        pass

    # round focal length to 2 decimals
    if isinstance(focal_length, (int, float)):
        focal_length = round(focal_length, 2)

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
