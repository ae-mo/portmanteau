{
  description = "Flake for portmanteau - portfolio manager to end all uncertainties";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    mach-nix = {
      url = github:DavHau/mach-nix/7266eda5065f509e76cdde66c5ec3f297c56a946; # conda beta
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };
  outputs = { self, nixpkgs, mach-nix, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = (import nixpkgs { inherit system; config.allowUnsupportedSystem = true; }).pkgs;
        mach-nix-utils = import mach-nix {
          inherit pkgs;
          python = "python3";
        };
        requirements = ''
            pyportfolioopt
            pytest
          '';
        providers = {
            scs = "nixpkgs";
        };
      in rec
      {

        devShell = mach-nix-utils.mkPythonShell {
          inherit requirements;
        };

        packages.portmanteau = mach-nix-utils.mkPython {
          inherit requirements;
        };

        defaultPackage = packages.portmanteau;

      }
  );
}
