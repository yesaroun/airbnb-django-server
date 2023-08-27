from django.urls import path

from rooms import views

urlpatterns = [
    path("", views.Rooms.as_view()),
    path("<int:pk>", views.RoomDetail.as_view()),
    path("<int:pk>/reivews", views.RoomReviews().as_view()),
    path("amenities/", views.Amenities.as_view()),
    path("amenities/<int:pk>", views.AmenityDetail.as_view()),
]
