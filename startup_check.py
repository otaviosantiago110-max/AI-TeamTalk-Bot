"""Runs before anything else starts: checks the Python version and that the
required third-party libraries are installed. If either check fails, prints
a clear error and plays sounds/critical.wav on the LOCAL machine (the bot
hasn't connected to any TeamTalk server yet at this point, so this can't be
played in-channel) before exiting.

Minimum supported version: Python 3.12. Anything below that (3.11 and
older) is not supported and will refuse to start.
"""
import os
import sys

MIN_PYTHON = (3, 12)
REQUIRED_MODULES = ["groq", "requests", "flask", "flask_sqlalchemy", "sqlalchemy", "dotenv"]


def _sounds_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


def _play_critical_sound_locally():
    """Best-effort local playback of critical.wav. Never raises — a failure
    to play the sound must not mask the real error being reported."""
    path = os.path.join(_sounds_dir(), "critical.wav")
    if not os.path.exists(path):
        return
    try:
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME)
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["afplay", path], check=False)
        else:
            import subprocess
            subprocess.run(["aplay", path], check=False)
    except Exception:
        pass  # Sound is a nice-to-have here; never let it block the real error.


def run_startup_check():
    """Call this as the very first thing in every entry point (main.py,
    main_gui.py, web_ui.py). Exits the process with a clear message if the
    environment doesn't meet the minimum requirements."""
    errors = []

    if sys.version_info[:2] < MIN_PYTHON:
        errors.append(
            f"Versão do Python incompatível: você está usando {sys.version_info.major}.{sys.version_info.minor}, "
            f"mas a versão mínima suportada é {MIN_PYTHON[0]}.{MIN_PYTHON[1]}. "
            f"Versões 3.11 ou anteriores não são suportadas e podem causar erros e conflitos."
        )

    missing = []
    for module_name in REQUIRED_MODULES:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)
    if missing:
        errors.append(
            "Dependência(s) faltando: " + ", ".join(missing) +
            ". Rode: pip install -r requirements.txt"
        )

    if errors:
        print("=" * 70)
        print("[Bot] Erro crítico de compatibilidade — o bot não pode iniciar:")
        for e in errors:
            print(f"  - {e}")
        print("=" * 70)
        _play_critical_sound_locally()
        sys.exit(1)
