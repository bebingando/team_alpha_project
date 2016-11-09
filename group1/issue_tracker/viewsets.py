from django.contrib.auth import models as auth_models
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, response
from response import Response
from issue_tracker import models as it_models
from issue_tracker import serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = auth_models.User.objects.all()
    serializer_class = serializers.UserSerializer


class IssueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows issues to be viewed or edited.
    """
    queryset = it_models.Issue.objects.all()
    serializer_class = serializers.IssueSerializer


class IssueViewSetRO(viewsets.ReadOnlyModelViewSet):
    """
    Obtain a list of issues that meet a certain set of search criteria
    """
    queryset = it_models.Issue.objects.all()
    serializer_class = serializers.IssueSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'id',
        'title',
        'issue_type',
        'status',
        'priority',
        'project',
        'reporter',
        'assignee',
        'verifier'
    )

class IssueViewSetSingle(viewsets.ReadOnlyModelViewSet):
    """
    Obtain a single issue that matches the issue ID provided
    """
    queryset = it_models.Issue.objects.all()
    serializer_class = serializers.IssueSerializer

    def retrieve(self, request, pk=None):
        """Return a single Issue"""
        user = get_object_or_404(queryset, pk=pk)
        return Response(serializer.data)
