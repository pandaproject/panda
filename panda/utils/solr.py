#!/usr/bin/env python

from uuid import uuid4

from django.utils import simplejson as json
from django.utils.timezone import now

def make_data_row(dataset, data, external_id=None):
    last_modified = now().replace(microsecond=0, tzinfo=None)
    last_modified = last_modified.isoformat('T') + 'Z' 

    solr_row = {
        'dataset_slug': dataset.slug,
        'full_text': '\n'.join([unicode(d) for d in data]),
        'data': json.dumps(data),
        'last_modified': last_modified 
    }

    if external_id:
        solr_row['id'] = '%s-%s' % (dataset.slug, external_id)
        solr_row['external_id'] = external_id
    else:
        solr_row['id'] = unicode(uuid4())

    return solr_row

