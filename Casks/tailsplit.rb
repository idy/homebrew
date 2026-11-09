cask "tailsplit" do
  arch arm: "arm64", intel: "amd64"

  version "0.8.0"
  sha256 arm:   "89d02a2be0425b537080f8a3e65bd370c13a7cd960d279390f37761512e2d187",
         intel: "bd54330368ecca3e1f1f4c09f42c7c72ef38b58d657d4a4ee39b3e8c328ae0be"

  url "https://github.com/idy/tailsplit/releases/download/v#{version}/TailSplit_#{version}_darwin_#{arch}.dmg"
  name "TailSplit"
  desc "Menu bar app for domain and IP routing through proxies and Tailscale"
  homepage "https://tailsplit.idy.dev/"

  livecheck do
    url :url
    strategy :github_latest
  end

  auto_updates true
  depends_on macos: :sonoma

  app "TailSplit.app"

  uninstall launchctl: "im.lbv.tailsplit.helper",
            quit:      "im.lbv.tailsplit",
            pkgutil:   "im.lbv.tailsplit.helper",
            delete:    "/var/run/im.lbv.tailsplit.sock"

  caveats <<~EOS
    Open TailSplit from Applications after installation. The first connection
    asks for administrator approval to install its bundled network service.
    Configuration and saved device login are retained when uninstalling.
  EOS
end
