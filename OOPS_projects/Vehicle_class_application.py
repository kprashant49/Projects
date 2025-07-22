from Vehicle_class import Vehicle, Truck, Motorcycle
car1 = Vehicle("Jeep","Toyota","Black")
truck1 = Truck("Pick-up","Chevy","White")

print(car1.vehicle_make)
print(car1.vehicle_body)
print(car1.vehicle_colour)
print(car1.Manufactured_in)

print(truck1.vehicle_make)
print(truck1.vehicle_body)
print(truck1.vehicle_colour)
print(truck1.Manufactured_in)

print(truck1.get_vehicle_count())
motorcycle1 = Motorcycle("250cc","Honda","Black")
print(motorcycle1.vehicle_make)
print(motorcycle1.vehicle_body)
print(motorcycle1.vehicle_colour)
print(motorcycle1.Manufactured_in)

# Polymorphism
for veh in [truck1, car1, motorcycle1]:
    veh.drive()

def perform_tasks(vehicle_object):
    vehicle_object.drive()

perform_tasks(truck1)
perform_tasks(car1)
perform_tasks(motorcycle1)