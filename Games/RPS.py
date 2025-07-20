from random import choice

players = int(input("Please enter numer of players: "))
while players not in [1,2]:
	players = int(input("Please enter numer of players: "))

player1_count = 0
player2_count = 0

for games in range(3):

	player1 = input("Player 1, make your move: ")
	while player1.lower() not in ["rock","paper","scissors"]:
		player1 = input("Player 1, make your move: ")

	if players == 2:
		player2 = input("Player 2, make your move: ")
		while player2.lower() not in ["rock","paper","scissors"]:
			player2 = input("Player 2, make your move: ")
	else:
		player2 = choice(["rock", "paper", "scissors"])
		print(f"Computer moved {player2}")

	if player1 == player2:
		print("It's a tie!")
	elif player1 == "rock" and player2 == "scissors":
		print("Player 1 wins!")
		player1_count += 1
	elif player1 == "paper" and player2 == "rock":
		print("Player 1 wins!")
		player1_count += 1
	elif player1 == "scissors" and player2 == "paper":
		print("Player 1 wins!")
		player1_count += 1
	elif players == 1:
		print("Computer wins!")
		player2_count += 1
	else:
		print("Player 2 wins!")
		player2_count += 1

print(f"Player 1 won {player1_count} games.")
print(f"Player 2 won {player2_count} games.")
if player1_count > player1_count:
	print("Player 1 is the winner!")
elif player1_count < player2_count:
	print("Player 2 is the winner!")
else:
	print("It's a tie!")