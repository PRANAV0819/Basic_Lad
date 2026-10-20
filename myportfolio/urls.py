from django.urls import path
from . import views

app_name = 'myportfolio'

urlpatterns = [
    # Primary Portfolio Showcase View
    path('', views.portfolio_preview_view, name='preview'),
    path('preview/', views.portfolio_preview_view, name='portfolio_preview'),
    path('view/<int:student_id>/', views.portfolio_preview_view, name='public_preview'),

    # Portfolio Builder / Editor View
    path('editor/', views.portfolio_editor_view, name='editor'),
    path('profile/', views.portfolio_editor_view, name='profile'),
]
