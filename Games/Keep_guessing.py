from random import randint

print("Welcome to the number guessing game!")
print("I'm thinking of a number between 1 and 10.")

while True:
    player = int(input("Guess a number between 1 to 10: "))
    computer = randint(1, 10)

    if player > computer:
        print("You guessed too high!",computer)
    elif player < computer:
        print("You guessed too low!",computer)
    else:
        print("You guessed it right!")
        play_again = input("Do you want to play again? (y/n): ")
        if play_again == "y":
            computer = randint(1, 10)
        else:
            print("Thanks for playing!")
            break