# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")

# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are an assistant."},
#         {"role": "user", "content": "Test the API connection."}
#     ]
# )
# print(response.choices[0].message.content)
import os
from openai import OpenAI

client = OpenAI()  # Correct import
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from dotenv import load_dotenv
import pdfplumber
from pdf2image import convert_from_path
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def answer_question(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request body
            data = json.loads(request.body)
            question = data.get('question')
            pdf_text = data.get('document_text')

            if not question or not pdf_text:
                return JsonResponse({'error': "Both 'question' and 'document_text' are required."}, status=400)

            # Call OpenAI API to answer the question based on PDF content
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": f"Based on the following information from the PDF: {pdf_text}. {question}"}
            ],
            max_tokens=100,
            temperature=0.5)

            response_text = response.choices[0].message.content.strip()

            return JsonResponse({'answer': response_text})

        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method. Only POST requests are allowed."}, status=400)

