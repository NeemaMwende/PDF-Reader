from django.urls import path
from .views import  *

urlpatterns = [
    path('upload/', views.upload_pdf.urls),
    path('answer/', views.answer_question.urls),
]