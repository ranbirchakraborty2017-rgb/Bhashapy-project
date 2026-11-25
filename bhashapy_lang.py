import datetime
import difflib
import io
import os
import random
import sys
import tokenize
import traceback

# Enables Up/Down arrow key history on Mac & Linux
try:
    import readline  # noqa: F401
except ImportError:
    pass


# ==========================================
# 0. TERMINAL COLORS (ANSI)
# ==========================================
class Color:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


# ==========================================
# 1. DEFINE BHASHAPY KEYWORDS
#    Format: "hindi_word": "python_word"
# ==========================================
KEYWORDS = {
    # Input / Output
    "likho": "print",
    "batao": "input",

    # Conditionals
    "yadi": "if",
    "ya_phir": "elif",
    "nahi_toh": "else",

    # Loops
    "dohrao": "while",
    "pratyek": "for",
    "andar": "in",
    "kram": "range",
    "thamo": "break",
    "badho": "continue",
    "jaane_do": "pass",

    # Functions, Classes & Imports
    "vidhi": "def",
    "bhejo": "return",
    "dhancha": "class",
    "bulao": "import",
    "me_se": "from",
    "rup_mein": "as",

    # Error Handling
    "prayas": "try",
    "sambhalo": "except",
    "ant_mein": "finally",
    "uthao": "raise",

    # Logic & Values
    "satya": "True",
    "asatya": "False",
    "shunya": "None",
    "tatha": "and",
    "athwa": "or",
    "mat": "not",
    "hai": "is",

    # Useful Built-in Functions
    "maap": "len",
    "kul": "sum",
    "adhik": "max",
    "nyun": "min",
    "kramit": "sorted",
    "poorn": "int",
    "bindu": "float",
    "paath": "str",
    "taalika": "list",
    "shabdkosh": "dict",
    "prakar": "type",
    "kholo": "open",
}

REVERSE_KEYWORDS = {v: k for k, v in KEYWORDS.items()}


# ==========================================
# 2. BUILT-IN BHASHAPY SUPERPOWER FUNCTIONS
# ==========================================
HINDI_DAYS = [
    "Somwar",
    "Mangalwar",
    "Budhwar",
    "Guruwar",
    "Shukrawar",
    "Shaniwar",
    "Raviwar",
]


def _builtin_chuno(items):
    """Picks a random element from a non-empty sequence."""
    seq = list(items)
    if not seq:
        raise ValueError("Khali list ya text me se kuch chuna nahi ja sakta!")
    return random.choice(seq)


def _builtin_dabba(text) -> str:
    """Prints text inside a neat decorative Unicode box and returns the framed string."""
    s = str(text)
    lines = s.splitlines() or [""]
    width = max(len(line) for line in lines)
    top = "+" + "-" * (width + 2) + "+"
    body = [f"| {line.ljust(width)} |" for line in lines]
    boxed = "\n".join([top, *body, top])
    print(boxed)
    return boxed


def _builtin_palti(seq):
    """Returns a reversed copy of a string, list, or tuple."""
    if isinstance(seq, str):
        return seq[::-1]
    return list(reversed(seq))


def _builtin_uljhao(items):
    """Returns a shuffled list or scrambled string."""
    if isinstance(items, str):
        chars = list(items)
        random.shuffle(chars)
        return "".join(chars)
    copied = list(items)
    random.shuffle(copied)
    return copied


def _builtin_dinank() -> str:
    """Returns today's date with the Hindi weekday name."""
    now = datetime.datetime.now()
    day_name = HINDI_DAYS[now.weekday()]
    return f"{day_name}, {now.strftime('%d-%m-%Y')}"


BHASHA_BUILTINS = {
    "chuno": _builtin_chuno,
    "dabba": _builtin_dabba,
    "palti": _builtin_palti,
    "uljhao": _builtin_uljhao,
    "dinank": _builtin_dinank,
}


def create_env() -> dict:
    """Creates a fresh execution environment with BhashaPy helpers."""
    return dict(BHASHA_BUILTINS)


# ==========================================
# 3. HINGLISH ERROR TRANSLATOR + TYPO HINTS
# ==========================================
def get_error_line(err: Exception, source_name: str):
    """Finds the exact line number in the user's code."""
    if isinstance(err, SyntaxError) and err.lineno:
        return err.lineno

    tb = traceback.extract_tb(err.__traceback__)
    for frame in reversed(tb):
        if frame.filename == source_name:
            return frame.lineno
    return None


def suggest_closest_word(word: str, env: dict | None = None) -> str | None:
    """Suggests the closest BhashaPy keyword, builtin, or variable name."""
    candidates = list(KEYWORDS.keys()) + list(BHASHA_BUILTINS.keys())
    if env:
        candidates.extend(
            k for k in env.keys()
            if k != "__builtins__" and not k.startswith("_")
        )
    matches = difflib.get_close_matches(word, candidates, n=1, cutoff=0.6)
    return matches[0] if matches else None


def format_hinglish_error(
    err: Exception,
    source_name: str = "<interactive>",
    env: dict | None = None,
) -> str:
    """Converts Python exceptions into friendly Hinglish messages with typo hints."""
    line_no = get_error_line(err, source_name)
    loc = f" (Line {line_no})" if line_no and source_name != "<interactive>" else ""

    if isinstance(err, tokenize.TokenError):
        msg = "Code adhoora reh gaya! Shayad koi quote (\" \") ya bracket () band karna bhool gaye."
    elif isinstance(err, IndentationError):
        msg = "Spacing (Indentation) galat hai! Colon (:) ke baad agli line mein 4 spaces ya Tab lagana zaroori hai."
    elif isinstance(err, SyntaxError):
        msg = "Likhne ka tareeka (Syntax) galat hai! Check karo kahin colon (:), bracket (), ya quote (\" \") toh nahi chhoota."
    elif isinstance(err, NameError):
        var_name = getattr(err, "name", None)
        if var_name:
            suggestion = suggest_closest_word(var_name, env=env)
            hint = f" Kya aapka matlab '{suggestion}' tha?" if suggestion else ""
            msg = (
                f"Arre! '{var_name}' naam ka koi variable ya shabd mila hi nahi.{hint}"
                " Spelling check karo ya pehle isko define karo."
            )
        else:
            msg = "Koi aisa naam use kiya hai jo pehle define nahi hua. Spelling check karo!"
    elif isinstance(err, ZeroDivisionError):
        msg = "Ganit ka niyam toot gaya! Kisi bhi sankhya ko shunya (0) se divide nahi kar sakte."
    elif isinstance(err, TypeError):
        msg = "Data prakar match nahi kar rahe! Jaise paath (string) aur poorn (number) ko seedha jod nahi sakte."
    elif isinstance(err, ValueError):
        msg = f"Value galat hai! ({err})"
    elif isinstance(err, IndexError):
        msg = "Taalika (list) ki seema paar ho gayi! Jis index ko dhoond rahe ho, utne items nahi hain."
    elif isinstance(err, KeyError):
        msg = f"Shabdkosh (dict) mein {err} naam ki key maujood nahi hai!"
    elif isinstance(err, ModuleNotFoundError):
        mod_name = getattr(err, "name", "ye module")
        msg = f"'{mod_name}' naam ki library nahi mili. Check karo ki ye installed hai."
    else:
        msg = f"Kuch gadbad ho gayi ({type(err).__name__})."

    return (
        f"\n{Color.RED}{Color.BOLD}[Truti{loc}]:{Color.RESET} {Color.RED}{msg}{Color.RESET}\n"
        f"{Color.DIM}  -> Technical Detail: {type(err).__name__}: {err}{Color.RESET}\n"
    )


# ==========================================
# 4. BIDIRECTIONAL TRANSPILER & ANALYZER
# ==========================================
def _replace_tokens(source_code: str, mapping: dict[str, str]) -> tuple[str, int]:
    """Replaces NAME tokens using mapping (skipping attribute access after '.')."""
    lines = source_code.splitlines(keepends=True)
    if not lines:
        return "", 0

    replacements = []
    prev_token = None

    tokens = tokenize.generate_tokens(io.StringIO(source_code).readline)
    for tok in tokens:
        if tok.type == tokenize.NAME and tok.string in mapping and prev_token != ".":
            replacements.append(tok)
        if tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT):
            prev_token = tok.string

    for tok in reversed(replacements):
        line_idx = tok.start[0] - 1
        start_col = tok.start[1]
        end_col = tok.end[1]
        lines[line_idx] = (
            lines[line_idx][:start_col]
            + mapping[tok.string]
            + lines[line_idx][end_col:]
        )

    return "".join(lines), len(replacements)


def translate_to_python(source_code: str) -> str:
    """Translates BhashaPy keywords into valid Python code."""
    translated, _ = _replace_tokens(source_code, KEYWORDS)
    return translated


def translate_to_bhasha(python_code: str) -> str:
    """Reverse-translates standard Python code into BhashaPy keywords."""
    translated, _ = _replace_tokens(python_code, REVERSE_KEYWORDS)
    return translated


def analyze_code(source_code: str) -> dict:
    """Validates BhashaPy code and returns keyword/structure statistics."""
    python_code, keyword_count = _replace_tokens(source_code, KEYWORDS)
    compile(python_code, "<check>", "exec")
    lines = [ln for ln in source_code.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return {
        "valid": True,
        "non_empty_lines": len(lines),
        "bhasha_keywords_used": keyword_count,
        "python_code": python_code,
    }


# ==========================================
# 5. FILE RUNNER, LINTER & EXPORTER
# ==========================================
def run_file(
    filepath: str,
    show_python: bool = False,
    export_py: bool = False,
    check_only: bool = False,
):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            custom_code = f.read()
    except FileNotFoundError:
        print(f"\n{Color.RED}[Truti]: '{filepath}' naam ki file mili hi nahi! Naam aur folder check karo.{Color.RESET}\n")
        return

    env = create_env()

    try:
        if check_only:
            stats = analyze_code(custom_code)
            print(f"{Color.GREEN}[Shuddh!]{Color.RESET} '{filepath}' mein koi syntax truti nahi hai.")
            print(
                f"{Color.DIM}  -> Active lines: {stats['non_empty_lines']} | "
                f"BhashaPy keywords used: {stats['bhasha_keywords_used']}{Color.RESET}\n"
            )
            return

        python_code = translate_to_python(custom_code)

        if export_py:
            out_path = filepath[:-7] + ".py" if filepath.endswith(".bhasha") else filepath + ".py"
            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(python_code)
            print(f"{Color.GREEN}[Exported]: Python file saved to '{out_path}'{Color.RESET}\n")

        if show_python:
            print(f"{Color.GREEN}--- Translated Python Code ---{Color.RESET}")
            print(f"{Color.DIM}{python_code}{Color.RESET}")
            print(f"{Color.GREEN}------------------------------{Color.RESET}\n")

        compiled = compile(python_code, filepath, "exec")
        exec(compiled, env)
    except Exception as e:
        print(format_hinglish_error(e, source_name=filepath, env=env))


# ==========================================
# 6. INTERACTIVE SHELL (REPL)
# ==========================================
def show_dictionary():
    print(f"\n{Color.YELLOW}{Color.BOLD}--- BhashaPy Keyword Dictionary ---{Color.RESET}")
    items = list(KEYWORDS.items())
    half = (len(items) + 1) // 2
    for i in range(half):
        left_k, left_v = items[i]
        left_str = f"  {Color.CYAN}{left_k:<12}{Color.RESET} -> {left_v:<10}"
        if i + half < len(items):
            right_k, right_v = items[i + half]
            right_str = f"  {Color.CYAN}{right_k:<12}{Color.RESET} -> {right_v}"
        else:
            right_str = ""
        print(f"{left_str}{right_str}")

    print(f"\n{Color.YELLOW}{Color.BOLD}--- Built-in Superpowers ---{Color.RESET}")
    print(f"  {Color.MAGENTA}chuno(items){Color.RESET}  -> List/text me se random item chunta hai")
    print(f"  {Color.MAGENTA}dabba(text){Color.RESET}   -> Text ko sundar box ke andar print karta hai")
    print(f"  {Color.MAGENTA}palti(seq){Color.RESET}    -> Text ya list ko ulta (reverse) karta hai")
    print(f"  {Color.MAGENTA}uljhao(seq){Color.RESET}   -> Text ya list ke items ko shuffle karta hai")
    print(f"  {Color.MAGENTA}dinank(){Color.RESET}      -> Aaj ka din (Hindi mein) aur date batata hai")

    print(f"\n{Color.YELLOW}{Color.BOLD}--- Shell Commands ---{Color.RESET}")
    print("  help | vars | history | stats | py <code> | bhasha <code> | run <file.bhasha> | clear | reset | exit\n")


def show_vars(env: dict):
    user_vars = {
        k: v for k, v in env.items()
        if k != "__builtins__" and k not in BHASHA_BUILTINS
    }
    if not user_vars:
        print(f"{Color.DIM}Abhi koi variable ya vidhi saved nahi hai.{Color.RESET}")
        return

    print(f"\n{Color.YELLOW}--- Saved Variables & Vidhiyan ---{Color.RESET}")
    for k, v in user_vars.items():
        print(f"  {Color.CYAN}{k}{Color.RESET} = {repr(v)}  {Color.DIM}({type(v).__name__}){Color.RESET}")
    print()


def _needs_continuation(text: str) -> bool:
    """Checks if a line ends with ':' or has unclosed brackets."""
    stripped = text.strip()
    if stripped.endswith(":"):
        return True
    opens = sum(text.count(ch) for ch in "([{")
    closes = sum(text.count(ch) for ch in ")]}")
    return opens > closes


def run_repl():
    print(f"{Color.CYAN}{Color.BOLD}==================================================")
    print("   Swagat hai BhashaPy v1.0 mein! (Hinglish Python)")
    print("   Type 'help' for shabdkosh, 'exit' to quit       ")
    print(f"=================================================={Color.RESET}\n")

    env = create_env()
    session_history: list[str] = []
    error_count = 0

    while True:
        try:
            line = input(f"{Color.CYAN}{Color.BOLD}bhasha>> {Color.RESET}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Color.YELLOW}Phir milenge! Namaste!{Color.RESET}")
            break

        cmd = line.strip()
        if not cmd:
            continue
        if cmd == "exit":
            print(f"{Color.YELLOW}Phir milenge! Namaste!{Color.RESET}")
            break
        if cmd == "help":
            show_dictionary()
            continue
        if cmd == "vars":
            show_vars(env)
            continue
        if cmd == "history":
            if not session_history:
                print(f"{Color.DIM}Abhi tak koi code run nahi hua.{Color.RESET}")
            else:
                for idx, item in enumerate(session_history, 1):
                    print(f"  {Color.DIM}{idx:>2}.{Color.RESET} {item}")
            continue
        if cmd == "stats":
            var_count = sum(
                1 for k in env if k != "__builtins__" and k not in BHASHA_BUILTINS
            )
            print(
                f"{Color.BLUE}[Session Stats]{Color.RESET} "
                f"Commands: {len(session_history)} | Variables: {var_count} | Errors: {error_count}"
            )
            continue
        if cmd == "clear":
            os.system("cls" if os.name == "nt" else "clear")
            continue
        if cmd == "reset":
            env = create_env()
            session_history.clear()
            error_count = 0
            print(f"{Color.GREEN}Memory saaf ho gayi! Nayi shuruaat.{Color.RESET}")
            continue
        if cmd.startswith("py "):
            snippet = cmd[3:]
            try:
                print(f"{Color.GREEN}Python -> {Color.RESET}{translate_to_python(snippet)}")
            except Exception as e:
                print(format_hinglish_error(e, env=env))
            continue
        if cmd.startswith("bhasha "):
            snippet = cmd[7:]
            try:
                print(f"{Color.CYAN}BhashaPy -> {Color.RESET}{translate_to_bhasha(snippet)}")
            except Exception as e:
                print(format_hinglish_error(e, env=env))
            continue
        if cmd.startswith("run "):
            filepath = cmd[4:].strip()
            run_file(filepath)
            continue

        code_lines = [line]
        if _needs_continuation(line):
            while True:
                try:
                    sub_line = input(f"{Color.DIM}...      {Color.RESET}")
                except (EOFError, KeyboardInterrupt):
                    break
                if sub_line.strip() == "":
                    break
                code_lines.append(sub_line)

        full_code = "\n".join(code_lines)
        session_history.append(cmd)

        try:
            py_code = translate_to_python(full_code)
            try:
                compiled = compile(py_code, "<interactive>", "eval")
                result = eval(compiled, env)
                if result is not None:
                    print(f"{Color.GREEN}{result}{Color.RESET}")
            except SyntaxError:
                compiled = compile(py_code, "<interactive>", "exec")
                exec(compiled, env)
        except Exception as e:
            error_count += 1
            print(format_hinglish_error(e, source_name="<interactive>", env=env))


# ==========================================
# 7. ENTRY POINT
# ==========================================
def main():
    if len(sys.argv) > 1:
        show_py = "--show-python" in sys.argv
        export_py = "--export" in sys.argv
        check_only = "--check" in sys.argv
        args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
        if args:
            run_file(
                args[0],
                show_python=show_py,
                export_py=export_py,
                check_only=check_only,
            )
        else:
            run_repl()
    else:
        run_repl()


if __name__ == "__main__":
    main()
