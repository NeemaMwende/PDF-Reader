from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
from .models import PDFDocument
from PyDF2 import PdfReader
from transformers import pipeline

qa_pipeline = pipeline("question-answering")

def upload_pdf(request):
    if request.method == 'POST':
        pdf = request.FILES['file']
        document = PDFDocument.objects.create(file=pdf)
        
        reader = PdfReader(document.file)
        full_text = ""
        for page in  reader.pages:
            full_text += page.extract_text()
            
        return  JsonResponse({'message': "File uploaded  successfully", 'text': full_text})
    return JsonResponse({"error": "Invalid request"})

def answer_question(request):
    question = request.POST.get('question')
    document_text = request.POST.get('document_text')
    
    response = qa_pipeline({
        'question': question,
        'context': document_text
    })
    return JsonResponse({'answer': response['answer']})