from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from authentication.permissions import IsUserOwner
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import (
    UserSerializer,
    UserDetailSerializer,
    RegisterSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    '''
    Vue pour récuperer les informations d'un utilisateur.
    '''
    queryset = User.objects.all().order_by('id')
    permission_classes = [
        IsAuthenticated,
        IsUserOwner,
        ]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        elif self.request.query_params.get('minimal') == 'true':
            return UserSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "message": "User was successfully update.",
                "data": serializer.data
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "Error update user",
                "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_username = instance.username
            self.perform_destroy(instance)
            return Response(
                {
                    "message": f"{user_username} was successfully deleted.",
                },
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {
                    "message": "Error delete user",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


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
