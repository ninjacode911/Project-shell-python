import sys


def main():
    # TODO: Uncomment the code below to pass the first stage
    sys.stdout.write("$ ") # this lets you write '$' to the console

# Captures the user's command in the "command" variable
command=input()
print(f'{command}: command not found')


if __name__ == "__main__":
    main()
