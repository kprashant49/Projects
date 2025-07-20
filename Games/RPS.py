from random import choice

players = int(input("Please enter numer of players: "))
while players not in [1,2]:
	players = int(input("Please enter numer of players: "))

Matches = int(input("Please enter number of matches: "))
if Matches%2 == 0:
	Winner = round((Matches/2),0)+1
else:
	Winner = round((Matches+1)/2,0)

player1_count = 0
player2_count = 0
ties = 0

# for games in range(Matches):
while player1_count < Winner and player2_count < Winner:
	if players == 1:
		print(f"Player 1: {player1_count} Computer: {player2_count} Ties: {ties}")
	else:
		print(f"Player 1: {player1_count} Player 2: {player2_count} Ties: {ties}")

	player1 = input("Player 1, make your move: ")
	if player1 == 'quit':
		break
	while player1.lower() not in ["rock","paper","scissors"]:
		player1 = input("Player 1, make your move: ")

	if players == 2:
		player2 = input("Player 2, make your move: ")
		while player2.lower() not in ["rock","paper","scissors"]:
			player2 = input("Player 2, make your move: ")
	else:
		player2 = choice(["rock", "paper", "scissors"])
		print(f"Computer moved {player2}")

	player1 = player1.lower()
	player2 = player2.lower()

	if player1 == player2:
		print("It's a tie!")
		ties += 1
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

if players == 1:
	print(f"Player 1: {player1_count} Computer: {player2_count} Ties: {ties}")
else:
	print(f"Player 1: {player1_count} Player 2: {player2_count} Ties: {ties}")

if player1_count > player2_count:
	print("Player 1 is the winner!")
elif player1_count < player2_count and players == 1:
	print("Computer is the winner!")
elif player1_count < player2_count and players == 2:
	print("Player 2 is the winner!")
else:
	print("It's a tie!")