from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from api.serializer import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import json
import os

# Create your views here.


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/test/',
        '/api/get-create-data/'
    ]
    return Response(routes)


# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def testEndPoint(request):
#     if request.method == 'GET':
#         data = f"Congratulation {request.user}, your API just responded to GET request"
#         return Response({'response': data}, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         try:
#             body = request.body.decode('utf-8')
#             data = json.loads(body)
#             if 'text' not in data:
#                 return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
#             text = data.get('text')
#             data = f'Congratulation your API just responded to POST request with text: {text}'
#             return Response({'response': data}, status=status.HTTP_200_OK)
#         except json.JSONDecodeError:
#             return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
#     return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def getCreateData(request):
    if request.method == 'GET':
        json_file_path = './orders-settings.json'

        # Check if the file exists
        if os.path.exists(json_file_path):
            # Read the content of the JSON file
            with open(json_file_path, 'r') as file:
                json_data = json.load(file)
            return JsonResponse(json_data, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'JSON file not found'}, status=status.HTTP_404_NOT_FOUND)
#     elif request.method == 'POST':
#         try:
#             body = request.body.decode('utf-8')
#             data = json.loads(body)
#             if 'text' not in data:
#                 return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
#             text = data.get('text')
#             data = f'Congratulation your API just responded to POST request with text: {text}'
#             return Response({'response': data}, status=status.HTTP_200_OK)
#         except json.JSONDecodeError:
#             return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
#     return Response("Invalid JSON data", status.HTTP_400_BAD_REQUEST)
