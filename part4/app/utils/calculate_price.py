# app/utils/calculate_price.py

from datetime import datetime


def calculate_price(place, start_date, end_date, guest_count):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    number_of_nights = (end_date - start_date).days

    if number_of_nights <= 0:
        raise ValueError("End date must be later than start date.")

    total_price = place.price * number_of_nights * guest_count
    return total_price
