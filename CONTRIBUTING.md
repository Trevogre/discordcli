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

1. Update version number in `setup.py`

2. Create and push a new tag:
```bash
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin v0.1.1
```

3. Create a GitHub release:
   - Go to https://github.com/Trevogre/discordcli/releases
   - Click "Draft a new release"
   - Choose the tag you just created
   - Add release notes
   - Publish the release

4. Update the Homebrew tap:
   ```bash
   # Clone the tap repository if you haven't already
   git clone https://github.com/Trevogre/homebrew-tap.git
   cd homebrew-tap

   # Get the SHA256 hash of the new release
   curl -L https://github.com/Trevogre/discordcli/archive/refs/tags/v0.1.1.tar.gz | shasum -a 256

   # Update the formula version and hash in Formula/disscli.rb
   # Change both the url and sha256 lines to match the new version
   ```

5. Test the updated formula:
   ```bash
   brew uninstall disscli        # Remove old version
   brew install --build-from-source ./Formula/disscli.rb
   ```

6. If everything works, commit and push the tap changes:
   ```bash
   git add Formula/disscli.rb
   git commit -m "feat: update disscli to version 0.1.1"
   git push origin main
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