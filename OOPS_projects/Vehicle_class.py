class Vehicle:
    Manufactured_in = "India"

    def __init__(self, body_type, make, colour):
        self.vehicle_body = body_type
        self.vehicle_make = make
        self.vehicle_colour = colour
    def drive(self):
        print("This is a Car!")
class Truck(Vehicle):
    def drive(self):
        print("This is a Truck!")

Car1 = Vehicle('Jeep','Toyota','Black')
Truck1 = Truck('Pickup_Truck','Chevy','Red')
Car1.drive()
Truck1.drive()