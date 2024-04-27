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
from api.models import Product
from api.models import Order
from django.core import serializers
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
        all_product = Product.objects.all()
        product_json = serializers.serialize('json', all_product)
        return JsonResponse(product_json,safe=False, status=status.HTTP_200_OK)
def getListData(request):
    if request.method == 'GET':
        all_order = Order.objects.all()
        order_json = serializers.serialize('json', all_order)
        return JsonResponse(order_json,safe=False, status=status.HTTP_200_OK)
      