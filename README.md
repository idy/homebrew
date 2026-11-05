# idy Homebrew tap

Install idy's macOS applications from their official GitHub Releases using [Homebrew](https://brew.sh).

## Install

Add the tap once:

```bash
brew tap idy/homebrew https://github.com/idy/homebrew
```

On Homebrew 7+, trust the tap before loading its casks:

```bash
brew trust idy/homebrew
```

Install TailSplit:

```bash
brew install --cask idy/homebrew/tailsplit
```

Install Nootify:

```bash
brew install --cask idy/homebrew/nootify
```

The explicit repository URL is required on the first `brew tap`: this repository is named `idy/homebrew`, while Homebrew's default naming convention would look for `idy/homebrew-homebrew`. After tapping, the fully qualified cask names above work normally.

| Cask | Application | Supported Macs | Minimum macOS |
| --- | --- | --- | --- |
| `tailsplit` | [TailSplit](https://tailsplit.idy.dev): menu bar app for domain and IP routing through proxies and Tailscale | Apple Silicon and Intel | 14 (Sonoma) |
| `nootify` | [Nootify](https://github.com/idy/nootify): Feishu message bridge for coding agents and pull request monitor | Apple Silicon | 13.5 (Ventura) |

These casks install desktop applications in Homebrew's configured applications directory, normally `/Applications`. They do not install the standalone TailSplit CLI.

- **TailSplit:** open the app after installation. Its first connection requests administrator approval for the bundled network service. The macOS releases are signed and notarized.
- **Nootify:** open the app after installation to set up its per-user background service. It bundles Node.js; a separate runtime is not required. Current releases are ad-hoc signed and not notarized. If macOS blocks the first launch, allow it in **System Settings > Privacy & Security**.

## Upgrade

Both applications support in-app updates. To update them explicitly through Homebrew, quit the apps first, refresh the tap, and run:

```bash
brew update
```

```bash
brew upgrade --cask --greedy idy/homebrew/tailsplit idy/homebrew/nootify
```

Open the applications again afterward. A Homebrew upgrade can remove and reinstall their background services; TailSplit may request administrator approval again. `--greedy` includes casks marked as supporting automatic updates.

## Uninstall

```bash
brew uninstall --cask idy/homebrew/tailsplit
```

```bash
brew uninstall --cask idy/homebrew/nootify
```

Uninstalling unloads each application's background service and removes its registration. TailSplit's installed network-service package is removed when present. TailSplit configuration and saved device login, and Nootify's state and logs, are retained. Use `brew uninstall --cask --zap idy/homebrew/nootify` only if you also want to remove Nootify's state and logs.

After uninstalling all applications from this tap, you can remove the tap:

```bash
brew untap idy/homebrew
```

## Release maintenance

Casks pin release versions and per-architecture SHA-256 hashes. `brew livecheck` can discover new stable versions. The **Update casks** workflow also checks the official releases every six hours and can be started manually from GitHub Actions. Before publishing a cask update, it validates metadata, checks Homebrew style, audits the casks, and downloads every supported architecture to verify its checksum. Drafts, prereleases, incomplete releases, version downgrades, and changed checksums for an existing version are rejected. An unchanged version with replaced assets requires manual review.

To refresh the pinned versions locally, use Python 3.9+ and an authenticated [GitHub CLI](https://cli.github.com):

```bash
python3 scripts/update_casks.py
```

To check without changing files:

```bash
python3 scripts/update_casks.py --check
```

You can restrict either command to `tailsplit` or `nootify`. The check command exits with status 1 when an update is available or validation fails. The script requires GitHub's asset SHA-256 digests; it never substitutes an unchecked checksum.

Run the updater's safety tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

CI validates the casks and downloads the Apple Silicon packages plus TailSplit's Intel package. It does not launch the apps or install privileged services.

## Repository layout

- `Casks/`: application installation, update, and removal definitions.
- `scripts/update_casks.py`: stable-release validation and pinned-version updates.
- `tests/`: offline tests for release completeness, checksum safety, and update behavior.
- `.github/workflows/ci.yml`: Homebrew style, audit, and download checks.
- `.github/workflows/update-casks.yml`: scheduled, validated cask updates.

The tap definitions and scripts are MIT-licensed. Each application retains its own license.
