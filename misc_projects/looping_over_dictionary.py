def total_donations(donations):

    # Method 1
    # total_donations = 0
    #
    # for donation in donations.values():
    #     total_donations += donation

    # Method 2
    # total_donations = sum(donation for donation in donations.values())

    # Method 3
    total_donations = sum(donations.values())

    return (total_donations)

donations = dict(sam=25.0, lena=88.99, chuck=13.0, linus=99.5, stan=150.0, lisa=50.25, harrison=10.0)

print(total_donations(donations))