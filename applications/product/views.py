from django.shortcuts import render
from rest_framework import status, mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from applications.product.serializers import *
from applications.product.models import Product, Category, Like, Rating, Comment, Favorite
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from applications.product.permissions import IsOwner, IsCommentOwner
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action


class LargeResultSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'
    max_page_size = 10000 
    
    
class ProductApiView(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwner]
    pagination_class = LargeResultSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'owner']
    search_fields = ['title', 'description']
    ordering_fields = ['id']
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['POST'])    # post/id/like
    def like(self, request, pk, *args, **kwargs):
        like_obj, _ = Like.objects.get_or_create(product_id=pk, owner=request.user)
        like_obj.like = not like_obj.like
        like_obj.save()
        status = 'liked'
        if not like_obj.like:
            status = 'unliked'
        
        return Response({'status': status})

    @action(detail=True, methods=['POST'])
    def rating(self, request, pk, *args, **kwargs):
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating_obj, _ = Rating.objects.get_or_create(post_id=pk, owner=request.user)
        rating_obj.rating = request.data['rating']
        rating_obj.save()
        
        return Response(request.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk, *args, **kwargs):
        favorite_obj, _ = Favorite.objects.get_or_create(product_id=pk, owner=request.user)
        favorite_obj.favorite = not favorite_obj.favorite
        favorite_obj.save()
        status = 'added to favorite'
        if not favorite_obj.favorite:
            status = 'removed from favorite'
            
        return Response({'status': status})
    

class CategoryApiView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    

class CommentApiView(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCommentOwner]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset
