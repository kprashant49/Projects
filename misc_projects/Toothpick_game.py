global toothpick_count
global player1
global player2
global current_player
toothpick_count = 13

def toothpick_image(toothpick_count):
    image = ("|") * toothpick_count
    return image

print("*****Welcome to the Toothpick Game!*****")
player1 = input("Player 1, please enter your name:")
player2 = input("Player 2, please enter your name:")
print(f"Total toothpicks available: {toothpick_image(toothpick_count)}")
current_player = player1

def swap_player(current_player):
    if current_player == player1:
        return player2
    elif current_player == player2:
        return player1
    return current_player

while True:
    pick = int(input(f"How many toothpicks do you wish to choose {current_player}?"))
    while pick not in [1,2,3]:
        pick = int(input(f"Incorrect input! Please enter between 1-3. How many toothpicks do you wish to choose {current_player}?"))
    if toothpick_count >3:
        toothpick_count -= pick
        current_player = swap_player(current_player)
        print(toothpick_image(toothpick_count))
    elif toothpick_count <=3:
        print(f"Yay! {current_player} wins!")
        break
print("*****Game Over!*****")