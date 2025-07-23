class BankAccount:
    def __init__(self, account_number, account_holder, balance = 0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance


accounts = {}

# Input loop for adding/removing accounts
while True:
    action = input("Enter 'add' to add account, 'remove' to remove account, or 'done' to finish: ").strip().lower()

    if action == 'add':
        acc_num = int(input("Enter account number: "))
        holder = input("Enter account holder name: ")
        balance = float(input("Enter initial balance: "))
        accounts[acc_num] = BankAccount(acc_num, holder, balance)

    elif action == 'remove':
        acc_num = int(input("Enter account number to remove: "))
        if acc_num in accounts:
            del accounts[acc_num]
            print("Account removed.")
        else:
            print("Account not found.")

    elif action == 'done':
        break

    else:
        print("Invalid input. Please enter 'add', 'remove', or 'done'.")

# Total asset calculation
total_assets = 0
for acc in accounts.values():
    total_assets += acc.balance

print(f"\nTotal assets in all accounts: {total_assets}")
