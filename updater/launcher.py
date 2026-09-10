import os
import subprocess


def find_entrypoint(root):
    candidates = []
    for current_root, _, files in os.walk(root):
        for filename in files:
            if filename.lower().endswith(".exe") and filename.lower().startswith("ai-teamtalk-bot"):
                candidates.append(os.path.join(current_root, filename))
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"Expected exactly one AI-TeamTalk-Bot executable, found {len(candidates)}."
        )
    return candidates[0]


def launch(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    return subprocess.Popen([path], cwd=os.path.dirname(path), close_fds=True)
