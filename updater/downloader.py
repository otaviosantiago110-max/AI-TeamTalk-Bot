import hashlib
import os
import tempfile

import requests


class DownloadError(Exception):
    pass


def download_release(release, progress_callback=None):
    temp_dir = tempfile.mkdtemp(prefix="ai_teamtalk_update_")
    destination = os.path.join(temp_dir, release.asset_name)
    hasher = hashlib.sha256()
    downloaded = 0

    try:
        with requests.get(
            release.asset_url,
            headers={
                "Accept": "application/octet-stream",
                "User-Agent": "AI-TeamTalk-Bot-Updater",
            },
            stream=True,
            timeout=(15, 60),
        ) as response:
            response.raise_for_status()
            with open(destination, "wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    output.write(chunk)
                    hasher.update(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, release.asset_size)

        if release.digest:
            expected = release.digest.split(":", 1)[-1].lower()
            if hasher.hexdigest().lower() != expected:
                raise DownloadError("SHA-256 digest does not match the GitHub release asset.")

        return destination
    except Exception:
        try:
            os.remove(destination)
        except OSError:
            pass
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass
        raise
