import django_filters
from .models import BlogPostModel


class BlogPostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=BlogPostModel.STATUS_CHOICES)
    category = django_filters.NumberFilter(field_name='category__id')
    category_slug = django_filters.CharFilter(field_name='category__slug')
    tags = django_filters.CharFilter(method='filter_tags')
    created_after = django_filters.DateTimeFilter(
        field_name='created_at', lookup_expr='gte',
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at', lookup_expr='lte',
    )
    author = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = BlogPostModel
        fields = ['status', 'category', 'author']

    def filter_tags(self, queryset, name, value):
        tag_slugs = [t.strip() for t in value.split(',') if t.strip()]
        if tag_slugs:
            return queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset
