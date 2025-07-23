class BankAccount:

    def __init__(self, account_number, account_holder, balance=0):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            print(f"Insufficient balance. Current balance: {self.balance}")
        else:
            self.balance -= amount
            return amount

    def __str__(self):
        return f"Account {self.account_number} - {self.account_holder}: ₹{self.balance}"


class Banking:

    def __init__(self):
        self.accounts = {}
        # This is a dictionary that maps account numbers to BankAccount objects

    def add_account(self, account):
        self.accounts[account.account_number] = account
        # This is Key based addition and addition of account number itself as a key in account dictionary

    def remove_account(self, account_number):
        if account_number in self.accounts:
            del self.accounts[account_number]
            # This is Key based deletion

    def get_total_assets(self):
        total_assets = 0
        for account in self.accounts.values():
            total_assets += account.balance
        return total_assets


if __name__ == "__main__":
    account_1 = BankAccount(9820, "Prashant", 10000)
    account_2 = BankAccount(9819, "Unnati", 20000)

    bank = Banking()

    # Creating an object of the Banking class. It calls the __init__ method of the Banking class and initializes the accounts attribute as an empty dictionary.
    # self.accounts = {}, which initializes an empty dictionary to store bank accounts.
    # Assigns the newly created Banking object to the variable bank to use bank.add_account(...), bank.get_total_assets() methods.
    # It’s like saying: “Give me a new banking system where I can store accounts.” and bank becomes your handle to interact with that system.

    bank.add_account(account_1)
    bank.add_account(account_2)

    print(f"Total assets before transaction: {bank.get_total_assets()}")

    account_1.deposit(500)
    account_2.withdraw(1000)

    print(f"Total assets after transaction: {bank.get_total_assets()}")

    for acc in bank.accounts.keys():
        print(acc)

    for bal in bank.accounts.values():
        print(bal)

    print(bank.accounts)