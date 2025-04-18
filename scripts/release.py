#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

def get_github_token():
    """Get GitHub token from gh CLI."""
    result = subprocess.run("gh auth token", shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print("Error: Could not get GitHub token. Please run 'gh auth login' first.")
        sys.exit(1)
    return result.stdout.strip()

def run_command(command, cwd=None):
    """Run a command and return its output."""
    # If this is a git command that needs authentication, use the GitHub token
    if command.startswith('git') and ('push' in command or 'clone' in command):
        token = get_github_token()
        # Replace git@ with https://token@ and convert SSH URL format to HTTPS
        if 'git@github.com:' in command:
            command = command.replace('git@github.com:', f'https://{token}@github.com/')
        else:
            command = command.replace('https://', f'https://{token}@')
    
    result = subprocess.run(command, shell=True, text=True, capture_output=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def get_current_version():
    """Get the current version from setup.py."""
    setup_py = Path("setup.py").read_text()
    version_match = re.search(r'version="([^"]+)"', setup_py)
    if not version_match:
        print("Could not find version in setup.py")
        sys.exit(1)
    return version_match.group(1)

def update_version(current_version, bump_type):
    """Update version based on bump type (major, minor, patch)."""
    major, minor, patch = map(int, current_version.split('.'))
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    setup_py = Path("setup.py").read_text()
    new_setup_py = re.sub(
        r'version="[^"]+"',
        f'version="{new_version}"',
        setup_py
    )
    Path("setup.py").write_text(new_setup_py)
    return new_version

def get_package_hash(url):
    """Get SHA256 hash of a package from its URL."""
    download_cmd = f"curl -sL {url}"
    tarball = subprocess.run(download_cmd, shell=True, capture_output=True).stdout
    return hashlib.sha256(tarball).hexdigest()

def get_pypi_package_info(package_name):
    """Get the latest version and hash for a PyPI package."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = subprocess.run(f"curl -sL {url}", shell=True, capture_output=True).stdout
    data = json.loads(response)
    latest_version = data["info"]["version"]
    for url_info in data["urls"]:
        if url_info["packagetype"] == "sdist":
            return {
                "version": latest_version,
                "url": url_info["url"],
                "sha256": url_info["digests"]["sha256"]
            }
    return None

def update_homebrew_formula(version, release_hash):
    """Update the Homebrew formula with new version and hash."""
    tap_dir = Path.home() / "Documents/GitHub/homebrew-tap"
    if not tap_dir.exists():
        tap_dir = Path("../homebrew-tap")
        if not tap_dir.exists():
            run_command("git clone https://github.com/Trevogre/homebrew-tap.git ../homebrew-tap")
            tap_dir = Path("../homebrew-tap")

    formula_path = tap_dir / "Formula/disscli.rb"
    formula = formula_path.read_text()
    
    # Update main package version and hash
    formula = re.sub(
        r'url "https://github\.com/Trevogre/discordcli/archive/refs/tags/v[^"]+"',
        f'url "https://github.com/Trevogre/discordcli/archive/refs/tags/v{version}.tar.gz"',
        formula
    )
    formula = re.sub(
        r'(^  sha256 ")[^"]+"',
        f'\\1{release_hash}"',
        formula,
        flags=re.MULTILINE
    )
    
    # Update PyPI dependencies
    dependencies = ["certifi", "charset-normalizer", "idna", "requests", "urllib3"]
    for dep in dependencies:
        pkg_info = get_pypi_package_info(dep)
        if pkg_info:
            # Find the resource block for this dependency
            resource_pattern = f'  resource "{dep}" do\n.*?  end'
            resource_block = re.search(resource_pattern, formula, re.DOTALL)
            if resource_block:
                old_block = resource_block.group(0)
                # Create new block with updated URL and hash
                new_block = f'''  resource "{dep}" do
    url "{pkg_info["url"]}"
    sha256 "{pkg_info["sha256"]}"
  end'''
                formula = formula.replace(old_block, new_block)
    
    formula_path.write_text(formula)
    return tap_dir

def create_github_release(version, bump_type):
    """Create a GitHub release for the version."""
    # Get the commits since the last tag
    last_tag = run_command("git describe --tags --abbrev=0 || echo ''")
    if last_tag:
        commits = run_command(f"git log {last_tag}..HEAD --pretty=format:'- %s'")
    else:
        commits = run_command("git log --pretty=format:'- %s'")

    # Create release notes
    notes = f"""Release version {version}

Changes in this release:
{commits}
"""

    # Create the release using GitHub CLI if available
    if subprocess.run("which gh", shell=True, capture_output=True).returncode == 0:
        release_cmd = f"""gh release create v{version} \
            --title "Version {version}" \
            --notes "{notes}" \
            --generate-notes"""
        run_command(release_cmd)
    else:
        print(f"""
Note: GitHub CLI (gh) not found. To create the release manually:
1. Go to https://github.com/Trevogre/discordcli/releases
2. Click 'Draft a new release'
3. Choose the tag v{version}
4. Add these release notes:

{notes}
""")

def main():
    parser = argparse.ArgumentParser(description="Release a new version of discordcli")
    parser.add_argument('bump_type', choices=['major', 'minor', 'patch'],
                      help='The type of version bump to perform')
    args = parser.parse_args()

    # Ensure we're in the root directory
    if not Path("setup.py").exists():
        print("Please run this script from the root directory of the project")
        sys.exit(1)

    # Ensure working directory is clean
    if run_command("git status --porcelain"):
        print("Working directory is not clean. Please commit or stash changes first.")
        sys.exit(1)

    # Get current version and bump it
    current_version = get_current_version()
    new_version = update_version(current_version, args.bump_type)
    print(f"Bumping version from {current_version} to {new_version}")

    # Commit version bump
    run_command(f'git add setup.py')
    run_command(f'git commit -m "chore: bump version to {new_version}"')

    # Create and push tag
    run_command(f'git tag -a v{new_version} -m "Release version {new_version}"')
    run_command('git push origin main --tags')

    print("Waiting for GitHub to process the release...")
    run_command('sleep 5')  # Give GitHub a moment to process the tag

    # Create GitHub release
    create_github_release(new_version, args.bump_type)

    # Get release hash and update Homebrew formula
    release_hash = get_package_hash(f"https://github.com/Trevogre/discordcli/archive/refs/tags/v{new_version}.tar.gz")
    tap_dir = update_homebrew_formula(new_version, release_hash)

    # Commit and push Homebrew changes
    run_command(f'git add Formula/disscli.rb', cwd=tap_dir)
    run_command(f'git commit -m "feat: update disscli to version {new_version}"', cwd=tap_dir)
    run_command('git push origin main', cwd=tap_dir)

    print(f"""
Release {new_version} completed successfully!
The release has been created on GitHub and the Homebrew formula has been updated.
""")

if __name__ == "__main__":
    main() 