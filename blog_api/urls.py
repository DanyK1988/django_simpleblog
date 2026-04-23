from django.urls import path
from .views import PostList, PostDetail
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView  # new

urlpatterns = [
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('', PostList.as_view(), name='post_list'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # new
]