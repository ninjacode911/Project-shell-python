import sys #importing sys module to interact with the system
import os   #importing os module to interact with the operating system
import subprocess #importing subprocess module to run external commands
def main():
    while True: # this adds an infinite loop to make sure the program runs continuously
        sys.stdout.write("$ ") # this lets you write '$' to the console
        command = input() # Captures the user's command in the "command" variable
        parts = command.split() # splits the command into a list of words




        if command == "exit":
            break
        elif command.startswith("echo"):
            print(" ".join(parts[1:])) # joins the list of words back into a string

        elif command.startswith("type "):
            cmd_to_check = command.split()[1]
            if cmd_to_check in ['echo', 'exit', 'type']:
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
                print(f"{command}: command not found") # prints the command not found message


if __name__ == "__main__":
    main()
