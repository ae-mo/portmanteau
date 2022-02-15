{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
    buildInputs = [ pkgs.python3 pkgs.poetry pkgs.python38Packages.numpy pkgs.python38Packages.pandas-datareader ];
}