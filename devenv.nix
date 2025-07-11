{ config, lib, pkgs, ... }:

{
  config = {
    packages = with pkgs; [
      just
    ];

    languages.python = {
      enable = true;
      version = "3.13";
      poetry = {
        enable = true;
        activate.enable = true;
      };
    };

    git-hooks.hooks = {
      nixpkgs-fmt.enable = true;
      ruff.enable = true;
      ruff-format.enable = true;
    };
  };
}
