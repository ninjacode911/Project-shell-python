import sys #importing sys module to interact with the system
import os   #importing os module to interact with the operating system
import subprocess #importing subprocess module to run external commands


def parse_command(command):
    """Parse command line respecting single quotes and double quotes."""
    parts = []
    current_part = ""
    quote_char = None  # This will be None, "'", or '"'

    i = 0
    while i < len(command):
        char = command[i]

        if quote_char is None:
            # We are NOT inside any quotes
            if char in ("'", '"'):
                quote_char = char  # Enter quote mode (single or double)
            elif char == " ":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
        elif char == quote_char:
            # We found the MATCHING closing quote
            quote_char = None
        else:
            # We are inside quotes, treat everything literally
            current_part += char
        i += 1

    if current_part:
        parts.append(current_part)
    return parts


def main():
    while True: # this adds an infinite loop to make sure the program runs continuously
        sys.stdout.write("$ ") # this lets you write '$' to the console
        command = input() # Captures the user's command in the "command" variable
        parts = parse_command(command) # splits the command into a list of words


        # if-starts 

        if command == "exit":  # if the command is exit, break the loop
            break

        elif command.startswith("echo"):
            print(" ".join(parts[1:])) # joins the list of words back into a string


        elif command.startswith("type "):
            cmd_to_check = command.split()[1]
            if cmd_to_check in ['echo', 'exit', 'type', 'pwd', 'cd']:
                print(f"{cmd_to_check} is a shell builtin")
            else:
                #search in path
                path_env = os.environ.get('PATH','')
                directories = path_env.split(os.pathsep)
                found = False
                for directory in directories:
                    file_path = os.path.join(directory, cmd_to_check)
                    if os.path.exists(file_path) and os.access(file_path, os.X_OK):
                        print(f"{cmd_to_check} is {file_path}")
                        found = True
                        break
                if not found:
                    print(f"{cmd_to_check}: not found")

        elif command.startswith('cd '):
            directory = parts[1]

            if directory == '~':
                directory = os.path.expanduser('~')

            try:
                os.chdir(directory)
            except FileNotFoundError:
                print(f"cd: {directory}: No such file or directory")

        elif command == "pwd":
            print(os.getcwd())

        else:
            #not a bulletin but try to run as an external program
            #split to get program name and arguments
            if len(parts) == 0:
                continue
            
            program_name = parts[0]

            path_env = os.environ.get('PATH','')
            directories = path_env.split(os.pathsep)

            found= False
            for directory in directories:
                file_path = os.path.join(directory, program_name)
                if os.path.exists(file_path) and os.access(file_path, os.X_OK):
                    
                    found = True
                    break
            if found:
                subprocess.run([program_name] + parts[1:])
            else:
                print(f"{command}: command not found")


if __name__ == "__main__":
    main()
