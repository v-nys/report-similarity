{
  description = "Poetry environment with libstdc++ on NixOS";

  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
    in {
      devShell.x86_64-linux = pkgs.mkShell {
        buildInputs = [
          pkgs.gcc
          pkgs.poetry
        ];

        shellHook = ''
          # Set LD_LIBRARY_PATH if it's undefined, then add libstdc++ path
          if [ -z "$LD_LIBRARY_PATH" ]; then
            export LD_LIBRARY_PATH="${pkgs.gcc.libc}/lib"
          else
            export LD_LIBRARY_PATH="${pkgs.gcc.libc}/lib:$LD_LIBRARY_PATH"
          fi
        '';
      };
    };
}
