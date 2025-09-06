def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def product(a, b):
    return a * b

def divide(a, b=1):
    # if b == 0:
    #     return "Cannot divide by zero"
    # return a / b
    try:
        return a/b
    except ZeroDivisionError:
        return "Cannot divide by zero"

def exponent(a, b):
    return a ** b

def max(a, b):
    if a > b:
        return a
    elif a == b:
        return "Equal"
    return b

def min(a, b):
    if a < b:
        return a
    elif a == b:
        return "Equal"
    return b

def math(a, b, fn=add):
    return fn(a, b)

if __name__ == "__main__":
    parts = input("Enter: num1 num2 [operation]: ").split()

    if len(parts) < 2:
        print("Please enter at least two numbers.")
        exit()

    a, b = map(int, parts[:2])

    if len(parts) == 3:
        op = parts[2].lower()
        fn = {"add": add, "sub": subtract, "exp": exponent, "prod": product, "div": divide, "max": max, "min": min}.get(op)
        if fn is None:
            print("Invalid operation")
            exit()
    else:
        fn = add  # default

    print(math(a, b, fn))