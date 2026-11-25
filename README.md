# BhashaPy

A fresh Hinglish-flavored Python transpiler, interactive REPL, and CLI tool built with an all-new set of Hindi keywords, bidirectional Python-to-BhashaPy translation, syntax linting, and smart typo suggestions.

## Installation

```bash
pip install -e .
```

## Usage

- Start the interactive shell:
  ```bash
  bhashapy
  ```
- Run a `.bhasha` file:
  ```bash
  bhashapy demo.bhasha
  ```
- Validate syntax and view keyword stats without executing:
  ```bash
  bhashapy demo.bhasha --check
  ```
- Show translated Python code or export to `.py`:
  ```bash
  bhashapy demo.bhasha --show-python
  bhashapy demo.bhasha --export
  ```

## Key Features

- **All-New Hindi Keywords**: `likho` (`print`), `batao` (`input`), `yadi`/`ya_phir`/`nahi_toh` (`if`/`elif`/`else`), `dohrao` (`while`), `pratyek`/`andar`/`kram` (`for`/`in`/`range`), `vidhi`/`bhejo` (`def`/`return`), `dhancha` (`class`), `prayas`/`sambhalo`/`ant_mein` (`try`/`except`/`finally`), `satya`/`asatya`/`shunya` (`True`/`False`/`None`).
- **Built-in Helpers**:
  - `chuno(items)`: Randomly selects an item from a list or string.
  - `dabba(text)`: Prints text inside a framed ASCII box.
  - `palti(seq)`: Reverses a string or list.
  - `uljhao(seq)`: Scrambles characters or shuffles a list.
  - `dinank()`: Returns today's date with the Hindi weekday name.
- **Smart Typo Hints**: `NameError` messages suggest the closest matching BhashaPy keyword, built-in, or variable (`Kya aapka matlab 'likho' tha?`).
- **Bidirectional REPL**: Use `py <code>` to convert BhashaPy to Python, `bhasha <code>` to convert Python to BhashaPy, plus `history`, `stats`, `vars`, `reset`, and `run <file.bhasha>`.
