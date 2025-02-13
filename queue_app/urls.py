from django.urls import path
from . import views

app_name = "queue_app"  # <--- ADD THIS LINE

# urlpatterns = [
#     path('', views.home, name='home'),
# ]
urlpatterns = [
    path('', views.home, name='home'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]