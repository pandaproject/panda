#!/usr/bin/env python

import re

from django.db import models
from django.template.defaultfilters import slugify

class SluggedModel(models.Model):
    """
    Extend this class to get a slug field and slug generated from a model
    field. We call the 'get_slug_text', '__unicode__' or '__str__'
    methods (in that order) on save() to get text to slugify. The slug may
    have numbers appended to make sure the slug is unique.
    """
    slug = models.SlugField(max_length=256)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()  
        
        super(SluggedModel, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Customized unique_slug function
        """
        if hasattr(self, 'get_slug_text') and callable(self.get_slug_text):
            slug_txt = self.get_slug_text()
        elif hasattr(self, '__unicode__'):
            slug_txt = unicode(self)
        elif hasattr(self, '__str__'):
            slug_txt = str(self)
        else:
            return

        slug = slugify(slug_txt)
        all_slugs = set(sl.values()[0] for sl in self.__class__.objects.values("slug"))

        if slug in all_slugs:
            counterFinder = re.compile(r'-\d+$')
            counter = 2
            slug = '%s-%i' % (slug, counter)

            while slug in all_slugs:
                slug = re.sub(counterFinder, '-%i' % counter, slug)
                counter += 1

        return slug 

