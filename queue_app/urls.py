from django.urls import path
from . import views

app_name = 'queue_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('queue/', views.queue_view, name='queue'),
        path('pop/', views.pop_queue, name='pop_queue'),
]
