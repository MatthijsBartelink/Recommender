from data import CITIES, BUSINESSES, USERS, REVIEWS, TIPS, CHECKINS

import random
import data
import numpy as np

def find_businesses_by_category(categories, city):
    """
    Finds businesses that share categories with the given list of categories.
    Returns a list of tuples, the first value of which is the business, and the
    second value is the number of shared categories.
    """
    businesses = []
    shared_count = 0

    for business in data.BUSINESSES[city]:
        for category in business['categories'].split(', '):
            category = category.strip()
            if category in categories:
                shared_count += 1
        if shared_count > 0:
            businesses.append((business, shared_count))
        shared_count = 0
    return sorted(businesses, key=lambda tup: tup[1], reverse=True)

def find_best_businesses_by_category(user_id, categories, already_found_businesses, city, n):
    """
    Finds the n businesses that share at least one category with the given
    categories, that have the highest predicted rating for the given user.
    """
    with_ratings = [(predict_rating(user_id, business[0]['business_id'], city), business) for business in find_businesses_by_category(categories, city) if business[0]['business_id'] not in already_found_businesses]
    return [val[1][0] for val in sorted(with_ratings[:n], key=lambda tup: tup[0], reverse=True)]

def user_average_score(user_id, city):
    """
    Finds the average score a user gave to businesses in a given city.
    """
    scores = [review['stars'] for review in data.get_reviews(city, user_id=user_id, n=1000000000000)]
    return np.mean(scores)

def cos_similarity(b1, b2, city):
    """
    Takes two dictionaries describing businesses. Returns a similarity score
    between the two businesses.
    """
    if b1 == b2:
        return 1.0

    reviews = REVIEWS[city]
    b1_reviewers = [review['user_id'] for review in reviews if review['business_id'] == b1['business_id']]
    shared_reviewers = [review['user_id'] for review in reviews if review['business_id'] == b2['business_id'] and review['user_id'] in b1_reviewers]

    if len(shared_reviewers) == 0:
        return 0.0

    b1_reviews = {}
    b2_reviews = {}
    for review in reviews:
            if review['user_id'] in shared_reviewers:
                if review['business_id'] == b1['business_id']:
                    b1_reviews[review['user_id']] = review['stars']
                elif review['business_id'] == b2['business_id']:
                    b2_reviews[review['user_id']] = review['stars']

    nom = 0.0
    for reviewer in shared_reviewers:
        mean_score = user_average_score(reviewer, city)
        b1_review = b1_reviews[reviewer] - mean_score
        b2_review = b2_reviews[reviewer] - mean_score
        nom += b1_review * b2_review

    return nom / (len(shared_reviewers)*2)


def predict_rating_naive(user_id, business_id, city):
    """
    Takes a userId describing a user, a dict describing a business and a dict
    describing a city. Returns a predicted rating for the given business in the
    given city by the given user.
    """
    businesses = BUSINESSES[city]
    reviews = REVIEWS[city]
    user_reviewed_businesses = []
    user_reviews = {}

    for review in reviews:
        if review['user_id'] == user_id:
            user_reviewed_businesses.append(review['business_id'])
            user_reviews[review['business_id']] = review['stars']

    total_rating = 0.0
    total_weight = 0.0
    for b2 in businesses:
        shared_similarity = cos_similarity(data.get_business(city, business_id), b2, city)
        if shared_similarity > 0.0:
            if business_id in user_reviewed_businesses:
                total_rating += user_reviews[business_id]
                total_weight += shared_similarity
            else:
                total_rating += data.get_business(city, business_id)['stars']
                total_weight += shared_similarity

    return total_rating/total_weight

def predict_rating(user_id, business_id, city):
    """
    Takes a userId describing a user, a dict describing a business and a dict
    describing a city. Returns a predicted rating for the given business in the
    given city by the given user.
    """
    reviews = REVIEWS[city]
    user_reviewed_businesses = []
    user_reviews = {}

    for review in reviews:
        if review['user_id'] == user_id:
            user_reviewed_businesses.append(review['business_id'])
            user_reviews[review['business_id']] = review['stars']

    total_rating = 0.0
    total_weight = 0.0
    for b2 in user_reviewed_businesses:
        shared_similarity = cos_similarity(data.get_business(city, business_id), data.get_business(city, b2), city)
        if shared_similarity > 0.0:
            total_rating += user_reviews[b2]
            total_weight += shared_similarity

    total_rating += data.get_business(city, business_id)['stars']
    total_weight += 1.0

    return total_rating/total_weight,


def recommend(user_id=None, business_id=None, city=None, n=10):
    """
    Returns n recommendations as a list of dicts.
    Optionally takes in a user_id, business_id and/or city.
    A recommendation is a dictionary in the form of:
        {
            business_id:str
            stars:str
            name:str
            city:str
            adress:str
        }
    """
    if not city:
        city = random.choice(CITIES)


    # business_id = random.choice(BUSINESSES[city])['business_id']
    # user_id = random.choice(USERS[city])['user_id']

    businesses_to_recommend = []

    if user_id and business_id:
        # If we have both a user id and a business id, we can find the
        # businesses with the highest predicted rating that are still somewhat
        # similar to the given business.
        similarity_list = [(cos_similarity(data.get_business(city, business_id), b2, city), b2) for b2 in list(BUSINESSES[city]) if b2 != data.get_business(city, business_id)]
        neighboorhood = [tuple for tuple in similarity_list if tuple[0] > 0.0 and tuple[1]['business_id'] != business_id]
        predicted_ratings = sorted([(predict_rating(user_id, tuple[1]['business_id'], city), tuple[1]) for tuple in neighboorhood], key=lambda tup: tup[0], reverse=True)
        similar_businesses = [tuple[1] for tuple in predicted_ratings][:n//2]

        # Fill out the rest of the values with first businesses that share a
        # category with the given business, or if too few of those can be found
        # simply use the highest rated businesses.
        already_found_businesses = similar_businesses.copy()
        already_found_businesses.append(data.get_business(city, business_id))
        already_found_businesses = [business['business_id'] for business in already_found_businesses]
        categorically_similar_businesses = find_best_businesses_by_category(user_id, data.get_business(city, business_id)['categories'].split(', '), already_found_businesses, city, n-len(similar_businesses))
        if len(similar_businesses) + len(categorically_similar_businesses) < n:
            categorically_similar_businesses.append(sorted([b for b in list(BUSINESSES[city])], key=lambda val: val['stars'], reverse=True)[:n-len(similar_businesses)-len(categorically_similar_businesses)])
        for business in categorically_similar_businesses:
            similar_businesses.append(business)

        # Randomly shuffle the businesses, to intersperse the two types of
        # suggestions.
        random.shuffle(similar_businesses)
        businesses_to_recommend = similar_businesses
    elif business_id:
        # If we only have a business id, find the most similar businesses based
        # on user reviews and add the businesses that share the most categories.
        # If not enough businesses can be found that way, simply use well rated
        # ones.
        similarity_list = [(cos_similarity(data.get_business(city, business_id), b2, city), b2) for b2 in list(BUSINESSES[city]) if b2 != data.get_business(city, business_id)]
        neighboorhood = [tuple for tuple in similarity_list if tuple[0] > 0.0]
        similar_businesses = [business[1] for business in sorted(neighboorhood, key=lambda tup: tup[0], reverse=True)][:n//2]
        categorically_similar_businesses = find_businesses_by_category(data.get_business(city, business_id)['categories'].split(', '), city)[:n-len(similar_businesses) + 1]
        categorically_similar_businesses = [val[0] for val in categorically_similar_businesses if val[0]['business_id'] != business_id]
        if len(similar_businesses) + len(categorically_similar_businesses) < n:
            for val in sorted([b for b in list(BUSINESSES[city])], key=lambda val: val['stars'], reverse=True)[:n-len(similar_businesses)-len(categorically_similar_businesses)]:
                categorically_similar_businesses.append(val)

        for business in categorically_similar_businesses:
            print(business)
            similar_businesses.append(business)

        # Randomly shuffle the businesses, to intersperse the two types of
        # suggestions.
        random.shuffle(similar_businesses)
        businesses_to_recommend = similar_businesses
    elif user_id:
        # Predict the rating that the givne user will give each business, then
        # return the businesses with the highest predicted ratings.
        predicted_ratings = [(predict_rating(user_id, business['business_id'], city), business) for business in list(BUSINESSES[city])]
        sorted_ratings = sorted(predicted_ratings, key=lambda tup: tup[0], reverse=True)
        businesses_to_recommend = [val[1] for val in sorted_ratings][:n]
    else:
        businesses_to_recommend = sorted([b for b in list(BUSINESSES[city])], key=lambda val: val['stars'], reverse=True)[:n]

    # Restructure the found businesses into correct recommendations.
    recommendations = []
    for business in businesses_to_recommend:
        recommendation = {}
        recommendation['business_id'] = business['business_id']
        recommendation['stars'] = str(business['stars'])
        recommendation['name'] = business['name']
        recommendation['city'] = business['city']
        recommendation['adress'] = business['address']
        recommendations.append(recommendation)

    return recommendations
