# 03/2018 - v1
# 06/2018 - v2 (better code, revised folders, new external lib maya_playblast)
# 01/2019 - v2.1 Added format to playblast, fixed sound.
# 05/2019 - v2.1.2 Added pathObject, added viewport aa option
# 08/2019 - 2.3.0 moved to arcaneQt
# 08/2019 - 2.3.1 Check for new shot before making playblast
# 08/2019 - 2.3.2 After playblast, restore viewport AA status
# 02/2020 - 3.0.0 arcane2
# 11/2021 - 3.1.0 python3 ui
# 05/2022 - 3.2.0 python3 maya 2022
# 08/2022 - 3.3.0 refactored tool to only playblast png
# 09/2022 - 3.3.1 audio node fix
# 04/2024 - 3.3.2 renamed export file to have version as v.
# 04/2026 - 4.0.0 refactored to use PySide6, added ffmpeg conversion to mp4, added hud info option, added settings to save ffmpeg path, added tooltips, refactored UI to use a dynamic builder, refactored code to be more modular and easier to read. Updated version number to 4.0.0 since there are breaking changes and new features.

VERSION_MAJOR = 4
VERSION_MINOR = 0
VERSION_PATCH = 0

version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

app_name = "Playblaster"
__qt__ = "Arcane3:Qt_" + app_name + "_ui"
