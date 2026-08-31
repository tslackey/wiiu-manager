from __future__ import annotations

import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from wiiu_manager.catalog import Package
from wiiu_manager.paths import downloads_dir
from wiiu_manager.util import ManagerError, ensure_dir, eprint, sha256_file, which


GITHUB_API = "https://api.github.com"
USER_AGENT = "wiiu-manager (https://github.com/tslackey/wiiu-manager)"


def _headers() -> dict[str, str]:
    return {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}


def http_json(url: str) -> object:
    request = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ManagerError(f"HTTP {exc.code} fetching {url}") from exc
    except urllib.error.URLError as exc:
        raise ManagerError(f"Network error fetching {url}: {exc.reason}") from exc


def resolve_download_url(package: Package) -> tuple[str, str]:
    """Return (url, suggested_filename)."""
    if package.kind == "aroma-api":
        if not package.url:
            raise ManagerError(f"Package {package.id} is missing url")
        return package.url, package.filename
    if package.kind == "github-release":
        if not package.repo:
            raise ManagerError(f"Package {package.id} is missing repo")
        data = http_json(f"{GITHUB_API}/repos/{package.repo}/releases/latest")
        if not isinstance(data, dict):
            raise ManagerError(f"Unexpected GitHub response for {package.repo}")
        assets = data.get("assets") or []
        match = None
        for asset in assets:
            name = asset.get("name") or ""
            if package.asset_name and name == package.asset_name:
                match = asset
                break
            if package.asset_prefix and name.startswith(package.asset_prefix):
                if package.asset_suffix and not name.endswith(package.asset_suffix):
                    continue
                match = asset
                break
        if match is None:
            names = [a.get("name") for a in assets]
            raise ManagerError(
                f"No matching asset for {package.id} in {package.repo} latest release. Assets: {names}"
            )
        url = match.get("browser_download_url")
        if not url:
            raise ManagerError(f"Asset for {package.id} has no browser_download_url")
        return url, package.filename
    raise ManagerError(f"Unsupported package kind {package.kind!r} for {package.id}")


def download_file(url: str, dest: Path) -> Path:
    ensure_dir(dest.parent)
    curl = which("curl")
    if curl:
        args = [
            curl,
            "-fL",
            "--retry",
            "4",
            "--retry-delay",
            "2",
            "-A",
            USER_AGENT,
            "-o",
            str(dest),
            url,
        ]
        # Show a progress bar when attached to a terminal.
        if dest.exists():
            dest.unlink()
        from wiiu_manager.util import run

        try:
            run(args)
        except Exception as exc:  # noqa: BLE001 - curl already printed the error
            raise ManagerError(f"curl failed downloading {url}") from exc
        return dest

    request = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(request, timeout=120) as response, dest.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    except urllib.error.URLError as exc:
        raise ManagerError(f"Download failed for {url}: {exc}") from exc
    return dest


def fetch_package(package: Package, dest_dir: Path | None = None) -> dict[str, str]:
    dest_dir = dest_dir or downloads_dir()
    url, filename = resolve_download_url(package)
    dest = dest_dir / filename
    eprint(f"Downloading {package.id} -> {dest.name}")
    download_file(url, dest)
    if dest.stat().st_size < 64:
        raise ManagerError(f"Downloaded file {dest} is suspiciously small")
    info = {
        "id": package.id,
        "url": url,
        "path": str(dest),
        "bytes": str(dest.stat().st_size),
        "sha256": sha256_file(dest),
    }
    eprint(f"  {dest.name}  {info['bytes']} bytes  sha256={info['sha256']}")
    return info


def fetch_packages(packages: list[Package], dest_dir: Path | None = None) -> list[dict[str, str]]:
    dest_dir = dest_dir or downloads_dir()
    ensure_dir(dest_dir)
    results = []
    for package in packages:
        results.append(fetch_package(package, dest_dir))
    manifest_path = dest_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps({"packages": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    return results
