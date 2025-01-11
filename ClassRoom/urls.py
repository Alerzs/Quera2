from django.urls import path
from .views import *


urlpatterns = [
    path('join/<str:shenase>',JoinClass.as_view()),
    path('private/<str:invite_id>',JoinClassByInvitation.as_view()),
    path('invite/<str:shenase>' ,SendInvitation.as_view()),
    path('my_class/',Classview.as_view()),
    path('class_detail/<str:shenase>' ,ClassDetail.as_view()),
]