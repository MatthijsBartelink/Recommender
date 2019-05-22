import data
import recommender
import random
import timeit

city = 'westlake'
# print(len(data.BUSINESSES[city]))
# def testsimilarity():
#     for b1 in data.BUSINESSES[city]:
#         for b2 in data.BUSINESSES[city]:
#             if b2 == b1:
#                 continue
#
# print(timeit.timeit(testsimilarity, number=1))


categories = []

for city in data.CITIES:
    for business in data.BUSINESSES[city]:
        for category in business['categories'].split(', '):
            if category not in categories:
                categories.append(category)

print(categories)

# print(recommender.find_businesses_by_categories(['Metal Fabricators', 'Jazz & Blues', 'Retirement Homes', 'Airports''Massage Therapy', 'Reflexology', 'Halotherapy', 'Acupuncture''Child Care & Day Care', 'Veterinarians', 'Do-It-Yourself Food', 'Tennis', 'Septic Services', 'Utilities', 'Rugs', 'Hot Tub & Pool', 'Pool & Hot Tub Service', 'Photography Stores & Services', 'Title Loans', 'Bridal', 'Pet Adoption', 'Pet Boarding', 'Dry Cleaning & Laundry', 'Laundry Services', 'Embroidery & Crochet', 'Screen Printing', 'Engraving', 'Olive Oil', 'Herbs & Spices', 'Community Service/Non-Profit', 'ATV Rentals/Tours', 'Trailer Rental', 'RV Rental', 'Steakhouses', 'American (New)', 'Movers', 'Fitness/Exercise Equipment', 'Permanent Makeup', 'Tattoo', 'Piercing', 'Mattresses', 'Nightlife'], city)[0])
