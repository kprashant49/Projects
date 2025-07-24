from matplotlib.style.core import library


class BooksInventory:

    def __init__(self, book_name, author_name, quantity=0):
        self.name = book_name
        self.author = author_name
        self.quantity = quantity

    def add_inventory(self, stock_inward):
        self.quantity += stock_inward

    def sales(self, stock_sold):
        if stock_sold > self.quantity:
            print(f"Currently we have only stock of {self.quantity} books.")
        else:
            self.quantity -= stock_sold
            return stock_sold
    def __str__(self):
        return f"Book {self.name} by {self.author} : Stock_remaining {self.quantity}"

class Library:

    def __init__(self):
        self.books = {}

    def add_book(self,book):
        self.books[book.name] = book

    def remove_book(self,book_name):
        if book_name in self.books:
            del self.books[book_name]

    def get_total_stock(self):
        total_stock = 0
        for book in self.books.values():
            total_stock += book.quantity
        return total_stock

if __name__ == "__main__":
    book_1 = BooksInventory("The Alchemist", "Paulo Coelho",5)
    book_2 = BooksInventory("The Monk who sold his Ferrari", "Robin Sharma", 10)
    book_3 = BooksInventory("The Da Vinci Code", "Dan Brown", 1)

    Library = Library()

    Library.add_book(book_1)
    Library.add_book(book_2)
    Library.add_book(book_3)

    print(f"Total stock before transaction: {Library.get_total_stock()}")

    book_1.sales(2)
    book_2.sales(4)

    print(f"Total stock after transaction: {Library.get_total_stock()}")

    for stock in Library.books.keys():
        print(stock)

    for qty in Library.books.values():
        print(qty)

    print(Library.books)