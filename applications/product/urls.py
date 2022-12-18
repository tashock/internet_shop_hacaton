from django.urls import path
from applications.product.views import CategoryApiView, CommentApiView, ProductApiView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('category', CategoryApiView)
router.register('comment', CommentApiView)
router.register('', ProductApiView)


urlpatterns = [
    
]

urlpatterns += router.urls
