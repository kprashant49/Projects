def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def exponent(a, b):
    return a ** b

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
        fn = {"add": add, "sub": subtract, "exp": exponent}.get(op)
        if fn is None:
            print("Invalid operation")
            exit()
    else:
        fn = add  # default

    print(math(a, b, fn))