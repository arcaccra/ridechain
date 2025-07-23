#Driver model with options for vehicle types, colors, and ID types
ID_TYPES = (
    ('', 'Select ID Type'),
    ('NATIONAL_ID', 'National ID'),
    ('PASSPORT', 'Passport'),
    ('DRIVER_LICENSE', 'Driver License'),
    ('VOTER_ID', 'Voter ID'),
)

VEHICLE_COLORS = (
    ('', 'Select Vehicle Color'),
    ('RED', 'Red'),
    ('BLUE', 'Blue'),
    ('GREEN', 'Green'),
    ('BLACK', 'Black'),
    ('WHITE', 'White'),
    ('SILVER', 'Silver'),
    ('YELLOW', 'Yellow'),
    ('ORANGE', 'Orange'),
    ('GRAY', 'Gray'),
)

VEHICLE_TYPES = (
    ('', 'Select Vehicle Type'),
    ('SEDAN', 'Sedan'),
    ('SALOON', 'Saloon'),
    ('MINIVAN', 'Minivan'),
    ('SUV', 'SUV'),
    ('TRUCK', 'Truck'),
    ('VAN', 'Van'),
    ('OTHER', 'Other'),
)

RIDE_STATUSES = (
    ('', 'Select Ride Status'),
    ('REQUESTED', 'Requested'),
    ('PENDING', 'Pending'),
    ('ACCEPTED', 'Accepted'),
    ('ENROUTE_PICKUP', 'Enroute to Pickup'),
    ('IN_PROGRESS', 'In Progress'),
    ('COMPLETED', 'Completed'),
    ('CANCELLED', 'Cancelled'),
)