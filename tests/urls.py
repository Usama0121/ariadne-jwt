from .schema import schema
from django.urls import path
from ariadne.contrib.django.views import GraphQLView

urlpatterns = [
    path('', GraphQLView.as_view(schema=schema), name='index')
]
