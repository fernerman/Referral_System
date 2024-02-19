from django.urls import path

from . import views
from .views import  UsersView, UserProfileView, RefferalCodeView


urlpatterns = [


    path('user/register/', views.create_my_users, name="register-user"),
    path('user/login/', views.login_users, name="login-user"),
    path("user/referals/<int:id>/", UserProfileView.as_view(), name="referals"),
    # path('user/profile/', UserProfileView.as_view(), name="profile-user"),
    path("user/register_referal/<str:code>/",views.register_code,name="register-referal"),
    # post
    path('code/', RefferalCodeView.as_view(), name="ref-code"),
    # delete
    # path("code/delete/<str:code>/", RefferalCodeView.as_view(), name="ref-code"),
    # # get
    # path("code/get_from_email/", RefferalCodeView.as_view(), name="ref-code"),
    # # patch
    # path("code/register/<str:code>/", views.register_code, name="ref-code"),


    # path('users/', UsersView.as_view()),
]
