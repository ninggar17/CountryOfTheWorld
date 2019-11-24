from django.contrib.auth.models import User, Group
from requests import Response
from rest_framework import status
from rest_framework.response import Response

from . import serializers
from rest_framework import viewsets
from executor.serializers import UserSerializer, GroupSerializer

cleaned_ids = {

}


def get_next_item_id():
    if cleaned_ids:
        return max(cleaned_ids) + 1
    else:
        return 1


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class QueryViewSet(viewsets.ViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    # def post(self, request):
    #     data = request.data.get('query', None)
    #     if data:
    #         res = CountryInfo(data)
    #         response = Response(res, status=status.HTTP_200_OK)
    #         return response
    #         # return JsonResponse(res, safe=False)
    #     else:
    #         return Response(None, status=status.HTTP_400_BAD_REQUEST)
    #
    # def get(self, request):
    #     data = request.data.get('query', None)
    #     if data:
    #         res = CountryInfo(data)
    #         response = Response(res, status=status.HTTP_200_OK)
    #         return response
    #     else:
    #         return Response(None, status=status.HTTP_400_BAD_REQUEST)
    serializer_class = serializers.CountryInfo

    def list(self, request):
        serializer = serializers.QuerySerializer(
            instance=cleaned_ids.values(), many=True
        )
        return Response(serializer.data)

    def create(self, request):
        is_many = isinstance(request.data, list)
        if not is_many:
            serializer = serializers.QuerySerializer(data=request.data)
            if serializer.is_valid():
                cleaning_id = serializer.save()
                num = get_next_item_id()
                cleaned_ids[num] = cleaning_id
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            for i in range(len(request.data)):
                serializer = serializers.QuerySerializer(data=request.data[i])
                if serializer.is_valid():
                    cleaning_id = serializer.save()
                    num = get_next_item_id()
                    cleaned_ids[num] = cleaning_id
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            cleaned_id = cleaned_ids[int(pk)]
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = serializers.CountryInfo(instance=cleaned_id)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            cleaned_id = cleaned_ids[int(pk)]
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        del cleaned_ids[cleaned_id]
        return Response(status=status.HTTP_204_NO_CONTENT)
