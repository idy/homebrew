cask "nootify" do
  version "0.1.22"
  sha256 "c406e6004d9b1dde4fb965f7bf543922235cf2aaf1b6be2caa4798e367a49793"

  url "https://github.com/idy/nootify/releases/download/v#{version}/Nootify_#{version}_aarch64.dmg"
  name "Nootify"
  desc "Feishu message bridge for coding agents and pull request monitor"
  homepage "https://github.com/idy/nootify"

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :ventura

  app "Nootify.app"

  uninstall launchctl: "dev.idy.nootify.service",
            quit:      "dev.idy.nootify",
            delete:    "~/Library/LaunchAgents/dev.idy.nootify.service.plist"

  zap trash: [
    "~/.local/state/nootify",
    "~/Library/Caches/dev.idy.nootify",
    "~/Library/Preferences/dev.idy.nootify.plist",
    "~/Library/WebKit/dev.idy.nootify",
  ]

  caveats <<~EOS
    Nootify requires macOS 13.5 or later.
    Open Nootify from Applications once to install its per-user background service.
    This release is ad-hoc signed and not notarized. If macOS blocks the first
    launch, allow it in System Settings > Privacy & Security.
  EOS
end
