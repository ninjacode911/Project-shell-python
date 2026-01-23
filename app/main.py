import sys
def main():
    while True: # this adds an infinite loop to make sure the program runs continuously
        sys.stdout.write("$ ") # this lets you write '$' to the console
        command = input() # Captures the user's command in the "command" variable

        if command == "exit":
            break
        else:
            print(f"{command}: command not found") # prints the command not found message


if __name__ == "__main__":
    main()
