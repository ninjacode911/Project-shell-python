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
            # OUTSIDE of any quotes
            if char == "\\":
                # Backslash escaping: take the next character literally
                i += 1
                if i < len(command):
                    current_part += command[i]
            elif char in ("'", '"'):
                # Enter quote mode
                quote_char = char
            elif char == " ":
                # Space is a delimiter outside of quotes
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        elif char == quote_char:
            # Found the matching closing quote
            quote_char = None
        else:
            # INSIDE quotes
            # Note: For this stage, we are treating double quotes literally 
            # (except for closing). Future stages might add backslash support INSIDE double quotes.
            current_part += char
        
        i += 1

    # Add the final part if it exists
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
            
        cmd = parts[0]

        # 1. Builtin: exit
        if cmd == "exit":
            break

        # 2. Builtin: echo
        elif cmd == "echo":
            print(" ".join(parts[1:]))

        # 3. Builtin: pwd
        elif cmd == "pwd":
            print(os.getcwd())

        # 4. Builtin: cd
        elif cmd == "cd":
            if len(parts) > 1:
                path = parts[1]
                if path == "~":
                    path = os.path.expanduser("~")
                try:
                    os.chdir(path)
                except (FileNotFoundError, NotADirectoryError):
                    print(f"cd: {path}: No such file or directory")

        # 5. Builtin: type
        elif cmd == "type":
            if len(parts) > 1:
                target = parts[1]
                builtins = ["echo", "exit", "pwd", "cd", "type"]
                
                if target in builtins:
                    print(f"{target} is a shell builtin")
                else:
                    # Search PATH for external command
                    path_env = os.environ.get("PATH", "")
                    found_path = None
                    for dir in path_env.split(os.pathsep):
                        full_path = os.path.join(dir, target)
                        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                            found_path = full_path
                            break
                    
                    if found_path:
                        print(f"{target} is {found_path}")
                    else:
                        print(f"{target}: not found")

        # 6. External Commands
        else:
            path_env = os.environ.get("PATH", "")
            found_path = None
            for dir in path_env.split(os.pathsep):
                full_path = os.path.join(dir, cmd)
                if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                    found_path = full_path
                    break
            
            if found_path:
                # Run the external program with parsed arguments
                subprocess.run(parts)
            else:
                print(f"{cmd}: command not found")

if __name__ == "__main__":
    main()