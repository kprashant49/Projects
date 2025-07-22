class Vehicle:
    Manufactured_in = "India"
    vehicle_counter = 0

    def __init__(self, body_type, make, colour):
        self.vehicle_body = body_type
        self.vehicle_make = make
        self.vehicle_colour = colour
        Vehicle.vehicle_counter += 1

    def drive(self):
        print(f"Driving new car: {self.vehicle_make} {self.vehicle_body}!")

    def get_vehicle_count(self):
        return Vehicle.vehicle_counter

# inheritance (Sub_class)
class Truck(Vehicle):
    # Overriding the constructor
    def drive(self):
        print(f"Driving new truck: {self.vehicle_make} {self.vehicle_body}!")

class Motorcycle(Vehicle):
    def drive(self):
        print(f"Riding new motorbike: {self.vehicle_make} {self.vehicle_body}!")

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
print(Car1.get_vehicle_count())
Car2.drive()