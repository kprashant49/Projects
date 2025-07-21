from tkinter.font import names


class Animal:
    def __init__(self):
        print("Animal constructed!")

    def eat(self):
        print("Animal eating")

    def move(self):
        print("Animal moving")

class Dog(Animal):
    def __init__(self,dog_name,dog_age):
        Animal.__init__(self)
        self.animalname = dog_name
        self.animalage = dog_age

    def move(self):
        print("Dog is moving")


myDog = Dog("Simba",10)
myDog.eat()
myDog.move()