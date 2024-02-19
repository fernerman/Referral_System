from rest_framework import status
from rest_framework.views import APIView
from .serialiezers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, \
    RefferalEmailSerializer
from .models import User, RefferalSystem
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from users.renderers import UserRenderer
from django.contrib.auth import authenticate, login
import random
import secrets
import hashlib
from datetime import timedelta, datetime
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import OpenApiParameter, extend_schema
from django.utils import timezone
from rest_framework.decorators import api_view

TIME = 3


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


def generate_referral_code(length=15):
    # Generate a random string of alphanumeric characters
    code = secrets.token_urlsafe(length)[:length]
    return code


def register_user(request_data):
    serializer = UserRegistrationSerializer(data=request_data)
    serializer.is_valid(raise_exception=True)
    registered_user = serializer.save()
    return registered_user


@extend_schema(
    request=UserRegistrationSerializer,
    summary="Создание реферала по реферальному коду",
    tags=["user"]

)
@api_view(['POST'])
def register_code(request, code):
    try:
        task = RefferalSystem.objects.get(code=code, isActive=1)
    except RefferalSystem.DoesNotExist:
        return Response({'error': 'No RefferalSystem found for the given code'}, status=status.HTTP_404_NOT_FOUND)

    try:
        registered_user = register_user(request.data)
        task.referal_id = registered_user.id
        task.isActive = False
        task.save()
        return Response({'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'errors': {"non_field_errors": [str(e)]}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# don`t used class
class UsersView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserRegistrationSerializer(users, many=True)  # many=True, так как у вас список пользователей
        return Response({"users": serializer.data})


@extend_schema(
    request=UserRegistrationSerializer,
    summary="Создание пользователя",
    tags=["user"],
    responses={
        status.HTTP_201_CREATED: UserProfileSerializer}
)
@api_view(['POST'])
def create_my_users(request):
    registered_user = register_user(request.data)
    serializer = UserProfileSerializer(registered_user)  # Serialize the registered user
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    request=UserLoginSerializer,
    summary="Вход пользователя",
    tags=["user"]
)
@api_view(['POST'])
def login_users(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors': {"non_field_errors": ["Email or Password is not valid"]}},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UserLoginSerializer,
        summary="Получение информации о рефералах по id реферера",
        tags=["user"]
    )
    def get(self, request, id):
        referals = []
        try:
            task = RefferalSystem.objects.filter(refer_id=id)
            if task.exists():
                for element in task:
                    referal = User.objects.get(id=element.referal_id)
                    serializer = UserProfileSerializer(referal)
                    serialized_data = serializer.data
                    referals.append(serialized_data)
                return Response({'referals': referals}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'Referral code doesn`t exist'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'errors': {"non_field_errors": [str(e)]}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefferalCodeView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    # code/delete/<str:code>/
    @extend_schema(
        summary="Удаление реферального кода",
        request=UserProfileSerializer,
        tags=["code"]
    )
    def delete(self, request, code=None):
        user_info = UserProfileSerializer(request.user)
        try:
            task = RefferalSystem.objects.get(code=code)
            task.delete()
            return Response({'msg': 'Referral code removed'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'errors': {"non_field_errors": [str(e)]}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 'code/create/'
    @extend_schema(
        summary="Создание реферального кода",
        tags=["code"]
    )
    def get(self, request):
        ref_link = generate_referral_code()
        user = request.user

        try:
            task = RefferalSystem.objects.get(refer_id=user.id, isActive=1)
            if task.due_date < timezone.localtime(timezone.now()):
                task.isActive = False
                task.save()
                return Response({'msg': f'The Refferal Link was expired{task.due_date}!'},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {'msg': f'You`r code is {task.code}! It will be expired at {task.due_date}!'},
                    status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            due_date = timezone.localtime(timezone.now()) + timedelta(days=TIME)
            ref_sys = RefferalSystem(code=ref_link, due_date=due_date, refer=user, isActive=True)
            ref_sys.save()
            return Response({'ref_link': ref_link, 'msg': 'Create is valid Referral Link'},
                            status=status.HTTP_200_OK)

    # 'code/get_from_email/'
    @extend_schema(
        request=RefferalEmailSerializer,
        summary="Получение реферального кода по email рефера",
        tags=["code"]

    )
    def post(self, request):

        # user = request.user
        serializer = RefferalEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            try:
                user = User.objects.get(email=email)
                user_id = user.id
                task = RefferalSystem.objects.get(refer_id=user_id, isActive=1)

                return Response({'ref_link': task.code, 'email_refer': email},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'errors': {"non_field_errors": [str(e)]}},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
