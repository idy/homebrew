cask "tailsplit" do
  arch arm: "arm64", intel: "amd64"

  version "0.9.5"
  sha256 arm:   "bf4acbddb445421355be44ecef6b8c4e932603f5b07a78eebb16b502c969c7d3",
         intel: "b60f43faa240abd37357508ea36dfe67db57c01b9eb3b22babed8e1aa41d082b"

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
