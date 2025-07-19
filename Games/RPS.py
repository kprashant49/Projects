player1 = input("Player 1, make your move: ")
while player1.lower() not in ["rock","paper","scissors"]:
	player1 = input("Player 1, make your move: ")

player2 = input("Player 2, make your move: ")
while player2.lower() not in ["rock","paper","scissors"]:
	player2 = input("Player 2, make your move: ")

if player1 == player2:
	print("It's a tie!")
elif player1 == "rock" and player2 == "scissors":
	print("Player 1 wins!")
elif player1 == "paper" and player2 == "rock":
	print("Player 1 wins!")
elif player1 == "scissors" and player2 == "paper":
	print("Player 1 wins!")
else:
	print("Player 2 wins!")