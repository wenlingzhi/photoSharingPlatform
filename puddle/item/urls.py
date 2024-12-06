from django.urls import path
from . import views

app_name = 'item'
urlpatterns = [
    path('',views.items,name='items'),
    path('new/',views.new,name='new'),
    path('<int:item_id>/toggle_like/', views.toggle_like, name='toggle_like'),
    path('<int:item_id>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('<int:pk>/', views.detail, name='detail'), 
    path('<int:pk>/delete/',views.delete,name='delete'),
    path('<int:pk>/edit/',views.edit,name='edit'),
    path('<int:pk>/',views.detail,name='detail')
]
