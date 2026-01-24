import sys
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
                print(f"{cmd_to_check}: is a shell builtin")
            else:
                print(f"{cmd_to_check}: not found")
        else:
            print(f"{command}: command not found") # prints the command not found message


if __name__ == "__main__":
    main()
