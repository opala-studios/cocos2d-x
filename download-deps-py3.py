#!/usr/bin/env python3
"""Download Cocos2d-x dependencies - Python 3 version"""

import os
import sys
import zipfile
import shutil
import json
from urllib.request import urlopen
from pathlib import Path

def download_file(url, filename, file_size):
    """Download file with progress bar"""
    print(f"==> Downloading {filename}...")
    print(f"    From: {url}")

    try:
        response = urlopen(url)
        total_size = file_size
        downloaded = 0
        chunk_size = 8192

        with open(filename, 'wb') as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                # Progress
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r    Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='')

        print("\n==> Download complete!")
        return True
    except Exception as e:
        print(f"\n==> Download failed: {e}")
        return False

def extract_zip(filename, extract_to):
    """Extract zip file"""
    print(f"==> Extracting {filename}...")

    with zipfile.ZipFile(filename, 'r') as z:
        z.extractall(extract_to)

    print("==> Extraction complete!")

def main():
    # Read config
    script_dir = Path(__file__).parent
    config_path = script_dir / "external" / "config.json"

    with open(config_path, 'r') as f:
        config = json.load(f)

    version = config["version"]
    repo_name = config["repo_name"]
    repo_parent = config["repo_parent"]
    zip_file_size = int(config["zip_file_size"])

    filename = version + '.zip'
    url = repo_parent + repo_name + '/archive/' + filename

    # Download
    os.chdir(script_dir)

    if os.path.isfile(filename):
        print(f"==> {filename} already exists, skipping download")
    else:
        if not download_file(url, filename, zip_file_size):
            sys.exit(1)

    # Extract
    # The zip contains a folder like 'cocos2d-x-3rd-party-libs-bin-3-deps-opalib-5/'
    # (version without 'v' prefix)
    extracted_folder = repo_name + '-' + version[1:]  # Remove 'v' prefix

    if os.path.exists(extracted_folder):
        print(f"==> Removing old {extracted_folder}")
        shutil.rmtree(extracted_folder)

    extract_zip(filename, '.')

    # Move contents
    external_dir = script_dir / "external"

    # Copy contents from extracted folder to external/
    src = Path(extracted_folder)

    print(f"==> Copying files to external/")

    for item in src.iterdir():
        dest = external_dir / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()

        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Handle move_dirs if specified
    if "move_dirs" in config:
        for src_dir, dst_dir in config["move_dirs"].items():
            src_path = external_dir / src_dir
            dst_path = script_dir / dst_dir / src_dir

            if src_path.exists():
                print(f"==> Moving {src_dir} to {dst_dir}/")
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.move(str(src_path), str(dst_path))

    # Cleanup
    print(f"==> Cleaning up...")
    shutil.rmtree(extracted_folder)

    # Ask about keeping zip
    response = input(f"==> Would you like to delete '{filename}'? [y/N]: ").strip().lower()
    if response in ['y', 'yes']:
        os.remove(filename)
        print(f"==> Deleted {filename}")
    else:
        print(f"==> Kept {filename}")

    print("==> Done!")

if __name__ == "__main__":
    main()
