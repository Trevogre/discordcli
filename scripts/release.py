#!/usr/bin/env python3
import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return its output."""
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

def get_release_hash(version):
    """Get SHA256 hash of the release tarball."""
    url = f"https://github.com/Trevogre/discordcli/archive/refs/tags/v{version}.tar.gz"
    tarball = run_command(f"curl -L {url}")
    return hashlib.sha256(tarball.encode()).hexdigest()

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
    
    # Update version in URL
    formula = re.sub(
        r'url "https://github\.com/Trevogre/discordcli/archive/refs/tags/v[^"]+"',
        f'url "https://github.com/Trevogre/discordcli/archive/refs/tags/v{version}.tar.gz"',
        formula
    )
    
    # Update SHA256
    formula = re.sub(
        r'sha256 "[^"]+"',
        f'sha256 "{release_hash}"',
        formula
    )
    
    formula_path.write_text(formula)
    return tap_dir

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

    # Get release hash and update Homebrew formula
    release_hash = get_release_hash(new_version)
    tap_dir = update_homebrew_formula(new_version, release_hash)

    # Commit and push Homebrew changes
    run_command(f'git add Formula/disscli.rb', cwd=tap_dir)
    run_command(f'git commit -m "feat: update disscli to version {new_version}"', cwd=tap_dir)
    run_command('git push origin main', cwd=tap_dir)

    print(f"""
Release {new_version} completed successfully!
Next steps:
1. Go to https://github.com/Trevogre/discordcli/releases
2. Click 'Draft a new release'
3. Choose the tag v{new_version}
4. Add release notes
5. Publish the release
""")

if __name__ == "__main__":
    main() 