import os

import maya.cmds as cmds  # type: ignore
from PySide6.QtWidgets import QApplication
from qt_log.stream_log import get_stream_logger

log = get_stream_logger("Playblaster")


def export_audio() -> str:
    """Exports audio from Maya."""
    try:
        audio_node = cmds.ls(type="audio")[0]
        log.info(f"Audio set to: {audio_node}")
        QApplication.processEvents()
    except IndexError:
        audio_node = ""
        log.info("Audio Node not found")
        QApplication.processEvents()

    if not audio_node:
        return

    audio_path = cmds.getAttr(f"{audio_node}.filename")
    if os.path.exists(audio_path):
        export_path = os.path.join(os.path.dirname(audio_path), "exported_audio.wav")
        try:
            cmds.file(audio_path, exportSelected=True, type="WAV", filename=export_path)
            log.info(f"Audio exported to: {export_path}")
        except RuntimeError as e:
            log.error(str(e))
    else:
        log.warning(f"Audio file does not exist: {audio_path}")

    return export_path
