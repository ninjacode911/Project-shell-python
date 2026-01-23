import sys
def main():
    sys.stdout.write("$ ") # this lets you write '$' to the console

    command = input() # Captures the user's command in the "command" variable
    print(f"{command}: command not found") # prints the command not found message
if __name__ == "__main__":
    main()