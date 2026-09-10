"""Best-effort local startup sound playback.

This sound is played once when the main application controller starts. It is
intentionally independent from TeamTalk bot audio and never blocks startup.
"""
import os
import subprocess
import sys


def play_program_started_sound():
    """Play sounds/program_started.wav locally, without blocking startup."""
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sounds",
        "program_started.wav",
    )
    if not os.path.exists(path):
        return

    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(
                path,
                winsound.SND_FILENAME | winsound.SND_ASYNC,
            )
        elif sys.platform == "darwin":
            subprocess.Popen(
                ["afplay", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen(
                ["aplay", "-q", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        # Audio feedback must never prevent the application from starting.
        pass
