from import_export import resources

from .models import Countries


class CountriesResource(resources.ModelResource):
    class Meta:
        model = Countries

    def get_queryset(self):
        return self.Meta.model.objects.order_by('population')
