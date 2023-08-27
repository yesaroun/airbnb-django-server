from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rooms.serializers import (
    RoomDetailSerializer,
    RoomListSerializer,
)
from rooms.models import Amenity, Room
from categories.models import Category


class Rooms(APIView):
    @swagger_auto_schema(
        operation_description="Get the list of all rooms",
        responses={200: RoomListSerializer(many=True)}
    )
    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(all_rooms, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new room",
        request_body=RoomDetailSerializer,
        responses={201: RoomDetailSerializer}
    )
    def post(self, request):
        if request.user.is_authenticated:
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
        else:
            raise NotAuthenticated


class RoomDetail(APIView):
    @staticmethod
    def get_object(pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    @swagger_auto_schema(
        operation_description="Get a specific room by ID",
        responses={200: RoomDetailSerializer}
    )
    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Put a specific room by ID",
        request_body=RoomDetailSerializer,
        responses={200: RoomDetailSerializer}
    )
    def put(self, request, pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
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
        operation_description="Delete a spcific room by ID",
        responses={204: "No Content"}
    )
    def delete(self, request, pk):
        room = self.get_object(pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if room.owner != request.user:
            raise PermissionDenied
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)