accounts = {}

# Loop for user actions
while True:
    action = input("Enter 'add' to add account, 'remove' to remove account, or 'done' to finish: ").strip().lower()

    if action == 'add':
        acc_num = input("Enter account number: ")
        holder = input("Enter account holder name: ")
        balance = float(input("Enter initial balance: "))

        # Create a dictionary for account and add it to accounts
        accounts[acc_num] = {
            "account_holder": holder,
            "balance": balance
        }

    elif action == 'remove':
        acc_num = input("Enter account number to remove: ")
        if acc_num in accounts:
            del accounts[acc_num]
            print("Account removed.")
        else:
            print("Account not found.")

    elif action == 'done':
        break

    else:
        print("Invalid input. Please enter 'add', 'remove', or 'done'.")

# Calculate total assets
total_assets = 0
for acc in accounts.values():
    total_assets += acc["balance"]

print(f"\nTotal assets in all accounts: {total_assets}")
print(accounts)
