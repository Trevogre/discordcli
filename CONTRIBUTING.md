# Contributing to discordcli

This guide explains how to make changes to discordcli and ensure they are properly released for both pip and Homebrew users.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/Trevogre/discordcli.git
cd discordcli
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Making Changes

1. Create a new branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and update tests as needed

3. Run tests to ensure everything works:
```bash
pytest
```

4. Commit your changes using conventional commit messages:
```bash
git commit -m "feat: add new feature"  # for new features
git commit -m "fix: resolve issue"     # for bug fixes
git commit -m "docs: update docs"      # for documentation
```

## Releasing a New Version

We have a fully automated release script that handles the entire release process. To release a new version:

1. Prerequisites:
   - Install GitHub CLI: `brew install gh`
   - Authenticate with GitHub: `gh auth login`
   - Ensure all changes are committed and pushed
   - Ensure your working directory is clean

2. Run the release script with the type of version bump you want (major, minor, or patch):
```bash
python scripts/release.py patch  # for a patch version bump (0.1.0 -> 0.1.1)
python scripts/release.py minor  # for a minor version bump (0.1.0 -> 0.2.0)
python scripts/release.py major  # for a major version bump (0.1.0 -> 1.0.0)
```

The script will automatically:
- Bump the version in setup.py
- Create and push a git tag
- Create a GitHub release with notes from commit messages
- Update the Homebrew formula with:
  - New version and hash for the main package
  - Latest versions and hashes for all PyPI dependencies
- Push changes to both repositories

No manual steps are required! The new version will be immediately available via Homebrew:
```bash
brew update
brew upgrade trevogre/tap/disscli
```

## Commit Message Guidelines

We use conventional commits to make the release process easier. Common types:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Getting Help

If you need help or have questions:
1. Open an issue on GitHub
2. Describe what you're trying to do
3. Include any relevant error messages or logs 