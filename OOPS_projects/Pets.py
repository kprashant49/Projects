from tkinter.font import names

class Animal:
    def __init__(self,name):
        self.animal_name = name
        print("Animal constructed!")

    def eat(self):
        raise NotImplementedError("Child class should be implementing this abstract method")

    def move(self):
        print(f"{self.animal_name} is moving")

class Monkey(Animal):
    def __init__(self, name, monkey_age):
        super().__init__(name)
        self.animal_age = monkey_age

    def eat(self):
        print(f"{self.animal_name} eating banana")

    def jump(self):
        print(f"{self.animal_name} is jumping")

class Bird(Animal):

    def eat(self):
        print(f"{self.animal_name} eating seeds")

    def fly(self):
        print(f"{self.animal_name} is flying")


myMonkey = Monkey("Jojo",10)
myMonkey.eat()
myMonkey.move()
myMonkey.jump()

myBird = Bird("Kuku")
myBird.eat()
myBird.move()
myBird.fly()