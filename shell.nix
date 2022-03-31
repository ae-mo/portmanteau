{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    buildInputs = [ pkgs.python3 pkgs.poetry pkgs.python39Packages.numpy pkgs.python39Packages.pandas-datareader ];
}