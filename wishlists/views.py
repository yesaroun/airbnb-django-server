from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from wishlists.models import Wishlist
from wishlists.serializers import WishlistSerializer
from rooms.models import Room


class Wishlists(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the list of all wishlists",
        responses={200: WishlistSerializer(many=True)},
    )
    def get(self, request):
        all_wishlists = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(
            all_wishlists,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new wishlist",
        request_body=WishlistSerializer,
        responses={201: WishlistSerializer},
    )
    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            wishlist = serializer.save(user=request.user)
            serializer = WishlistSerializer(wishlist)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class WishlistDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound

    @swagger_auto_schema(
        operation_description="Get a specific wishlist by ID",
        responses={200: WishlistSerializer},
    )
    def get(self, requst, pk):
        wishlist = self.get_object(pk, requst.user)
        serializer = WishlistSerializer(
            wishlist,
            context={"request": requst},
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Delete a specific wishlist by ID",
        responses={204: "No Content"},
    )
    def delete(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        wishlist.delete()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Put a specific wishlist by ID",
        request_body=WishlistSerializer,
        responses={200: WishlistSerializer},
    )
    def put(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(
            wishlist,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            wishlist = serializer.save()
            serializer = WishlistSerializer(
                wishlist,
                context={"request": request},
            )
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class WishlistToggle(APIView):
    def get_list(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound

    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    @swagger_auto_schema(
        operation_description="room 추가 또는 제거 Put",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "room_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Room의 ID"),
            }
        ),
        responses={
            200: "성공",
            400: "잘못된 요청",
            404: "Wishlist 또는 Room을 찾을 수 없음",
        }
    )
    def put(self, request, pk, room_pk):
        wishlist = self.get_list(pk, request.user)
        room = self.get_room(room_pk)
        if wishlist.rooms.filter(pk=room.pk).exists():
            wishlist.rooms.remove(room)
        else:
            wishlist.rooms.add(room)
        return Response(status=status.HTTP_200_OK)
