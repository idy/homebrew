cask "tailsplit" do
  arch arm: "arm64", intel: "amd64"

  version "0.7.8"
  sha256 arm:   "8cd0a460acc9fa3a6f32af17a7011870d37008518cd542399ed82f5ca76d4ee2",
         intel: "a2094d0d5e2a2a5074b7785794124d319fc3ec2ebd9dc541147f6c9e88d28dd3"

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
