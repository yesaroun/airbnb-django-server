from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rooms.serializers import (
    RoomDetailSerializer,
    RoomListSerializer,
    AmenitySerializer,
)
from rooms.models import Amenity, Room
from reviews.schemas import review_request_body
from reviews.serializers import ReviewSerializer
from categories.models import Category
from medias.serializers import PhotoSerializer


class Rooms(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Get the list of all rooms",
        responses={200: RoomListSerializer(many=True)},
    )
    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new room",
        request_body=RoomDetailSerializer,
        responses={201: RoomDetailSerializer},
    )
    def post(self, request):
        serializer = RoomDetailSerializer(data=request.data)
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if not category_pk:
                raise ParseError("Category is required.")
            try:
                category = Category.objects.get(pk=category_pk)
                if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                    raise ParseError("The category kind should be 'rooms")
            except Category.DoesNotExist:
                raise ParseError("Category not found")
            try:
                with transaction.atomic():
                    room = serializer.save(owner=request.user, category=category)
                    amenities = request.data.get("amenities")
                    for amenity_pk in amenities:
                        amenity = Amenity.objects.get(pk=amenity_pk)
                        room.amenities.add(amenity)
                    serializer = RoomDetailSerializer(room)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("Amenity not found")
        else:
            return Response(serializer.errors)


class RoomDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Get a specific room by ID",
        responses={200: RoomDetailSerializer},
    )
    def get(self, request, pk):
        room = Room.get_object(pk)
        serializer = RoomDetailSerializer(
            room,
            context={"request": request},
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Put a specific room by ID",
        request_body=RoomDetailSerializer,
        responses={200: RoomDetailSerializer},
    )
    def put(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_room = serializer.save()
            return Response(
                RoomDetailSerializer(updated_room).data,
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific room by ID",
        responses={204: "No Content"},
    )
    def delete(self, request, pk):
        room = self.get_object(pk)
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Room에 해당하는 Reivews Get",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="페이지 번호",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=1,
            )
        ],
        responses={200: ReviewSerializer},
    )
    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = Room.get_object(pk)
        serializer = ReviewSerializer(
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Room에 해당하는 Reivew Post",
        request_body=review_request_body,
        responses={201: ReviewSerializer},
    )
    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                room=Room.get_object(pk),
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data)


class RoomAmenities(APIView):
    @swagger_auto_schema(
        operation_description="Room에 해당하는 Amenities Get",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="페이지 번호",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=1,
            )
        ],
        responses={200: AmenitySerializer},
    )
    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = 3
        start = (page - 1) * page_size
        end = start + page_size
        room = Room.get_object(pk)
        serializer = AmenitySerializer(
            room.reviews.all()[start:end],
            many=True,
        )
        return Response(serializer.data)


class RoomPhotos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk)
        if request.user != room.owner:
            raise PermissionDenied
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
