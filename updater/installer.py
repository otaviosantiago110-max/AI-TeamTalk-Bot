import os
import shutil
import sys
import tempfile
import zipfile

PRESERVED_FILES = (
    "config.ini",
    ".env",
    "site.db",
    "bot.log",
    "bot.log.1",
    "bot.log.2",
)


def validate_zip(zip_path):
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(zip_path)
    with zipfile.ZipFile(zip_path, "r") as archive:
        if archive.testzip() is not None:
            raise ValueError("The update ZIP is corrupted.")
        names = [name.replace("\\", "/") for name in archive.namelist()]
        if not names:
            raise ValueError("The update ZIP is empty.")
        if not any(name.lower().endswith(".spec") for name in names):
            raise ValueError("The update ZIP does not look like an AI-TeamTalk-Bot package.")


def extract_update(zip_path):
    validate_zip(zip_path)
    destination = tempfile.mkdtemp(prefix="ai_teamtalk_update_extract_")
    try:
        destination_path = os.path.abspath(destination)
        with zipfile.ZipFile(zip_path, "r") as archive:
            for member in archive.infolist():
                member_path = os.path.abspath(os.path.join(destination_path, member.filename))
                if os.path.commonpath((destination_path, member_path)) != destination_path:
                    raise ValueError("The update ZIP contains an unsafe path.")
            archive.extractall(destination)
        return destination
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def find_entrypoint(root):
    candidates = []
    for current_root, _, files in os.walk(root):
        for filename in files:
            lower = filename.lower()
            if lower.endswith(".exe") and lower.startswith("ai-teamtalk-bot"):
                candidates.append(os.path.join(current_root, filename))
    if len(candidates) != 1:
        raise ValueError(
            f"Expected exactly one AI-TeamTalk-Bot executable in the update package, found {len(candidates)}."
        )
    return candidates[0]


def _package_root(extracted_root):
    entrypoint = find_entrypoint(extracted_root)
    package_root = os.path.dirname(entrypoint)
    if os.path.basename(package_root).lower() == "dist":
        package_root = os.path.dirname(package_root)
    return package_root, entrypoint


def _write_update_script(script_path, app_dir, stage_dir, backup_dir, current_exe_name, staged_exe_name, pid):
    preserved = list(PRESERVED_FILES)
    lines = [
        "@echo off",
        "setlocal",
        f'set "APP_DIR={app_dir}"',
        f'set "STAGE_DIR={stage_dir}"',
        f'set "BACKUP_DIR={backup_dir}"',
        f'set "CURRENT_EXE={current_exe_name}"',
        f'set "STAGED_EXE={staged_exe_name}"',
        f'set "PID={pid}"',
        ":wait_for_app",
        'tasklist /FI "PID eq %PID%" /NH | find "%PID%" >nul',
        "if not errorlevel 1 (",
        "    timeout /t 1 /nobreak >nul",
        "    goto wait_for_app",
        ")",
        'if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"',
        'move /Y "%APP_DIR%" "%BACKUP_DIR%" >nul',
        'if errorlevel 1 goto install_failed',
        'move /Y "%STAGE_DIR%" "%APP_DIR%" >nul',
        'if errorlevel 1 goto restore_failed',
        f'if exist "%APP_DIR%\\{staged_exe_name}" if /I not "%STAGED_EXE%"=="%CURRENT_EXE%" ren "%APP_DIR%\\{staged_exe_name}" "%CURRENT_EXE%"',
    ]
    for filename in preserved:
        lines.extend([
            f'if exist "%BACKUP_DIR%\\{filename}" move /Y "%BACKUP_DIR%\\{filename}" "%APP_DIR%\\{filename}" >nul',
        ])
    lines.extend([
        'start "AI-TeamTalk-Bot" /D "%APP_DIR%" "%APP_DIR%\\%CURRENT_EXE%"',
        'rmdir /s /q "%BACKUP_DIR%"',
        'del "%~f0"',
        'exit /b 0',
        ":restore_failed",
        'rmdir /s /q "%APP_DIR%"',
        'move /Y "%BACKUP_DIR%" "%APP_DIR%" >nul',
        'exit /b 1',
        ":install_failed",
        'exit /b 1',
    ])
    with open(script_path, "w", encoding="utf-8", newline="\r\n") as script:
        script.write("\n".join(lines) + "\n")


def prepare_install(zip_path, current_executable=None):
    if not getattr(sys, "frozen", False):
        raise RuntimeError("Automatic installation is available only from a compiled application.")
    if not current_executable:
        current_executable = sys.executable
    current_executable = os.path.abspath(current_executable)
    app_dir = os.path.dirname(current_executable)
    current_exe_name = os.path.basename(current_executable)

    extracted_root = extract_update(zip_path)
    package_root, staged_executable = _package_root(extracted_root)
    staged_exe_name = os.path.basename(staged_executable)

    if os.path.abspath(package_root) == os.path.abspath(app_dir):
        raise ValueError("The update package cannot use the current application directory as its staging directory.")

    transaction_dir = tempfile.mkdtemp(prefix="ai_teamtalk_update_transaction_")
    stage_dir = os.path.join(transaction_dir, "package")
    backup_dir = os.path.join(os.path.dirname(app_dir), os.path.basename(app_dir) + ".update-backup")
    shutil.move(package_root, stage_dir)
    shutil.rmtree(extracted_root, ignore_errors=True)

    script_path = os.path.join(transaction_dir, "apply_update.cmd")
    _write_update_script(
        script_path,
        app_dir,
        stage_dir,
        backup_dir,
        current_exe_name,
        staged_exe_name,
        os.getpid(),
    )
    return {
        "script_path": script_path,
        "app_dir": app_dir,
        "backup_dir": backup_dir,
        "current_exe": current_executable,
        "current_exe_name": current_exe_name,
        "staged_exe_name": staged_exe_name,
        "transaction_dir": transaction_dir,
    }


def launch_installer(plan):
    if not os.path.isfile(plan["script_path"]):
        raise FileNotFoundError(plan["script_path"])
    import subprocess
    subprocess.Popen(
        ["cmd.exe", "/c", plan["script_path"]],
        cwd=plan["transaction_dir"],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        close_fds=True,
    )
