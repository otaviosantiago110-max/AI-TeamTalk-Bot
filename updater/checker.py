import logging
import re

import requests

from version import GITHUB_OWNER, GITHUB_REPOSITORY

API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/releases/latest"
API_VERSION = "2026-03-10"


class ReleaseInfo:
    def __init__(self, tag, name, asset_name, asset_url, asset_size, digest):
        self.tag = tag
        self.name = name
        self.asset_name = asset_name
        self.asset_url = asset_url
        self.asset_size = asset_size
        self.digest = digest


def parse_version(tag):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?", str(tag).strip())
    if not match:
        return None
    parts = [int(value) for value in match.groups(default="0")]
    return tuple(parts)


def is_newer_version(remote_tag, current_tag):
    remote = parse_version(remote_tag)
    current = parse_version(current_tag)
    return remote is not None and current is not None and remote > current


def fetch_latest_release(asset_name, current_tag, logger=None):
    logger = logger or logging.getLogger(__name__)
    response = requests.get(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "AI-TeamTalk-Bot-Updater",
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    tag = str(data.get("tag_name", "")).strip()

    if not is_newer_version(tag, current_tag):
        return None

    asset = next(
        (item for item in data.get("assets", []) if item.get("name") == asset_name),
        None,
    )
    if not asset:
        logger.warning("Release %s exists, but asset %s was not found.", tag, asset_name)
        return None

    return ReleaseInfo(
        tag=tag,
        name=str(data.get("name") or tag),
        asset_name=str(asset.get("name")),
        asset_url=str(asset.get("browser_download_url")),
        asset_size=int(asset.get("size") or 0),
        digest=str(asset.get("digest") or ""),
    )
