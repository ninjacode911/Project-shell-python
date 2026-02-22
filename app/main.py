import sys
import os
import subprocess

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
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        try:
            command_raw = input()
        except EOFError:
            break
            
        parts = parse_command(command_raw)
        if not parts:
            continue
            
        # --- REDIRECTION LOGIC ---
        redirect_file = None
        # Look for > or 1> in the arguments
        if ">" in parts:
            idx = parts.index(">")
            redirect_file = parts[idx + 1]
            parts = parts[:idx] # Remove > and filename from command
        elif "1>" in parts:
            idx = parts.index("1>")
            redirect_file = parts[idx + 1]
            parts = parts[:idx]

        output_file = None
        if redirect_file:
            # Open file for writing (creates if missing, overwrites if exists)
            output_file = open(redirect_file, "w")
        
        try:
            cmd = parts[0]

            if cmd == "exit":
                break

            elif cmd == "echo":
                # Use 'file' argument to redirect print output
                print(" ".join(parts[1:]), file=output_file if output_file else sys.stdout)

            elif cmd == "pwd":
                print(os.getcwd(), file=output_file if output_file else sys.stdout)

            elif cmd == "cd":
                if len(parts) > 1:
                    path = parts[1]
                    if path == "~":
                        path = os.path.expanduser("~")
                    try:
                        os.chdir(path)
                    except (FileNotFoundError, NotADirectoryError):
                        print(f"cd: {path}: No such file or directory")

            elif cmd == "type":
                if len(parts) > 1:
                    target = parts[1]
                    builtins = ["echo", "exit", "pwd", "cd", "type"]
                    out = sys.stdout if not output_file else output_file
                    
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
                # External Commands
                path_env = os.environ.get("PATH", "")
                found_path = None
                for dir in path_env.split(os.pathsep):
                    full_path = os.path.join(dir, cmd)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        found_path = full_path
                        break
                
                if found_path:
                    # Pass the file object to subprocess.run's stdout argument
                    subprocess.run(parts, stdout=output_file if output_file else None)
                else:
                    print(f"{cmd}: command not found")
        finally:
            if output_file:
                output_file.close()

if __name__ == "__main__":
    main()