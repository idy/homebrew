cask "tailsplit" do
  arch arm: "arm64", intel: "amd64"

  version "0.9.6"
  sha256 arm:   "efd48f56f1cf9f6ab6e369e2879e4bea6497381e306f63c4ba3939ce971be6a1",
         intel: "9da284bacc326434c3a0574bd4f959dfd8906ef0f768df58db2ca8fd1522234d"

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
