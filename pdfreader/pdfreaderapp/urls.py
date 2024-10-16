from django.urls import path
from . import views

urlpatterns = [
    # URL for uploading the PDF
    path('upload/', views.upload_pdf, name='upload_pdf'),

    # URL for asking a question
    path('answer/', views.answer_question, name='answer_question'),
]
