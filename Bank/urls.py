from django.urls import path
from .views import *

urlpatterns = [
    path('soal/',SoalView.as_view()),
    path('soal/',SoalDetailView.as_view()),
    path('solve/',Solve.as_view()),
    path('solvefile/' ,SolveFile.as_view()),
    ]