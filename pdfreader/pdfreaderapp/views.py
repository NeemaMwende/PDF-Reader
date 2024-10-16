import os
import openai
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from dotenv import load_dotenv
import pdfplumber
from pdf2image import convert_from_path
from django.views.decorators.csrf import csrf_exempt


# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def index(request):
    return render(request, 'index.html')

# Function to extract text from the uploaded PDF
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF file: {e}")
    return text

# Function to convert PDF pages to images
def convert_pdf_to_images(file_path):
    images = []
    try:
        pages = convert_from_path(file_path, dpi=200)
        for i, page in enumerate(pages):
            image_path = os.path.join(settings.MEDIA_ROOT, f'pdf_page_{i}.png')
            page.save(image_path, 'PNG')
            images.append(settings.MEDIA_URL + f'pdf_page_{i}.png')
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
    return images

# Endpoint to handle PDF upload and text extraction
@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST':
        # Check if a PDF file is uploaded
        if 'file' in request.FILES: 
            file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)

            # Extract text from the PDF
            pdf_text = extract_text_from_pdf(file_path)
            pdf_images = convert_pdf_to_images(file_path)

            # Store text and images in the session for answering questions later
            request.session['pdf_text'] = pdf_text
            request.session['pdf_images'] = pdf_images

            # Return JSON response with extracted text and image URLs
            return JsonResponse({'message': "File uploaded successfully", 'text': pdf_text, 'images': pdf_images})

    return JsonResponse({"error": "Invalid request"}, status=400)

# Endpoint to handle question answering based on the PDF content
def answer_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        pdf_text = request.POST.get('document_text')  # Text passed from frontend

        if question and pdf_text:
            try:
                # Call OpenAI API to answer the question based on PDF content
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant."},
                        {"role": "user", "content": f"Based on the following information from the PDF: {pdf_text}. {question}"}
                    ],
                    max_tokens=150,
                    temperature=0.5
                )
                response_text = response['choices'][0]['message']['content'].strip()

                return JsonResponse({'answer': response_text})

            except Exception as e:
                return JsonResponse({'error': f"Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
