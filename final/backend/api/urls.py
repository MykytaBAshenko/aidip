from django.urls import path
from . import views
import random
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser  # Allow multipart data
from django.conf import settings  # Access project settings
import os
from rest_framework.response import Response
from rest_framework import status
from colorthief import ColorThief
from PIL import Image, ImageDraw

class UploadImagesView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            images = request.FILES.getlist('images')

            if not images:
                return Response({'error': 'No images uploaded'}, status=status.HTTP_400_BAD_REQUEST)

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/')

            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            color_data = []
            for image in images:
                filename = image.name
                filepath = os.path.join(upload_dir, filename)

                # Save image to file system
                with open(filepath, 'wb') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                # Analyze colors using colorthief
                color_thief = ColorThief(filepath)
                dominant_colors = color_thief.get_palette(color_count=10)
                color_data.append({
                    'filename': filename,
                    'colors': list(dominant_colors)  # Convert tuple to list for response
                })
            
            common_color_data = []
            for i in range(len(color_data[0]['colors'])):  # Iterate over color indices
                color_values = [item['colors'][i] for item in color_data]  # Get colors at the same index
                middle_value = sorted(color_values)[len(color_values) // 2]
                common_color_data.append(middle_value)

            generated_filename = 'generated_image.jpg'
            generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            os.makedirs(os.path.dirname(generated_filepath), exist_ok=True)  # Ensure generated directory exists

            # Create a square image with common colors
            square_size = 20  # Adjust this to control square size
            num_squares_x = int(1000 // square_size)  # Calculate number of squares horizontally
            num_squares_y = int(500 // square_size)  # Calculate number of squares vertically
            img = Image.new('RGB', (num_squares_x * square_size, num_squares_y * square_size))  # Create square image
            pixels = img.load()

            for y in range(num_squares_y):
                for x in range(num_squares_x):
                    random_color = random.choice(common_color_data)  # Choose a random color

                    # Fill entire square with the randomly chosen color
                    for y_offset in range(square_size):
                        for x_offset in range(square_size):
                            current_y = y * square_size + y_offset
                            current_x = x * square_size + x_offset
                            if 0 <= current_y < img.height and 0 <= current_x < img.width:
                                pixels[current_x, current_y] = random_color

            img.save(generated_filepath)

            output_image = Image.new("RGB", (1000, 500))

            mask_image = Image.new("L", output_image.size, 0)
            draw = ImageDraw.Draw(mask_image)
            shape_coordinates = [
            (0, 0), (1000, 100), (1000, 400), (0, 500),( 0, 300), (800, 250), (0,200)  # Coordinates relative to image size
            ]

            # Draw the shape onto the mask, using scaled coordinates
            scaled_coordinates = [(x * 1000 / img.width, y * 500 / img.height) for x, y in shape_coordinates]
            draw.polygon(scaled_coordinates, fill=255)

            # Paste the fill image onto the output image using the mask
            output_image.paste(img, (0, 0), mask=mask_image)

            # Save the output image as PNG
            generated_filename = 'uniform.jpg'
            generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            output_image.save(generated_filepath, "PNG")



            output_image = Image.new("RGB", (1000, 500))

            mask_image = Image.new("L", output_image.size, 0)
            draw = ImageDraw.Draw(mask_image)
            shape_coordinates = [
                (0, 0),  # Left shoulder
                (850, 0),  # Right shoulder
                (970, 100),  # Right bottom
                (1000, 200),  # Right bottom
                (1000, 300),  # Right bottom
                (970, 400),  # Right bottom
                (850, 500),  # Right shoulder
                (0, 500),  # Left shoulder
                (0, 410),  # Left shoulder
                (700, 410),  # Left shoulder
                (0, 380),  # Left shoulder
                (0, 120),  # Left shoulder
                (700, 90),  # Left shoulder
                (0, 90)  # Left shoulder

            ]

            # Draw the shape onto the mask, using scaled coordinates
            scaled_coordinates = [(x * 1000 / img.width, y * 500 / img.height) for x, y in shape_coordinates]
            draw.polygon(scaled_coordinates, fill=255)

            # Paste the fill image onto the output image using the mask
            output_image.paste(img, (0, 0), mask=mask_image)

            # Save the output image as PNG
            generated_filename = 'uniform2.jpg'
            generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            output_image.save(generated_filepath, "PNG")

            return Response({'response': 'Images uploaded successfully', 'common_color_data': common_color_data, 'color_data': color_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('test/', views.testEndPoint, name='test'),
    path('', views.getRoutes),
    path('upload-images/', UploadImagesView.as_view())
]
