from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('', views.index, name='index'),
    # path('upload/', views.upload_pdf, name='upload_pdf'),
    # path('answer/', views.answer_question, name='answer_question'),
    path('', views.index, name='index'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('ask/', views.upload_pdf, name='ask_question'),  # Reuse the same view
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

