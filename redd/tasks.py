#!/usr/bin/env python

import json
from uuid import uuid4

from celery.decorators import task
from django.conf import settings
from sunburnt import SolrInterface

from csvkit import CSVKitReader
from csvkit.exceptions import InvalidValueForTypeException, InvalidValueForTypeListException
from csvkit.typeinference import normalize_table

SOLR_ADD_BUFFER_SIZE = 500

@task(name='Import data')
def dataset_import_data(dataset_id):
    from redd.models import Dataset

    raise TypeError('blah!')

    dataset = Dataset.objects.get(id=dataset_id)

    solr = SolrInterface(settings.SOLR_ENDPOINT)
    #solr_fields = []

    #for h, t in dataset.schema:
    #    if t == 'NoneType':
    #        solr_fields.append(None)
    #    else:
    #        solr_fields.append('%s_%s' % (h, t.__name__))
        
    reader = CSVKitReader(open(dataset.data_upload.get_path(), 'r'))
    reader.next()

    add_buffer = []
    normal_type_exceptions = []

    for i, row in enumerate(reader, start=1):
        data = {}

        typing="""for t, header, field, value in izip(normal_types, headers, solr_fields, row):
            try:
                value = normalize_column_type([value], normal_type=t)[1][0]
            except InvalidValueForTypeException:
                # Convert exception to row-specific error
                normal_type_exceptions.append(InferredNormalFalsifiedException(i, header, value, t))
                continue

            # No reason to send null fields to Solr (also sunburnt doesn't like them) 
            if value == None:
                continue

            if t in [unicode, bool, int, float]:
                if value == None:
                    continue

                data[field] = value
            elif t == datetime:
                data[field] = value.isoformat()
            elif t == date:
                pass
            elif t == time:
                pass
            else:
                # Note: if NoneType should never fall through to here 
                raise TypeError('Unexpected normal type: %s' % t.__name__)"""

        # If we've had a normal type exception, don't bother do the rest of this
        if not normal_type_exceptions:
            data = {
                'id': uuid4(),
                'dataset_id': dataset.id,
                'row': str(i),
                'full_text': '\n'.join(row),
                'csv_data': json.dumps(row)
            }

            add_buffer.append(data)

            if i % SOLR_ADD_BUFFER_SIZE == 0:
                solr.add(add_buffer)
                add_buffer = []

    if add_buffer:
        solr.add(add_buffer)
        add_buffer = []
    
    if not normal_type_exceptions:
        solr.commit()
    else:
        # Rollback pending changes
        solr.delete(queries=solr.query(dataset_id=dataset.id))
        
        for e in normal_type_exceptions:
            print e 

    print 'Finished'

