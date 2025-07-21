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

class Banking:

    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.account_number] = account

    def remove_account(self, account_number):
        if account_number in self.accounts:
            del self.accounts[account_number]

    def get_total_assets(self):
        total_assets = 0
        for account in self.accounts.values():
            total_assets += account.balance
        return total_assets


if __name__ == "__main__":
    account_1 = BankAccount(1, "Prashant", 10000)
    account_2 = BankAccount(2, "Unnati", 20000)

    bank = Banking()
    bank.add_account(account_1)
    bank.add_account(account_2)

    print(f"Total assets before transaction: {bank.get_total_assets()}")

    account_1.deposit(500)
    account_2.withdraw(1000)

    print(f"Total assets after transaction: {bank.get_total_assets()}")
