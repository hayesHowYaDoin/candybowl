{ config, lib, pkgs, ... }:

{
  config = {
    packages = with pkgs; [
      just
      ruff # For git hooks and CLI on NixOS
      python313Packages.mypy # For git hooks and CLI on NixOS
      stdenv.cc.cc.lib # required by jupyter
      gcc-unwrapped # fix: libstdc++.so.6: cannot open shared object file
      libz # fix: for numpy/pandas import
    ];

    processes = {
      backend.exec = "cd backend && python -m apps.main";
      chatbot.exec = "cd chatbot && python -m apps.main";
      frontend.exec = "cd frontend && npm run dev -- --host 0.0.0.0";
    };

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
      mypy.enable = true;
    };

    # Ensure correct load path
    env.LD_LIBRARY_PATH = "${pkgs.gcc-unwrapped.lib}/lib64:${pkgs.libz}/lib";

    # Ensure Nix tools are available for git hooks by prepending to PATH
    env.PATH = "${pkgs.ruff}/bin:${pkgs.python313Packages.mypy}/bin:$PATH";
  };
}
