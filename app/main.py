import sys
import os
import subprocess

try:
    import readline
except ImportError:
    # Readline is not available on basic Windows Python installations,
    # but is available on Linux where the tests run.
    pass

def parse_command(command):
    """Parse command line respecting single quotes, double quotes, and backslashes."""
    parts = []
    current_part = ""
    quote_char = None  # None, "'", or '"'
    
    i = 0
    while i < len(command):
        char = command[i]
        if quote_char is None:
            if char == "\\":
                i += 1
                if i < len(command):
                    current_part += command[i]
            elif char in ("'", '"'):
                quote_char = char
            elif char == " ":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        elif char == quote_char:
            quote_char = None
        elif char == "\\" and quote_char == '"':
            if i + 1 < len(command) and command[i+1] in ('"', '\\', '$', '`'):
                current_part += command[i+1]
                i += 1
            else:
                current_part += char
        else:
            current_part += char
        i += 1
    if current_part:
        parts.append(current_part)
    return parts

def main():
    # --- AUTOCOMPLETION SETUP ---
    builtins_list = ["echo", "exit", "pwd", "cd", "type"]

    def completer(text, state):
        # Filter builtins that start with the text being typed
        matches = [b for b in builtins_list if b.startswith(text)]
        if state < len(matches):
            return matches[state] + " " # Add trailing space
        return None

    if 'readline' in sys.modules:
        readline.set_completer(completer)
        # Use tab for completion
        if sys.platform == 'darwin': # macOS support
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        try:
            command_raw = input()
        except EOFError:
            break
            
        initial_parts = parse_command(command_raw)
        if not initial_parts:
            continue
            
        # --- REDIRECTION LOGIC ---
        stdout_file_path = None
        stderr_file_path = None
        stdout_mode = "w"
        stderr_mode = "w"
        parts = []
        
        i = 0
        while i < len(initial_parts):
            p = initial_parts[i]
            if p in (">", "1>"):
                stdout_file_path = initial_parts[i+1]
                stdout_mode = "w"
                i += 2
            elif p in (">>", "1>>"):
                stdout_file_path = initial_parts[i+1]
                stdout_mode = "a"
                i += 2
            elif p == "2>":
                stderr_file_path = initial_parts[i+1]
                stderr_mode = "w"
                i += 2
            elif p == "2>>":
                stderr_file_path = initial_parts[i+1]
                stderr_mode = "a"
                i += 2
            else:
                parts.append(p)
                i += 1

        if not parts:
            continue

        stdout_file = None
        stderr_file = None
        
        try:
            if stdout_file_path:
                stdout_file = open(stdout_file_path, stdout_mode)
            if stderr_file_path:
                stderr_file = open(stderr_file_path, stderr_mode)

            cmd = parts[0]
            out = stdout_file if stdout_file else sys.stdout
            err = stderr_file if stderr_file else sys.stderr

            if cmd == "exit":
                break
            elif cmd == "echo":
                print(" ".join(parts[1:]), file=out)
            elif cmd == "pwd":
                print(os.getcwd(), file=out)
            elif cmd == "cd":
                if len(parts) > 1:
                    path = parts[1]
                    if path == "~":
                        path = os.path.expanduser("~")
                    try:
                        os.chdir(path)
                    except (FileNotFoundError, NotADirectoryError):
                        print(f"cd: {path}: No such file or directory", file=err)
            elif cmd == "type":
                if len(parts) > 1:
                    target = parts[1]
                    builtins = ["echo", "exit", "pwd", "cd", "type"]
                    if target in builtins:
                        print(f"{target} is a shell builtin", file=out)
                    else:
                        path_env = os.environ.get("PATH", "")
                        found_path = None
                        for dir in path_env.split(os.pathsep):
                            full_path = os.path.join(dir, target)
                            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                                found_path = full_path
                                break
                        if found_path:
                            print(f"{target} is {found_path}", file=out)
                        else:
                            print(f"{target}: not found", file=out)
            else:
                path_env = os.environ.get("PATH", "")
                found_path = None
                for dir in path_env.split(os.pathsep):
                    full_path = os.path.join(dir, cmd)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        found_path = full_path
                        break
                
                if found_path:
                    subprocess.run(parts, stdout=stdout_file, stderr=stderr_file)
                else:
                    print(f"{cmd}: command not found", file=err)
        
        finally:
            if stdout_file: stdout_file.close()
            if stderr_file: stderr_file.close()

if __name__ == "__main__":
    main()