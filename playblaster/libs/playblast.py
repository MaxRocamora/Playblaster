import os
import re

import maya.cmds as cmds  # type: ignore
import maya.mel as mel  # type: ignore
from backpack.folder_utils import create_folder, remove_files_in_dir
from qt_log.stream_log import get_stream_logger

from playblaster.libs.audio import export_audio
from playblaster.libs.makemov import make_mp4
from playblaster.libs.utils import get_camera_lens, restore_colors, set_green_bg

log = get_stream_logger("Playblaster")


def playblast(
    vp_green: bool, vp_motion_blur: bool, vp_aliasing: bool, vp_hud: bool, ffmpeg_path: str = None
):
    """Executes maya playblast command."""

    # range & size
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)
    width = cmds.getAttr("defaultResolution.width")
    height = cmds.getAttr("defaultResolution.height")

    # viewport aa
    aa_stored = cmds.getAttr("hardwareRenderingGlobals.multiSampleEnable")
    if vp_aliasing:
        cmds.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.aasc", 16)

    # viewport motion blur
    if vp_motion_blur:
        cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.motionBlurByFrame", 1)
        cmds.setAttr("hardwareRenderingGlobals.motionBlurShutter", 0.5)

    # output path
    filename = get_filename()
    if not filename:
        log.error("Filename is empty, cannot playblast.")
        return

    path = export_path(filename)
    pb_filepath = os.path.join(path, filename)

    # store interface bg original colors
    bg_color = cmds.displayRGBColor("background", query=True)
    top_color = cmds.displayRGBColor("backgroundTop", query=True)
    bot_color = cmds.displayRGBColor("backgroundBottom", query=True)

    # vfx green vg
    if vp_green:
        set_green_bg()

    # hud
    if vp_hud:
        _configure_hud(filename)

    # maya command for playblast
    try:
        cmds.playblast(
            st=start_frame,
            et=end_frame,
            format="image",
            compression="png",
            filename=pb_filepath,
            forceOverwrite=True,
            viewer=True,
            quality=100,
            os=True,
            fp=4,
            percent=100,
            clearCache=1,
            widthHeight=[width, height],
            combineSound=True,
        )
    except RuntimeError as e:
        log.error(str(e))
    finally:
        restore_colors(top_color, bg_color, bot_color)

    # cleanup
    cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", aa_stored)
    if vp_motion_blur:
        cmds.setAttr("hardwareRenderingGlobals.motionBlurEnable", 0)
        cmds.setAttr("hardwareRenderingGlobals.motionBlurByFrame", 0)
        cmds.setAttr("hardwareRenderingGlobals.motionBlurShutter", 0)
    if vp_hud and cmds.headsUpDisplay("HUDPreviewInfo", exists=True):
        cmds.headsUpDisplay("HUDPreviewInfo", rem=True)

    # export audio separately if it exists
    audio_filepath = export_audio()

    # make mov
    fps = cmds.playbackOptions(q=True, fps=True)
    make_mp4(
        path,
        os.path.join(path, f"{filename}.mp4"),
        audio_filepath,
        fps=_format_fps_for_ffmpeg(fps),
        first_frame=str(int(start_frame)),
        ffmpeg_path=ffmpeg_path,
    )


def _configure_hud(filename: str):
    hud_print = f"{filename} - {get_camera_lens()}"
    mel.eval("setCurrentFrameVisibility 1;")
    cmds.headsUpDisplay(layoutVisibility=True)
    cmds.headsUpDisplay(rp=(5, 0))
    cmds.headsUpDisplay("HUDPreviewInfo", rem=True)
    cmds.headsUpDisplay(
        "HUDPreviewInfo",
        s=5,
        b=0,
        ba="center",
        dw=50,
        label=hud_print,
        labelFontSize="large",
        blockSize="large",
    )


def get_filename() -> str:
    """Builds filename from context."""
    filename = cmds.file(q=True, sn=True, shn=True).rsplit(".", 1)[0]
    # replace a dot version number with an underscore to avoid ffmpeg issues
    if not filename:
        filename = "untitled"
    filename = re.sub(r"\.(\d+)$", r"_\1", filename)
    return filename


def export_path(filename: str) -> str:
    """Creates playblast export path, remove its files, and returns it."""

    export_path = os.path.join(cmds.workspace(query=True, rootDirectory=True), "playblast")
    playblast_path = os.path.join(export_path, filename)

    create_folder(playblast_path)
    remove_files_in_dir(playblast_path)

    return playblast_path


def maya_fps_to_number(fps_value) -> float:
    """Convert Maya FPS values to a positive int/float.

    Maya can return frame rates as numeric values, strings like "24fps",
    or named units like "film" and "ntsc".
    """
    named_units = {
        "game": 15,
        "film": 24,
        "pal": 25,
        "ntsc": 30,
        "show": 48,
        "palf": 50,
        "ntscf": 60,
    }

    if fps_value is None:
        return 24

    if isinstance(fps_value, (int, float)):
        if fps_value <= 0:
            return 24
        return int(fps_value) if float(fps_value).is_integer() else float(fps_value)

    fps_str = str(fps_value).strip().lower()
    if fps_str in named_units:
        return named_units[fps_str]

    fps_str = fps_str.replace("fps", "").strip()
    match = re.search(r"[-+]?\d*\.?\d+", fps_str)
    if not match:
        return 24

    parsed = float(match.group(0))
    if parsed <= 0:
        return 24

    return int(parsed) if parsed.is_integer() else parsed


def _format_fps_for_ffmpeg(fps_value: float) -> str:
    """Format a validated FPS value for ffmpeg arguments."""
    fps_number = maya_fps_to_number(fps_value)
    if isinstance(fps_number, int):
        return str(fps_number)
    return f"{fps_number:g}"
