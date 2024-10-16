from django.shortcuts import render
from django.http import JsonResponse
from .models import PDFDocument
from PyPDF2 import PdfReader  # Correct import from PyPDF2
from transformers import AutoTokenizer, AutoModelWithLMHead

# Load the model and tokenizer
model_name = "MaRiOrOsSi/t5-base-finetuned-question-answering"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelWithLMHead.from_pretrained(model_name)

def upload_pdf(request):
    if request.method == 'POST':
        pdf = request.FILES['file']
        document = PDFDocument.objects.create(file=pdf)
        
        # Read the uploaded PDF and extract text
        reader = PdfReader(document.file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()
        
        return JsonResponse({'message': "File uploaded successfully", 'text': full_text})
    return JsonResponse({"error": "Invalid request"}, status=400)

def answer_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        document_text = request.POST.get('document_text')

        if not question or not document_text:
            return JsonResponse({"error": "Question or document text missing"}, status=400)

        # Prepare input for the model
        input_text = f"question: {question} context: {document_text}"
        encoded_input = tokenizer([input_text], return_tensors='pt', max_length=512, truncation=True)

        # Generate the answer
        output = model.generate(input_ids=encoded_input.input_ids, attention_mask=encoded_input.attention_mask)
        answer = tokenizer.decode(output[0], skip_special_tokens=True)

        return JsonResponse({'answer': answer})

    return JsonResponse({"error": "Invalid request"}, status=400)
