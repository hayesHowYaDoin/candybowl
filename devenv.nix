{ config, lib, pkgs, ... }:

{
  config = {
    packages = with pkgs; [
      just
      stdenv.cc.cc.lib # required by jupyter
      gcc-unwrapped # fix: libstdc++.so.6: cannot open shared object file
      libz # fix: for numpy/pandas import
    ];

    dotenv.enable = true;

    languages.python = {
      enable = true;
      version = "3.13";
      poetry = {
        enable = true;
        activate.enable = true;
      };
    };

    languages.javascript = {
      enable = true;
      npm.enable = true;
    };

    git-hooks.hooks = {
      nixpkgs-fmt.enable = true;
      ruff.enable = true;
      ruff-format.enable = true;
    };

    # Ensure correct load path
    env.LD_LIBRARY_PATH = "${pkgs.gcc-unwrapped.lib}/lib64:${pkgs.libz}/lib";
  };
}
