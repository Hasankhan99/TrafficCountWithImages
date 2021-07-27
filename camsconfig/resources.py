from import_export import resources
from .models import CamsData


class CamsDataResource(resources.ModelResource):
    class Meta:
        model = CamsData
        exclude = ('id',)