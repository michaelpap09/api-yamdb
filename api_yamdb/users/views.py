"""Представления приложения пользователей."""

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from users.permissions import IsAdmin
from users.serializers import (
    SignupSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Возвращает или обновляет профиль текущего пользователя."""
        if request.method == 'GET':
            serializer = UserMeSerializer(request.user)
            return Response(serializer.data)

        serializer = UserMeSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(('POST',))
@permission_classes((AllowAny,))
def signup(request):
    """Регистрирует пользователя и отправляет код подтверждения."""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    email = serializer.validated_data['email']

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'email': email},
    )

    confirmation_code = get_random_string(length=50)
    user.confirmation_code = confirmation_code
    user.save()

    send_mail(
        'Код подтверждения YaMDb',
        f'Ваш код подтверждения: {confirmation_code}',
        'admin@yamdb.local',
        [email],
        fail_silently=False,
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
@permission_classes((AllowAny,))
def get_token(request):
    """Выдаёт JWT-токен по username и коду подтверждения."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'],
    )

    if user.confirmation_code != serializer.validated_data[
        'confirmation_code'
    ]:
        return Response(
            {'confirmation_code': 'Неверный код подтверждения.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)
