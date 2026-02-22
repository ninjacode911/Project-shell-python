import sys
import os
import subprocess
import io

try:
    import readline
except ImportError:
    pass

def parse_command(command):
    """Parse command line respecting single quotes, double quotes, and backslashes."""
    parts = []
    current_part = ""
    quote_char = None
    i = 0
    while i < len(command):
        char = command[i]
        if quote_char is None:
            if char == "\\":
                i += 1
                if i < len(command): current_part += command[i]
            elif char in ("'", '"'): quote_char = char
            elif char == " ":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else: current_part += char
        elif char == quote_char: quote_char = None
        elif char == "\\" and quote_char == '"':
            if i + 1 < len(command) and command[i+1] in ('"', '\\', '$', '`'):
                current_part += command[i+1]
                i += 1
            else: current_part += char
        else: current_part += char
        i += 1
    if current_part: parts.append(current_part)
    return parts

def get_executable_path(cmd):
    path_env = os.environ.get("PATH", "")
    for dir in path_env.split(os.pathsep):
        full_path = os.path.join(dir, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

def run_builtin(parts, out, err, builtins_list):
    """Executes a builtin command and writes output/error to specified streams."""
    cmd = parts[0]
    if cmd == "echo":
        print(" ".join(parts[1:]), file=out)
    elif cmd == "pwd":
        print(os.getcwd(), file=out)
    elif cmd == "cd":
        if len(parts) > 1:
            path = parts[1]
            if path == "~": path = os.path.expanduser("~")
            try: os.chdir(path)
            except Exception: print(f"cd: {path}: No such file or directory", file=err)
    elif cmd == "type":
        if len(parts) > 1:
            target = parts[1]
            if target in builtins_list:
                print(f"{target} is a shell builtin", file=out)
            else:
                full_path = get_executable_path(target)
                if full_path: print(f"{target} is {full_path}", file=out)
                else: print(f"{target}: not found", file=out)
    return True

def main():
    builtins_list = ["echo", "exit", "pwd", "cd", "type"]

    def completer(text, state):
        matches = [b for b in builtins_list if b.startswith(text)]
        path_env = os.environ.get("PATH", "")
        for directory in path_env.split(os.pathsep):
            if not os.path.isdir(directory): continue
            try:
                for filename in os.listdir(directory):
                    full_path = os.path.join(directory, filename)
                    if (filename.startswith(text) and os.path.isfile(full_path) and os.access(full_path, os.X_OK)):
                        matches.append(filename)
            except Exception: continue
        matches = sorted(list(set(matches)))
        if not matches: return None
        if len(matches) == 1:
            if state == 0: return matches[0] + " "
            return None
        common = os.path.commonprefix(matches)
        if len(common) > len(text):
            if state == 0: return common
            return None
        if state < len(matches): return matches[state]
        return None

    def display_matches(substitution, matches, longest_match_len):
        valid_matches = sorted(list(set([m for m in matches if m])))
        sys.stdout.write("\n" + "  ".join(valid_matches) + "\n$ " + readline.get_line_buffer())
        sys.stdout.flush()

    if 'readline' in sys.modules:
        readline.set_completer(completer)
        readline.set_completion_display_matches_hook(display_matches)
        readline.set_completer_delims('')
        if sys.platform != 'darwin': readline.parse_and_bind("tab: complete")

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        try: command_raw = input()
        except EOFError: break
        initial_parts = parse_command(command_raw)
        if not initial_parts: continue
        
        # Redirection/Pipe Parsing
        stdout_file_path, stderr_file_path = None, None
        stdout_mode, stderr_mode = "w", "w"
        parts = []
        i = 0
        while i < len(initial_parts):
            p = initial_parts[i]
            if p in (">", "1>"): stdout_file_path, stdout_mode, i = initial_parts[i+1], "w", i + 2
            elif p in (">>", "1>>"): stdout_file_path, stdout_mode, i = initial_parts[i+1], "a", i + 2
            elif p == "2>": stderr_file_path, stderr_mode, i = initial_parts[i+1], "w", i + 2
            elif p == "2>>": stderr_file_path, stderr_mode, i = initial_parts[i+1], "a", i + 2
            else: parts.append(p); i += 1

        if not parts: continue

        # --- PIPELINE HANDLING ---
        if "|" in parts:
            idx = parts.index("|")
            cmd1_p, cmd2_p = parts[:idx], parts[idx+1:]
            
            output_file = open(stdout_file_path, stdout_mode) if stdout_file_path else None
            error_file = open(stderr_file_path, stderr_mode) if stderr_file_path else None
            
            try:
                # Case 1: External | External
                if cmd1_p[0] not in builtins_list and cmd2_p[0] not in builtins_list:
                    p1 = subprocess.Popen(cmd1_p, stdout=subprocess.PIPE)
                    p2 = subprocess.Popen(cmd2_p, stdin=p1.stdout, stdout=output_file, stderr=error_file)
                    p1.stdout.close(); p2.communicate()
                
                # Case 2: Builtin | External
                elif cmd1_p[0] in builtins_list:
                    capture = io.StringIO()
                    run_builtin(cmd1_p, capture, sys.stderr, builtins_list)
                    subprocess.run(cmd2_p, input=capture.getvalue().encode(), stdout=output_file, stderr=error_file)
                
                # Case 3: External | Builtin (e.g., ls | type exit)
                else:
                    p1 = subprocess.Popen(cmd1_p, stdout=subprocess.PIPE)
                    run_builtin(cmd2_p, output_file or sys.stdout, error_file or sys.stderr, builtins_list)
                    p1.communicate()
            finally:
                if output_file: output_file.close()
                if error_file: error_file.close()
            continue

        # --- SINGLE COMMAND HANDLING ---
        stdout_file = open(stdout_file_path, stdout_mode) if stdout_file_path else None
        stderr_file = open(stderr_file_path, stderr_mode) if stderr_file_path else None
        try:
            out, err = (stdout_file or sys.stdout), (stderr_file or sys.stderr)
            if parts[0] == "exit": break
            if parts[0] in builtins_list:
                run_builtin(parts, out, err, builtins_list)
            elif get_executable_path(parts[0]):
                subprocess.run(parts, stdout=stdout_file, stderr=stderr_file)
            else:
                print(f"{parts[0]}: command not found", file=err)
        finally:
            if stdout_file: stdout_file.close()
            if stderr_file: stderr_file.close()

if __name__ == "__main__":
    main()