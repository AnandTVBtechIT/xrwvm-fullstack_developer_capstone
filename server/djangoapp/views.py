from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel, Dealership, Review
import json
import logging

logger = logging.getLogger(__name__)

def get_cars(request):
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

def logout_user(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except:
        logger.debug("{} is new user".format(username))

    if not username_exist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)

def get_dealerships(request, state="All"):
    if state == "All":
        dealerships = Dealership.objects.all()
    else:
        dealerships = Dealership.objects.filter(state=state)
    dealer_list = [
        {
            "id": d.id,
            "name": d.name,
            "city": d.city,
            "state": d.state,
            "address": d.address,
            "zip_code": d.zip_code,
        }
        for d in dealerships
    ]
    return JsonResponse({"status": 200, "dealers": dealer_list})

def get_dealer_details(request, dealer_id):
    try:
        d = Dealership.objects.get(id=dealer_id)
        data = {
            "id": d.id,
            "name": d.name,
            "city": d.city,
            "state": d.state,
            "address": d.address,
            "zip_code": d.zip_code,
        }
        return JsonResponse({"status": 200, "dealer": data})
    except Dealership.DoesNotExist:
        return JsonResponse({"status": 404, "message": "Not found"})

def get_dealer_reviews(request, dealer_id):
    reviews = Review.objects.filter(dealership_id=dealer_id)
    data = [
        {
            "id": r.id,
            "reviewer_name": r.reviewer_name,
            "review": r.review,
            "sentiment": r.sentiment,
            "created_at": r.created_at,
        }
        for r in reviews
    ]
    return JsonResponse({"status": 200, "reviews": data})

@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"status": 405, "message": "Method not allowed"})
    try:
        body = json.loads(request.body)
        dealership_id = body.get("dealership_id")
        reviewer_name = body.get("reviewer_name")
        review_text = body.get("review")
        sentiment = "positive" if "good" in review_text.lower() else "neutral"
        review = Review.objects.create(
            dealership_id=dealership_id,
            reviewer_name=reviewer_name,
            review=review_text,
            sentiment=sentiment,
        )
        return JsonResponse({"status": 201, "review_id": review.id})
    except Exception as e:
        return JsonResponse({"status": 400, "message": str(e)})
