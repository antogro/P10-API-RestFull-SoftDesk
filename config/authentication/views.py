from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    RegisterSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    '''
    Vue pour récuperer les informations d'un utilisateur.
    '''
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.request.query_params.get('minimal') == 'true':
            return UserSerializer
        return UserSerializer


class RegisterViewSet(APIView):
    '''
    Vue pour l'enregistrement d'un nouvelle utilisateur.
    '''
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)
