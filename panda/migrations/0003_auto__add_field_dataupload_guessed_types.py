# encoding: utf-8
import datetime
import os

from south.db import db
from south.v2 import SchemaMigration
from django.conf import settings

from panda.models import DataUpload
from panda import utils

class Migration(SchemaMigration):

    def get_path(self, data_upload):
        """
        From BaseUpload abstract model.
        """
        return os.path.join(settings.MEDIA_ROOT, data_upload.filename)

    def dialect_as_parameters(self, data_upload):
        """
        From DataUpload model.
        """
        dialect_params = {}

        # This code is absolutely terrifying
        # (Also, it works.)
        for k, v in data_upload.dialect.items():
            if isinstance(v, basestring):
                dialect_params[k] = v.decode('string_escape')
            else:
                dialect_params[k] = v

        return dialect_params

    def forwards(self, orm):
        
        # Adding field 'DataUpload.guessed_types'
        db.add_column('panda_dataupload', 'guessed_types', self.gf('panda.fields.JSONField')(null=True), keep_default=False)

        db.commit_transaction()     # Commit the first transaction
        db.start_transaction()      # Start the second, committed on completion

        for data_upload in orm.DataUpload.objects.all():
            path = self.get_path(data_upload) 
            try:
                data_upload.guessed_types = utils.guess_column_types(data_upload.data_type, path, self.dialect_as_parameters(data_upload), encoding=data_upload.encoding)
                data_upload.save()
            except IOError:
                # File does not exist on disk
                continue

    def backwards(self, orm):
        
        # Deleting field 'DataUpload.guessed_types'
        db.delete_column('panda_dataupload', 'guessed_types')


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
        'panda.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'panda.dataset': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Dataset'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'datasets'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['panda.Category']"}),
            'columns': ('panda.fields.JSONField', [], {'default': 'None', 'null': 'True'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256', 'db_index': 'True'})
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
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exports'", 'to': "orm['panda.Dataset']"}),
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
        'panda.taskstatus': {
            'Meta': {'object_name': 'TaskStatus'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'null': 'True', 'to': "orm['auth.User']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'panda.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['panda']
