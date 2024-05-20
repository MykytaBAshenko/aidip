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
import numpy as np
import csv
SQUARES_IN_WIDTH = 200
def generate_chart_and_save_to_pdf(data,form_data,pdf_size_data, filename):
    # Prepare data for chart
    print(form_data)
    print(pdf_size_data)

    categories = [c[0]+"/"+str(v)+"%" for c, v in data.items()]
    values = [v for c, v in data.items()]

    # Create a bar chart with four columns
    fig, ax = plt.subplots()
    ax.bar(categories, values, color=['cyan', 'magenta', 'yellow', 'black'])
    ax.set_xlabel('Paint')
    ax.set_ylabel('%')
    ax.set_title('Color percentage')

    # Save the chart as a PNG
    plt.savefig('chart.png', bbox_inches='tight')
    c = canvas.Canvas(filename, pagesize=letter)

    # Add text to the PDF
    c.drawString(100, 750, "Order title: " + form_data['title'])
    c.drawString(400, 750, "Order model: " + form_data['model'])
    c.drawString(100, 710, "Order description: " + form_data['description'])
    c.drawString(100, 670, "Order size: " + form_data['size'])
    c.drawString(250, 670, "Quantity: " + str(form_data['quantity']))
    c.drawString(400, 670, "Cost: " + str(form_data['cost']))
    c.drawString(100, 630, "COLOR/PAINT ANALYSIS")
    area_for_m = float((pdf_size_data['height_in_mm']/1000 * pdf_size_data['width_in_mm']) / 1000)
    c.drawString(100, 590, "Area in m^2 for 1 paint: " + str(pdf_size_data['width_in_mm']) + "mm" + " * " + str(pdf_size_data['height_in_mm']) + "mm"+ " = " + str(area_for_m) + "m^2")
    combiner = int(int(form_data['quantity']) * area_for_m)
    c.drawString(100, 550, "All area in m^2 for " + str(form_data['quantity']) + " orders: " + str(combiner) + "m^2")
    all_area = int(combiner * 12)
    c.drawString(100, 510, "To paint 1m^2 need 12 milliliters of paint.")
    c.drawString(100, 470, "To paint everything needed "+ str(all_area) + " milliliters(+/-5%) of paint.")
    
    for i in range(4):
        c.drawString((i*120)+100, 430, categories[i][0]+ " - " + str(int((all_area * values[i]) / 100)) + "mg(+/-5%)")

    # Add image to the PDF
    img = Image.open("chart.png")
    width, height = img.size
    aspect_ratio = height / width
    desired_width = 400  # Adjust the width as needed
    desired_height = int(desired_width * aspect_ratio)
    c.drawImage("chart.png", 100, 70, width=desired_width, height=desired_height)
    c.save()



def calculate_ink_percentage(image_path):
    # Открываем изображение
    img = Image.open(image_path)

    # Преобразуем изображение в массив numpy для более удобной обработки
    img_array = np.array(img)

    # Получаем размеры изображения
    height, width, _ = img_array.shape

    # Инициализируем счетчики для каждого цвета
    cyan = 0
    magenta = 0
    yellow = 0
    black = 0

    # Проходим по каждому пикселю изображения
    for i in range(height):
        for j in range(width):
            # Получаем значения цветов изображения для текущего пикселя
            r, g, b = img_array[i, j]

            # Вычисляем процентное содержание каждого цвета CMYK
            c = 1 - r / 255
            m = 1 - g / 255
            y = 1 - b / 255
            # Для K (черного) выбирается минимальное значение из CMY
            k = min(c, m, y)

            # Обновляем счетчики для каждого цвета
            cyan += c
            magenta += m
            yellow += y
            black += k

    # Вычисляем средние значения для каждого цвета
    total_pixels = height * width
    cyan_percent = int((cyan / total_pixels) * 100)
    magenta_percent = int((magenta / total_pixels) * 100)
    yellow_percent = int((yellow / total_pixels) * 100)
    black_percent = int((black / total_pixels) * 100)

    # Нормализуем значения, чтобы их сумма была равна 100
    total_percentage = cyan_percent + magenta_percent + yellow_percent + black_percent
    cyan_percent = round((cyan_percent / total_percentage) * 100,2)
    magenta_percent = round((magenta_percent / total_percentage) * 100,2)
    yellow_percent = round((yellow_percent / total_percentage) * 100,2)
    black_percent = round((black_percent / total_percentage) * 100,2)

    # Возвращаем результат в виде словаря
    return {
        'Cyan': cyan_percent,
        'Magenta': magenta_percent,
        'Yellow': yellow_percent,
        'Black': black_percent
    }

def calculate_cmyk_matrix(image_path, generated_filepath):
    # Open the image
    img = Image.open(image_path)

    # Convert the image to a numpy array for easier processing
    img_array = np.array(img)

    # Get the dimensions of the image
    height, width, _ = img_array.shape

    # Initialize the CMYK matrix
    cmyk_matrix = np.zeros((height, width, 4))

    # Iterate over each pixel in the image
    for i in range(height):
        for j in range(width):
            # Get the RGB values of the current pixel
            r, g, b = img_array[i, j]

            # Compute the CMYK values
            c = 1 - r / 255
            m = 1 - g / 255
            y = 1 - b / 255
            k = min(c, m, y)

            # Normalize CMYK values so their sum equals 1
            total = c + m + y + k
            if total > 0:
                c /= total
                m /= total
                y /= total
                k /= total
            
            # Convert to percentages
            cmyk_matrix[i, j] = [c * 100, m * 100, y * 100, k * 100]

    # Save the CMYK matrix to a CSV file
    with open(generated_filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['X', 'Y', 'Cyan', 'Magenta', 'Yellow', 'Black'])

        for i in range(height):
            for j in range(width):
                writer.writerow([i, j] + list(cmyk_matrix[i, j]))

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


def generate_background(generated_filepath, images, width, height):
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

    square_size = int(int(width) // SQUARES_IN_WIDTH) 
    num_squares_x = int(int(width) // square_size) + 1 
    num_squares_y = int(int(height) // square_size) + 1 
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



class PNGManager:
    def __init__(self, image_path):
        self.image = Image.open(image_path)
        self.temp_directory = os.path.join(settings.MEDIA_ROOT, 'tempParts/')
        self.generated_directory = os.path.join(settings.MEDIA_ROOT, 'generatedParts/')
        os.makedirs(self.temp_directory, exist_ok=True)
        self.split_images = []
    
    def split_image(self):
        width, height = self.image.size
        self.split_width = width // 100
        self.split_height = height // 100

        for x in range(100):
            for y in range(100):
                left = x * self.split_width
                top = y * self.split_height
                right = left + self.split_width
                bottom = top + self.split_height
                cropped_image = self.image.crop((left, top, right, bottom))
                path = os.path.join(self.temp_directory, f'image_{x}_{y}.png')
                cropped_image.save(path)
                self.split_images.append((cropped_image, path))

    def combine_images(self, finalSave, fromX, fromY, width, height):
        target_width = int(self.split_width * (width / 100 * 100))
        target_height = int(self.split_height * (height / 100 * 100))
        combined_image = Image.new('RGB', (target_width, target_height))
        
        for x in range(fromX, fromX + width):
            for y in range(fromY, fromY + height):
                path = os.path.join(self.temp_directory, f'image_{x}_{y}.png')
                img = Image.open(path)
                combined_image.paste(img, ((x - fromX) * self.split_width, (y - fromY) * self.split_height))
        
        combined_image.save(finalSave)
        return combined_image
    def compare_images(self, image_path, generated_filepath, generated_red_filepath, generated_csv_small_filepath, generated_csv_matrix_filepath):
        base_image = Image.open(generated_filepath)
        comparing_image = Image.open(image_path)
        base_pixels = base_image.load()
        comparing_pixels = comparing_image.load()

        visual_image = Image.new('RGB', base_image.size, color='white')
        visual_pixels = visual_image.load()
        total_difference = 0  # To track the total difference
        max_possible_diff = 3 * 255 * base_image.width * base_image.height  
        # Detailed CSV 
        with open(generated_csv_small_filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['X', 'Y', 'Red Difference', 'Green Difference', 'Blue Difference'])

            # Matrix-like CSV for RGB differences
            matrix_csv = [['(R, G, B)' for _ in range(base_image.width)] for _ in range(base_image.height)]
            for x in range(base_image.width):
                for y in range(base_image.height):
                    r1, g1, b1 = base_pixels[x, y]
                    r2, g2, b2 = comparing_pixels[x, y]
                    diff = (abs(r1 - r2), abs(g1 - g2), abs(b1 - b2))
                    writer.writerow([x, y] + list(diff))

                    # Update total difference
                    total_difference += sum(diff)

                    # Calculate intensity of red based on the average difference
                    intensity = sum(diff) / (3 * 255)
                    red_intensity = int(255 * intensity)
                    visual_pixels[x, y] = (255, 255 - red_intensity, 255 - red_intensity)
                    matrix_csv[y][x] = f"({diff[0]}, {diff[1]}, {diff[2]})"

        visual_image.save(generated_red_filepath)

        # Save the matrix-like CSV
        with open(generated_csv_matrix_filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in matrix_csv:
                writer.writerow(row)
        
        mismatch_percentage = (total_difference / max_possible_diff) * 100
        return mismatch_percentage
    def generate_fix_image(self, image_path, generated_filepath, output_fixed_filepath):
        base_image = Image.open(generated_filepath).convert("RGBA")
        comparing_image = Image.open(image_path).convert("RGBA")
        base_pixels = base_image.load()
        comparing_pixels = comparing_image.load()
        fix_image = Image.new('RGBA', base_image.size, (255, 255, 255, 0))  # Create a transparent image
        fix_pixels = fix_image.load()

        for x in range(base_image.width):
            for y in range(base_image.height):
                r1, g1, b1, a1 = base_pixels[x, y]
                r2, g2, b2, a2 = comparing_pixels[x, y]

                if (r1, g1, b1) != (r2, g2, b2):
                    # Calculate the difference and apply proportional transparency
                    diff_r = r1 - r2
                    diff_g = g1 - g2
                    diff_b = b1 - b2
                    intensity = (abs(diff_r) + abs(diff_g) + abs(diff_b)) / 3
                    alpha = int(255 * (intensity / 255))
                    fix_pixels[x, y] = (
                        max(0, min(255, diff_r)),
                        max(0, min(255, diff_g)),
                        max(0, min(255, diff_b)),
                        alpha  # Set alpha proportional to the intensity of the difference
                    )

        # Save the fix image
        fix_image.save(output_fixed_filepath, "PNG")
class AnalyzeImage(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            json_data_str = request.POST['formData']
            form_data = json.loads(json_data_str)
            print(form_data)
            images = request.FILES.getlist('images')
            if not images:
                return Response({'error': 'No images uploaded'}, status=status.HTTP_400_BAD_REQUEST)
            # os.path.join(settings.MEDIA_ROOT, 'clothesdata/', form_data.get('model', '') + "/" + form_data.get('model', '') + ".svg")

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'temp/')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            checkImagePath = ""
            for image in images:
                filename = image.name
                filepath = os.path.join(upload_dir, filename)
                checkImagePath = filepath
                # Save image to file system
                with open(filepath, 'wb') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            print(images)
            print(checkImagePath)
            
            manager = PNGManager(os.path.join(settings.MEDIA_ROOT, 'generated/') + form_data['generated'])
            current_time_unix = str(int(time.time()))
            generated_filename = current_time_unix + 'generated_background.png'
            generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generatedParts/', generated_filename)
            generated_red_filename = current_time_unix + 'generated_background_red.png'
            generated_red_filepath = os.path.join(settings.MEDIA_ROOT, 'generatedParts/', generated_red_filename)
            generated_fix_filename = current_time_unix + 'generated_background_fix.png'
            generated_fix_filepath = os.path.join(settings.MEDIA_ROOT, 'generatedParts/', generated_fix_filename)
            generated_csv_small_filename = current_time_unix + 'generated_small.csv'
            generated_csv_small_filepath = os.path.join(settings.MEDIA_ROOT, 'generatedParts/', generated_csv_small_filename)
            generated_csv_matrix_filename = current_time_unix + 'dif_matrix.csv'
            generated_csv_matrix_filepath = os.path.join(settings.MEDIA_ROOT, 'generatedParts/', generated_csv_matrix_filename)
            manager.split_image()
            manager.combine_images(generated_filepath, 0, 0, 100, 100)
            difference = manager.compare_images(checkImagePath, generated_filepath, generated_red_filepath, generated_csv_small_filepath, generated_csv_matrix_filepath)
            manager.generate_fix_image(checkImagePath, generated_filepath, generated_fix_filepath)
            return Response({'response': 'lol',
                            'generated_background': generated_filename,
                            'generated_red_background': generated_red_filename,
                            'csv_long': generated_csv_small_filename,
                            'csv_matrix': generated_csv_matrix_filename,
                            'fix_background': generated_fix_filename,
                            'difference': difference,



                     }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    
class GenerateOrder(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            json_data_str = request.POST['formData']
            form_data = json.loads(json_data_str)
            print(form_data)
            current_time_unix = str(int(time.time()))
            generated_filename = current_time_unix + 'generated_background.png'
            generated_filepath = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_filename)
            os.makedirs(os.path.dirname(generated_filepath), exist_ok=True)  # Ensure generated directory exists
            instruction_file = os.path.join(settings.MEDIA_ROOT, 'clothesdata/', form_data.get('model', '') + "/" + form_data.get('model', '') + ".svg")
            images = request.FILES.getlist('images')
            tree = ET.parse(instruction_file)
            root = tree.getroot()
            width = root.get('width')
            height = root.get('height')
            generate_background(generated_filepath, images, width, height)


            root = tree.getroot()
            width = root.get('width')
            height = root.get('height')
            width_in_mm = 1900
            height_in_mm = int((int(height) *int(width_in_mm))/ int(width))
            pdf_size_data = {'width_in_mm':width_in_mm, 'height_in_mm':height_in_mm}
            # Open the DXF file
            generated_with_cut_filename = current_time_unix + 'generated_with_cut.png'
            generated_with_cut = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_with_cut_filename)
            add_svg_to_image(generated_filepath, instruction_file, generated_with_cut)
            generated_pdf_filename = current_time_unix + "output.pdf"
            generated_pdf = os.path.join(settings.MEDIA_ROOT, 'generated/', generated_pdf_filename)
            generate_chart_and_save_to_pdf(calculate_ink_percentage(generated_filepath), form_data,pdf_size_data, generated_pdf)
            return Response({'response': 'Images uploaded successfully',
                             'generated_filename': generated_filename,
                             'generated_pdf_filename': generated_pdf_filename,
                             'generated_with_cut_filename': generated_with_cut_filename
                            }, status=status.HTTP_201_CREATED)
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


class GetAnalyzeOrder(APIView):
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
    path('get-list-data/', views.getListData, name="get-list-data"),
    path('get-analyze-order/', GetAnalyzeOrder.as_view()),
    path('analyze/', AnalyzeImage.as_view()),

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