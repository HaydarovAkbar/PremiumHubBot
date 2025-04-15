from django_filters import rest_framework as filters
from .models import TGUsers


class FilterByDate(filters.FilterSet):
    date_from = filters.DateFilter(field_name="date_of_created", lookup_expr='gte')
    date_to = filters.DateFilter(field_name="date_of_created", lookup_expr='lte')
    # slug = filters.CharFilter(field_name="username", lookup_expr='iexact')
