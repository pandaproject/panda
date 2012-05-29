# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SearchSubscription'
        db.create_table('panda_searchsubscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='subscribed_searches', to=orm['auth.User'])),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='subscribed_searches', null=True, to=orm['panda.Dataset'])),
            ('query', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('last_run', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('panda', ['SearchSubscription'])

    def backwards(self, orm):
        # Deleting model 'SearchSubscription'
        db.delete_table('panda_searchsubscription')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'panda.activitylog': {
            'Meta': {'unique_together': "(('user', 'when'),)", 'object_name': 'ActivityLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activity_logs'", 'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'panda.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
        },
        'panda.dataset': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Dataset'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'datasets'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['panda.Category']"}),
            'column_schema': ('panda.fields.JSONField', [], {'default': 'None', 'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datasets'", 'to': "orm['auth.User']"}),
            'current_task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['panda.TaskStatus']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_upload': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'initial_upload_for'", 'null': 'True', 'to': "orm['panda.DataUpload']"}),
            'last_modification': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'locked_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'row_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sample_data': ('panda.fields.JSONField', [], {'default': 'None', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
        },
        'panda.dataupload': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'DataUpload'},
            'columns': ('panda.fields.JSONField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data_uploads'", 'null': 'True', 'to': "orm['panda.Dataset']"}),
            'dialect': ('panda.fields.JSONField', [], {'null': 'True'}),
            'encoding': ('django.db.models.fields.CharField', [], {'default': "'utf-8'", 'max_length': '32'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'guessed_types': ('panda.fields.JSONField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'sample_data': ('panda.fields.JSONField', [], {'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'panda.export': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'Export'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exports'", 'null': 'True', 'to': "orm['panda.Dataset']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'panda.notification': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'Notification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': "orm['auth.User']"}),
            'related_dataset': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['panda.Dataset']", 'null': 'True'}),
            'related_export': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['panda.Export']", 'null': 'True'}),
            'related_task': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['panda.TaskStatus']", 'null': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Info'", 'max_length': '16'})
        },
        'panda.relatedupload': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'RelatedUpload'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related_uploads'", 'to': "orm['panda.Dataset']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'panda.searchlog': {
            'Meta': {'object_name': 'SearchLog'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'searches'", 'null': 'True', 'to': "orm['panda.Dataset']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'search_logs'", 'to': "orm['auth.User']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'panda.searchsubscription': {
            'Meta': {'object_name': 'SearchSubscription'},
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'subscribed_searches'", 'null': 'True', 'to': "orm['panda.Dataset']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_run': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subscribed_searches'", 'to': "orm['auth.User']"})
        },
        'panda.taskstatus': {
            'Meta': {'object_name': 'TaskStatus'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_description': ('django.db.models.fields.TextField', [], {}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'panda.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'activation_key_expiration': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['panda']