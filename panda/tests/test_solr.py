#!/usr/bin/env python

import datetime

from django.test import TestCase

from panda import solr as solrjson

class TestSolrJSONEncoder(TestCase):
    def test_datetime(self):
        v = { 'datetime': datetime.datetime(2012, 4, 11, 11, 3, 0) }
        self.assertEqual(solrjson.dumps(v), '{"datetime": "2012-04-11T11:03:00Z"}')

    def test_date(self):
        v = { 'date': datetime.date(2012, 4, 11) }
        self.assertEqual(solrjson.dumps(v), '{"date": "2012-04-11"}')

    def test_time(self):
        v = { 'time': datetime.time(11, 3, 0) }
        self.assertEqual(solrjson.dumps(v), '{"time": "11:03:00"}')

    def test_int(self):
        v = { 'int': 123 }
        self.assertEqual(solrjson.dumps(v), '{"int": 123}')

