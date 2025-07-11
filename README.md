# Candy Bowl

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/hayesHowYaDoin/candybowl)]()

Have you ever wondered if AI could replace capitalism? Wonder no longer.

![logo not found!][logo]

All dependencies are managed through the [Poetry package manager][1], unit 
tests utilize the [pytest][4] framework, and the static analysis tools 
[ruff][2] and [mypy][3] installed by default.

### Prerequisites

The following instructions assume that [nix][5], [direnv][6], and [Git][7] are 
installed on the host computer.

### Setting Up The Development Environment

1) Clone the repository onto the host computer with the following command:
   ```
   git clone https://github.com/hayesHowYaDoin/candybowl.git
   ```
2) Navigate into the repository and un-block .envrc:
   ```
   direnv allow
   ```

And... that's it!

## Commands

Most useful commands have been added to the justfile in the root of this 
project. This allows for a clean, unified method of executing commands across 
multiple utilities.

These commands are as follows:
```
just default .......... Lists all available commands
just install .......... Installs the python package and all dependencies
just analyze .......... Runs linter and static type checking
just test ............. Runs all unit tests
just pre-commit ....... Runs pre-commit hooks on all files
just run .............. Runs the application
```

[1]: https://python-poetry.org/
[2]: https://docs.astral.sh/ruff/
[3]: https://mypy-lang.org/
[4]: https://docs.pytest.org/en/7.4.x/
[5]: https://nixos.org/
[6]: https://direnv.net/
[7]: https://git-scm.com/
[logo]: https://github.com/hayesHowYaDoin/candybowl/raw/main/assets/bowl.png "You took too much too fast. The candy spills onto the floor."
