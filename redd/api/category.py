#!/usr/bin/env python

from django.conf import settings
from django.db.models import Count
from tastypie.authorization import DjangoAuthorization

from redd.api.utils import PandaApiKeyAuthentication, SluggedModelResource, PandaSerializer
from redd.models import Category, Dataset

class CategoryResource(SluggedModelResource):
    """
    Simple API for Category objects. 
    """
    class Meta:
        queryset = Category.objects.annotate(dataset_count=Count('datasets'))
        resource_name = 'category'
        allowed_methods = ['get']

        authentication = PandaApiKeyAuthentication()
        authorization = DjangoAuthorization()
        serializer = PandaSerializer()

    def dehydrate(self, bundle):
        """
        If using an annotated queryset, return the dataset counts as well.
        (This happens when accessing the Category API directly, but not when
        a Category is embedded in another object, such as a Dataset.)
        """
        if hasattr(bundle.obj, 'dataset_count') and bundle.obj.dataset_count is not None:
            bundle.data['dataset_count'] = bundle.obj.dataset_count

        return bundle

    def get_list(self, request, **kwargs):
        """
        Overriden from underlying implementation in order to insert a fake category
        for "Uncategorized" datasets.
        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        objects = self.obj_get_list(request=request, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_list_uri(), limit=self._meta.limit)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['objects']]
        to_be_serialized['objects'] = [self.full_dehydrate(bundle) for bundle in bundles]

        # Insert fake category
        uncategorized = Category(
            id=settings.PANDA_UNCATEGORIZED_ID,
            slug=settings.PANDA_UNCATEGORIZED_SLUG,
            name=settings.PANDA_UNCATEGORIZED_NAME)
        uncategorized.__dict__['dataset_count'] = Dataset.objects.filter(categories=None).count() 
        uncategorized_bundle = self.full_dehydrate(self.build_bundle(obj=uncategorized))

        to_be_serialized['objects'].append(uncategorized_bundle)

        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

        return self.create_response(request, to_be_serialized)
