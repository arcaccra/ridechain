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
    ('Requested', 'Requested'),
    ('Accepted', 'Accepted'),
    ('In Progress', 'In Progress'),
    ('COMPLETED', 'Completed'),
    ('CANCELLED', 'Cancelled'),
)

DRIVER_STATUS_CHOICES = (
    ('', 'Select Driver Status'),
    ('Approved', 'Approved'),
    ('Documents Submitted', 'Documents Submitted'),
    ('Rejected', 'Rejected'),
    ('Under Review', 'Under Review'),
)


IMPRESSION_OPTIONS = (
    ('', 'Select Impression'),
    ('FRIENDLY', 'Friendly'),
    ('PUNCTUAL', 'Punctual'),
    ('SAFE_DRIVER', 'Safe Driver'),
    ('CLEAN_VEHICLE', 'Clean Vehicle'),
    ('GOOD_MUSIC', 'Good Music'),
    ('HELPFUL', 'Helpful'),
    ('RUSHED', 'Rushed'),
    ('UNFRIENDLY', 'Unfriendly'),
    ('DANGEROUS_DRIVER', 'Dangerous Driver'),
    ('DIRTY_VEHICLE', 'Dirty Vehicle'),
    ('BAD_MUSIC', 'Bad Music'),
    ('UNHELPFUL', 'Unhelpful'),
)