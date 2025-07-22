class Vehicle:
    Manufactured_in = "India"

    def __init__(self, body_type, make, colour):
        self.vehicle_body = body_type
        self.vehicle_make = make
        self.vehicle_colour = colour
    def drive(self):
        print(f"Driving new car: {self.vehicle_make} {self.vehicle_body}!")
class Truck(Vehicle):
    def drive(self):
        print(f"Driving new truck: {self.vehicle_make} {self.vehicle_body}!")

Car1 = Vehicle('Jeep','Toyota','Black')
Car1.engine = '4-cylinder'  # we can assign a variable out of a class specific to an instance
Car2 = Vehicle('Sedan','Honda','White')
Truck1 = Truck('Pickup_Truck','Chevy','Red')
Car1.drive()
Truck1.drive()
print(Car2.vehicle_body)
print(Car2.vehicle_make)
print(Car2.Manufactured_in)
print(Car2.vehicle_colour)
print(Car1.engine)
Car2.drive()