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
import cairosvg
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET  # For SVG parsing and modification
from lxml import etree
import io
import svgwrite
import ezdxf
from svgpathtools import svg2paths
import xml.etree.ElementTree as ET
import json
import time
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from api.models import Order
from api.models import Product
from django.core import serializers
from django.http import JsonResponse

def generate_chart_and_save_to_pdf(data, filename):
    # Prepare data for chart
    categories = [d[0] for d in data]
    values = [d[1] for d in data]

    # Create a bar chart with four columns
    fig, ax = plt.subplots()
    ax.bar(categories, values, color=['red', 'green', 'blue', 'orange'])
    ax.set_xlabel('Categories')
    ax.set_ylabel('Values')
    ax.set_title('Data Chart')

    # Save the chart as a PNG
    plt.savefig('chart.png', bbox_inches='tight')
    c = canvas.Canvas(filename, pagesize=letter)

    # Add text to the PDF
    c.drawString(100, 750, "asdfgdbherw wdqwsfdvasd")

    # Add image to the PDF
    img = Image.open("chart.png")
    width, height = img.size
    aspect_ratio = height / width
    desired_width = 400  # Adjust the width as needed
    desired_height = int(desired_width * aspect_ratio)
    c.drawImage("chart.png", 100, 100, width=desired_width, height=desired_height)
    c.save()
    # # Create a PDF document
    # doc = SimpleDocTemplate(filename)
    # styles = getSampleStyleSheet()
    # style = styles["Normal"]
    # centered_style = ParagraphStyle(name='Centered', parent=style, alignment=1)

    # # Add chart to PDF
    # story = []
    # story.append(Paragraph("Data Chart", centered_style))
    # story.append(Spacer(1, inch * 0.5))
    # story.append(Paragraph("Below is the chart:", centered_style))
    # story.append(Spacer(1, inch * 0.2))
    # story.append(Paragraph('<img src="chart.png" width="500" height="1400"/>', centered_style))
    # story.append(Spacer(1, inch))

    # # Add data table to PDF
    # data_table = [["Category", "Value"]]
    # for d in data:
    #     data_table.append([str(d[0]), str(d[1])])

    # t = Table(data_table)
    # t.setStyle([
    #     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    #     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    #     ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
    # ])
    # story.append(Paragraph("Data Table", centered_style))
    # story.append(Spacer(1, inch * 0.2))
    # story.append(t)
    # plt.close()


def get_color_percentage(image_path):
    # Open the image
    img = Image.open(image_path)
    
    # Initialize counters for CMYK colors
    cyan_count = 0
    magenta_count = 0
    yellow_count = 0
    black_count = 0
    
    # Get pixel data
    pixels = img.load()
    width, height = img.size
    
    # Loop through each pixel
    for y in range(height):
        for x in range(width):
            # Get RGB values of the pixel
            r, g, b = pixels[x, y]
            
            # Convert RGB to CMYK
            c = 1 - r / 255.0
            m = 1 - g / 255.0
            y = 1 - b / 255.0
            
            # Find the maximum value and calculate black
            k = min(c, m, y)
            c = (c - k) / (1 - k)
            m = (m - k) / (1 - k)
            y = (y - k) / (1 - k)
            
            # Increment counters based on CMYK values
            cyan_count += c
            magenta_count += m
            yellow_count += y
            black_count += k
            
    # Calculate percentages
    total_pixels = width * height
    cyan_percentage = (cyan_count / total_pixels) * 100
    magenta_percentage = (magenta_count / total_pixels) * 100
    yellow_percentage = (yellow_count / total_pixels) * 100
    black_percentage = (black_count / total_pixels) * 100
    
    # Return the result
    return {
        'Cyan': cyan_percentage,
        'Magenta': magenta_percentage,
        'Yellow':  yellow_percentage,
        'Black': black_percentage
    }

def add_svg_to_image(background_image_path, svg_file_path, output_image_path):
    # Open the background image
    background_image = Image.open(background_image_path)

    # Open the SVG file and read its content
    with open(svg_file_path, "r") as svg_file:
        svg_content = svg_file.read()
    # Convert SVG content to PNG
    svg_png = cairosvg.svg2png(bytestring=svg_content)

    # Convert PNG data to PIL Image
    svg_image = Image.open(io.BytesIO(svg_png))

    # Create a new image with the same dimensions as the background image
    composite_image = Image.new("RGBA", background_image.size)

    # Composite the background image onto the new image
    composite_image.paste(background_image, (0, 0))

    # Composite the SVG image onto the new image
    composite_image.paste(svg_image, (0, 0), svg_image)

    # Save the composite image
    composite_image.save(output_image_path)
class GenerateOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]



    def post(self, request):
        try:
            json_data_str = request.POST['formData']
            form_data = json.loads(json_data_str)
            print(form_data)
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
            current_time_unix = str(int(time.time()))
            generated_filename = current_time_unix + 'generated_background.png'
            generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            os.makedirs(os.path.dirname(generated_filepath), exist_ok=True)  # Ensure generated directory exists
            
            svg_path = os.path.join(settings.MEDIA_ROOT, 'clothesdata/', form_data.get('model', '') + "/" + form_data.get('model', '') + ".svg")
            tree = ET.parse(svg_path)
            root = tree.getroot()
            width = root.get('width')
            height = root.get('height')
            square_size = 50  # Adjust this to control square size
            num_squares_x = int(int(width) // square_size) + 1 # Calculate number of squares horizontally
            num_squares_y = int(int(height) // square_size) + 1 # Calculate number of squares vertically
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
            # Open the DXF file
            generated_with_cut_filename = current_time_unix + 'generated_with_cut.png'
            generated_with_cut = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_with_cut_filename)
            add_svg_to_image(generated_filepath, svg_path, generated_with_cut)
            print(get_color_percentage(generated_filepath))
            generated_pdf_filename = current_time_unix + "output.pdf"
            generated_pdf = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_pdf_filename)
            data = [("A", 10), ("B", 20), ("C", 15), ("D", 25)]
            generate_chart_and_save_to_pdf(data, generated_pdf)
            return Response({'response': 'Images uploaded successfully',
                             'generated_filename': generated_filename,
                             'generated_pdf_filename': generated_pdf_filename,
                             'generated_with_cut_filename': generated_with_cut_filename, 
                             'common_color_data': common_color_data, 
                             'color_data': color_data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            form_data = json.loads(request.POST['formData'])
            model = form_data['model']
            product = Product.objects.get(title=model)

            Order.objects.create(
                title=form_data['title'],
                description=form_data['description'],
                quantity=form_data['quantity'],  # Assuming quantity is 10
                cost=form_data['cost'], # Assuming cost is 100
                size=form_data['size'],   # Assuming size is XL
                model=product,  # Assign the Product object to the model field
                status='CREATED',  # Assuming status is pending
                cutPath=form_data['generatedWithCut'],  # Assuming cutPath
                backgroundPath=form_data['generated'],  # Assuming backgroundPath
                pdfPath=form_data['pdf'],  # Assuming pdfPath
                creator=request.user  # Assuming you have access to the request object and want to assign the current user as the creator
            )
            return Response({'response': 'Order ' + form_data['title'] + " created"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            form_data = json.loads(request.POST['deleteData'])
            order_id = form_data['id']  # Assuming you pass orderId for deletion
            order = Order.objects.get(pk=order_id)
            order.delete()
            all_order = Order.objects.all()
            order_json = serializers.serialize('json', all_order)
            return JsonResponse(order_json,safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            form_data = json.loads(request.POST['formData'])
            model = form_data['model']
            product = Product.objects.get(title=model)
            order_id = form_data['id']  # Assuming you pass orderId for update
            order = Order.objects.get(pk=order_id)
            order.title = form_data['title']
            order.description = form_data['description']
            order.quantity = form_data['quantity']
            order.cost = form_data['cost']
            order.size = form_data['size']
            order.model = product
            order.cutPath = form_data['generatedWithCut']
            order.backgroundPath = form_data['generated']
            order.pdfPath = form_data['generated']
            order.save()
            all_order = Order.objects.all()
            order_json = serializers.serialize('json', all_order)
            return JsonResponse(order_json,safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateStatusOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            form_data = json.loads(request.POST['statusData'])
            order_id = form_data['id']  # Assuming you pass orderId for update
            new_status = form_data['value']  # Assuming you pass new status for update
            order = Order.objects.get(pk=order_id)
            order.status = new_status
            order.save()
            all_order = Order.objects.all()
            order_json = serializers.serialize('json', all_order)
            return JsonResponse(order_json,safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetUpdateOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            form_data = json.loads(request.POST['updateData'])
            order_id = form_data['id']  # Assuming you pass orderId for update
            order = Order.objects.get(pk=order_id)
            print(order)
            order_json = serializers.serialize('json', [order])
            return JsonResponse(order_json,safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    # path('test/', views.testEndPoint, name='test'),
    path('', views.getRoutes),
    path('generate-order/', GenerateOrder.as_view()),
    path('create-order/', CreateOrder.as_view()),
    path('delete-order/', DeleteOrder.as_view()),
    path('update-status-order/', UpdateStatusOrder.as_view()),
    path('update-order/', UpdateOrder.as_view()),
    path('get-update-order/', GetUpdateOrder.as_view()),
    path('get-create-data/', views.getCreateData, name="get-create-data"),
    path('get-list-data/', views.getListData, name="get-list-data")
]



            # output_image = Image.new("RGB", (1000, 500))

            # mask_image = Image.new("L", output_image.size, 0)
            # draw = ImageDraw.Draw(mask_image)
            # shape_coordinates = [
            #     (0, 0),  # Left shoulder
            #     (850, 0),  # Right shoulder
            #     (970, 100),  # Right bottom
            #     (1000, 200),  # Right bottom
            #     (1000, 300),  # Right bottom
            #     (970, 400),  # Right bottom
            #     (850, 500),  # Right shoulder
            #     (0, 500),  # Left shoulder
            #     (0, 410),  # Left shoulder
            #     (700, 410),  # Left shoulder
            #     (0, 380),  # Left shoulder
            #     (0, 120),  # Left shoulder
            #     (700, 90),  # Left shoulder
            #     (0, 90)  # Left shoulder

            # ]

            # # Draw the shape onto the mask, using scaled coordinates
            # scaled_coordinates = [(x * 1000 / img.width, y * 500 / img.height) for x, y in shape_coordinates]
            # draw.polygon(scaled_coordinates, fill=255)

            # # Paste the fill image onto the output image using the mask
            # output_image.paste(img, (0, 0), mask=mask_image)

            # # Save the output image as PNG
            # generated_filename = 'uniform2.jpg'
            # generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            # output_image.save(generated_filepath, "PNG")

            # output_image = Image.new("RGB", (1000, 500))

            # mask_image = Image.new("L", output_image.size, 0)
            # draw = ImageDraw.Draw(mask_image)
            # shape_coordinates = [
            # (0, 0), (1000, 100), (1000, 400), (0, 500),( 0, 300), (800, 250), (0,200)  # Coordinates relative to image size
            # ]

            # # Draw the shape onto the mask, using scaled coordinates
            # scaled_coordinates = [(x * 1000 / img.width, y * 500 / img.height) for x, y in shape_coordinates]
            # draw.polygon(scaled_coordinates, fill=255)

            # # Paste the fill image onto the output image using the mask
            # output_image.paste(img, (0, 0), mask=mask_image)

            # # Save the output image as PNG
            # generated_filename = 'uniform.jpg'
            # generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            # output_image.save(generated_filepath, "PNG")