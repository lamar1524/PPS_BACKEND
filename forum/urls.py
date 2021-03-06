from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views
from users import views as user_views
from groups import views as group_views
from posts import views as post_views
from chatApp import views as chat_views
from django.contrib import admin

router = routers.DefaultRouter()
router.register(r'users', user_views.UserViewSet)
router.register(r'groups', group_views.GroupViewSet)
router.register(r'posts', post_views.PostViewSet)
router.register(r'messages', chat_views.ChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/login/', views.obtain_auth_token, name='login'),
    path('admin/', admin.site.urls),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
