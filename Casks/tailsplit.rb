cask "tailsplit" do
  arch arm: "arm64", intel: "amd64"

  version "0.9.8"
  sha256 arm:   "d5f87aaed6ec92b43a040d7d40f2cc1e5650755742dff07e0bdf1bec42d7b77e",
         intel: "b63cb59cf628a93866e491687c7f59505fa872a15936112887f36ac586c8970b"

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
