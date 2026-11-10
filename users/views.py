from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Користувача успішно зареєстровано"}, 
                status=status.HTTP_201_CREATED
            )
        # При невалідних даних повертає статус 400 та помилки для кожної з полів[cite: 4]
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #[cite: 4]