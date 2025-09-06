from random import randint

print("Welcome to the number guessing game!")
print("I'm thinking of a number between 1 and 10.")

def game_logic(player, computer):
    if player > computer:
        return f"You guessed too high! The number was {computer}"
    elif player < computer:
        return f"You guessed too low! The number was {computer}"
    else:
        return f"You guessed it right! The number was {computer}"

while True:
    try:
        player = int(input("Guess a number between 1 to 10: "))
    except ValueError:
        print("That's not a number!")
        continue

    computer = randint(1, 10)
    print(game_logic(player,computer))

    play_again = input("Do you want to play again? (y/n): ").lower()
    if play_again != "y":
        print("Thanks for playing!")
        break