import glob
import os
import re
import subprocess

from qt_log.stream_log import get_stream_logger

log = get_stream_logger("Playblaster")


def _resolve_ffmpeg_executable(ffmpeg_path: str) -> str:
    """Resolve ffmpeg executable from a direct path or a directory path."""
    if not ffmpeg_path:
        return ""

    normalized = os.path.normpath(ffmpeg_path)
    if os.path.isdir(normalized):
        for candidate in ("ffmpeg.exe", "ffmpeg"):
            candidate_path = os.path.join(normalized, candidate)
            if os.path.isfile(candidate_path):
                return candidate_path
        return ""

    if os.path.isfile(normalized):
        return normalized

    return ""


def make_mp4(
    input_path: str,
    output_path: str,
    audio_path: str = None,
    fps: str = "24",
    first_frame: str = "0",
    ffmpeg_path: str = None,
) -> None:
    """Converts a sequence of PNG images to an MP4 video using FFmpeg.

    Args:
        input_path (str): The directory containing the PNG image sequence.
        output_path (str): The file path for the output MP4 video.
        audio_path (str, optional): The file path for the audio to be muxed into the video.
        fps (str, optional): The frame rate of the output video. Defaults to "24".
        first_frame (str, optional): The starting frame number of the image sequence. Defaults to "0".
        ffmpeg_path (str, optional): The file path to the FFmpeg executable. If not provided, it will be read from settings.

    Returns:
        None
    """
    ffmpeg_executable = _resolve_ffmpeg_executable(ffmpeg_path)
    if not ffmpeg_executable:
        log.error("Invalid FFMpeg path. Provide ffmpeg executable or its bin directory.")
        return

    if not input_path or not os.path.isdir(input_path):
        log.error("Input path does not exist: %s", input_path)
        return

    png_files = glob.glob(os.path.join(input_path, "*.png"))
    if not png_files:
        log.error("No PNG files found in input path: %s", input_path)
        return

    if not output_path:
        log.error("Output path is empty, cannot convert to mp4.")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            log.error("Could not create output directory %s: %s", output_dir, str(e))
            return

    if audio_path and not os.path.isfile(audio_path):
        log.warning("Audio file not found, exporting video without audio: %s", audio_path)
        audio_path = None

    try:
        first_frame_value = int(str(first_frame))
    except (TypeError, ValueError):
        log.warning("Invalid first_frame value '%s', using 0.", first_frame)
        first_frame_value = 0

    if first_frame_value < 0:
        log.warning("Negative first_frame value '%s', using 0.", first_frame)
        first_frame_value = 0

    try:
        fps_value = float(str(fps))
    except (TypeError, ValueError):
        log.warning("Invalid fps value '%s', using 24.", fps)
        fps_value = 24.0

    if fps_value <= 0:
        log.warning("Non-positive fps value '%s', using 24.", fps)
        fps_value = 24.0

    fps_string = str(int(fps_value)) if fps_value.is_integer() else f"{fps_value:g}"

    # detect printf-style image sequence pattern from actual files
    image_pattern, detected_first_frame = _build_image_sequence_pattern(input_path)
    if not image_pattern:
        log.error("Could not determine image sequence pattern in: %s", input_path)
        return

    command = generate_ffmpeg_command(
        image_pattern,
        output_path,
        audio_path=audio_path,
        fps=fps_string,
        first_frame=str(detected_first_frame),
        ffmpeg_path=ffmpeg_executable,
    )
    if not command:
        log.error("Could not generate ffmpeg command.")
        return

    run_windows_command(command)


def _build_image_sequence_pattern(input_path: str) -> tuple:
    """Detect printf-style image sequence pattern from PNG files in directory.

    Maya saves frames as ``basename.NNNN.png`` (4-digit padding when fp=4).
    ffmpeg requires a printf format such as ``basename.%04d.png``.

    Returns:
        (pattern_str, first_frame_int) or (None, None) on failure.
    """
    png_files = sorted(glob.glob(os.path.join(input_path, "*.png")))
    if not png_files:
        return None, None

    first = os.path.basename(png_files[0])
    match = re.match(r"^(.+)\.(\d+)\.png$", first, re.IGNORECASE)
    if not match:
        log.warning("Cannot detect image sequence pattern from filename: %s", first)
        return None, None

    base = match.group(1)
    frame_str = match.group(2)
    pad = len(frame_str)
    first_frame = int(frame_str)

    pattern = os.path.join(input_path, f"{base}.%0{pad}d.png").replace("\\", "/")
    return pattern, first_frame


def generate_ffmpeg_command(
    png_input: str,
    output: str,
    fps: str,
    first_frame: str,
    audio_path: str = None,
    ffmpeg_path: str = None,
) -> str:
    """Generates an FFmpeg command to convert an image sequence to an MP4 file.

    Args:
        png_input (str): The input file pattern for the image sequence.
        output (str): The output file path for the MP4 file.
        fps (str): The frame rate of the output video.
        first_frame (str): The starting frame number of the image sequence.
        audio_path (str, optional): The audio file path to mux into the output.

    Returns:
        str: The generated FFmpeg command string.
    """
    if not ffmpeg_path:
        log.error("FFMpeg path not set, cannot generate command.")
        return ""

    command_parts = [
        ffmpeg_path,
        "-y",
        "-framerate",
        str(fps),
        "-start_number",
        str(first_frame),
        "-i",
        png_input,
    ]

    if audio_path:
        command_parts.extend(
            [
                "-i",
                audio_path,
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
            ]
        )

    command_parts.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            output,
        ]
    )

    return subprocess.list2cmdline(command_parts)


def run_windows_command(command: str):
    """Run given command."""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    log.info("Running Command:")
    log.info(command)
    try:
        sp = subprocess.Popen(
            command,
            startupinfo=startupinfo,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = sp.communicate()
        sp.stdin.close()
        log.info(out.decode("utf-8"))
        log.info(err.decode("utf-8"))
    except OSError as e:
        log.error(str(e))
