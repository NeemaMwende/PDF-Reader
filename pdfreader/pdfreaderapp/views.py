import os
import openai
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from dotenv import load_dotenv
from pdf2image import convert_from_path
import pdfplumber
from .models import PDFDocument  # If needed

# Load OpenAI API key from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF file: {e}")
    return text

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

def upload_pdf(request):
    if request.method == 'POST':
        # If a PDF file is uploaded, process it
        if 'pdf_file' in request.FILES:
            file = request.FILES['pdf_file']
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_path = fs.path(filename)

            # Extract text and images from PDF
            pdf_text = extract_text_from_pdf(file_path)
            pdf_images = convert_pdf_to_images(file_path)

            # Store text and images in session for later use
            request.session['pdf_text'] = pdf_text
            request.session['pdf_images'] = pdf_images

            return JsonResponse({'message': "File uploaded successfully", 'text': pdf_text, 'images': pdf_images})

        # If a question is asked based on the PDF content
        question = request.POST.get('question')
        pdf_text = request.session.get('pdf_text', '')

        if question and pdf_text:
            try:
                # Call OpenAI API to generate an answer based on the PDF content and question
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
