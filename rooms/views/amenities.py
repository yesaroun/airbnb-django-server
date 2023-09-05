from rest_framework.views import APIView
from rest_framework.exceptions import (
    NotFound,
)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from drf_yasg.utils import swagger_auto_schema

from rooms.serializers import (
    AmenitySerializer,
)
from rooms.models import Amenity


class Amenities(APIView):
    @swagger_auto_schema(
        operation_description="Get the list of all amenities",
        responses={200: AmenitySerializer(many=True)},
    )
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new amenity",
        request_body=AmenitySerializer,
        responses={201: AmenitySerializer},
    )
    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data)
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )


class AmenityDetail(APIView):
    @staticmethod
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound

    @swagger_auto_schema(
        operation_description="Get a specific amenity by ID",
        responses={200: AmenitySerializer},
    )
    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a specific amenity by ID",
        request_body=AmenitySerializer,
        responses={200: AmenitySerializer},
    )
    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_amenity = serializer.save()
            return Response(
                AmenitySerializer(updated_amenity).data,
            )
        else:
            return Response(
                serializer.errors,
                status=HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific amenity by ID",
        responses={204: "No Content"},
    )
    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)
