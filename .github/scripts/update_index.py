import os
import sys
import json
import hashlib
import re
import urllib.request
from pathlib import Path
from ruamel.yaml import YAML

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RECIPES_DIR = Path("recipes")

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

def github_api_request(url):
    req = urllib.request.Request(url)
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("User-Agent", "Conan-Auto-Updater")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"API Error {url}: {e}")
        return None

def extract_version_from_tag(tag_name, auto_config):
    tag_pattern = auto_config.get("tag_regex")
    version_extract = auto_config.get("version_regex")

    if tag_pattern and not re.match(tag_pattern, tag_name):
        return None

    if version_extract:
        match = re.search(version_extract, tag_name)
        if match:
            return match.group(1) if match.groups() else match.group(0)
        return None

    return tag_name

def get_latest_upstream(auto_config):
    repo = auto_config["repo"]
    fmt = auto_config.get("format", "url_sha256")

    if auto_config["type"] == "github_tags":
        data = github_api_request(f"https://api.github.com/repos/{repo}/tags")
        if not data: return None, {}

        # First tag from response will be recent update (I hope)
        for t in data:
            tag_name = t["name"]
            version = extract_version_from_tag(tag_name, auto_config)
            if version:
                if fmt == "tag_only":
                    return version, { "tag": tag_name }
                else:
                    url = f"https://github.com/{repo}/archive/refs/tags/{tag_name}.tar.gz"
                    return version, { "url": url, "download_url": url }

    elif auto_config["type"] == "github_commits":
        branch = auto_config.get("branch", "main")
        data = github_api_request(f"https://api.github.com/repos/{repo}/commits/{branch}")
        if not data: return None, {}
        sha = data["sha"]
        if fmt == "commit_only":
            date_str = data["commit"]["committer"]["date"].split("T")[0].replace("-", "")
            return f"cci.{date_str}", {"commit": sha}

    elif auto_config["type"] == "github_releases":
        data = github_api_request(f"https://api.github.com/repos/{repo}/releases")
        if not data: return None, {}
        
        for release in data:
            if release.get("draft") or release.get("prerelease"):
                continue
                
            tag_name = release["tag_name"]
            version = extract_version_from_tag(tag_name, auto_config)
            if not version:
                continue
                
            asset_keyword = auto_config.get("asset_keyword", "android-binaries")
            asset_extension = auto_config.get("asset_extension", ".tar.gz")
            
            download_url = None
            for asset in release.get("assets", []):
                name = asset["name"]
                if asset_keyword in name and name.endswith(asset_extension):
                    download_url = asset["browser_download_url"]
                    break
                    
            if download_url:
                return version, {"url": download_url, "download_url": download_url}
            
    return None, {}

def calculate_sha256(url):
    print(f"Скачивание ассета для расчёта хэша: {url}")
    sha256 = hashlib.sha256()
    try:
        with urllib.request.urlopen(url) as response:
            while chunk := response.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return None

def update_recipe(recipe_path, version, source_data):
    config_path = recipe_path / "config.yml"
    conandata_path = recipe_path / "all" / "conandata.yml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.load(f)

    if "versions" in config and version in config["versions"]:
        return False

    if "versions" not in config or config["versions"] is None:
        from ruamel.yaml.comments import CommentedMap
        config["versions"] = CommentedMap()

    config["versions"].insert(0, version, { "folder": "all" })

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f)

    with open(conandata_path, "r", encoding="utf-8") as f:
        conandata = yaml.load(f)

    if "sources" not in conandata or conandata["sources"] is None:
        from ruamel.yaml.comments import CommentedMap
        conandata["sources"] = CommentedMap()

    conandata["sources"].insert(0, version, source_data)

    if "patches" in conandata and conandata["patches"]:
        existing_versions = [v for v in conandata["patches"].keys() if v != version]
        if existing_versions:
            latest_old_version = existing_versions[0]
            conandata["patches"].insert(0, version, conandata["patches"][latest_old_version])
            print(f" Наследован патч от версии {latest_old_version} для {version} (добавлен в начало)")
    with open(conandata_path, "w", encoding="utf-8") as f:
        yaml.dump(conandata, f)

    return True

def main():
    updated_packages = []
    if not RECIPES_DIR.exists():
        sys.exit(0)

    for recipe_path in RECIPES_DIR.iterdir():
        if not recipe_path.is_dir(): continue
        auto_file = recipe_path / "automation.yml"
        if not auto_file.exists(): continue

        print(f"Upstream check: {recipe_path.name}")
        with open(auto_file, "r") as f:
            auto_config = yaml.load(f)

        version, source_data = get_latest_upstream(auto_config)
        if not version:
            print("   No updates found.")
            continue

        config_path = recipe_path / "config.yml"
        if config_path.exists():
            with open(config_path, "r") as f:
                cfg = yaml.load(f)
                if version in cfg.get("versions", {}):
                    print(f"   Version {version} already added.")
                    continue

        if "download_url" in source_data:
            dl_url = source_data.pop("download_url")
            sha = calculate_sha256(dl_url)
            if not sha: continue
            source_data["sha256"] = sha

        if update_recipe(recipe_path, version, source_data):
            has_patches = False
            conandata_path = recipe_path / "all" / "conandata.yml"
            if conandata_path.exists():
                with open(conandata_path, "r") as f:
                    data = yaml.load(f)
                    has_patches = "patches" in data and version in data["patches"]

            updated_packages.append(f"{recipe_path.name}:{version}:{'HAS_PATCHES' if has_patches else 'NO_PATCHES'}")

    if updated_packages:
        env_file = os.getenv("GITHUB_ENV")
        if env_file:
            with open(env_file, "a") as f:
                f.write(f"UPDATED_PACKAGES={','.join(updated_packages)}\n")
        print(f"🔥 Обновлено пакетов: {len(updated_packages)}")
    else:
        print("✅ Всё в актуальном состоянии.")

if __name__ == "__main__":
    main()