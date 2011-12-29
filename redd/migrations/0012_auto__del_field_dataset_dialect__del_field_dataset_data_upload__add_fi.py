# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Dataset.dialect'
        db.delete_column('redd_dataset', 'dialect')

        # Deleting field 'Dataset.data_upload'
        db.delete_column('redd_dataset', 'data_upload_id')

        # Adding field 'Dataset.initial_upload'
        db.add_column('redd_dataset', 'initial_upload', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='initial_upload_for', null=True, to=orm['redd.Upload']), keep_default=False)

        # Changing field 'Dataset.creation_date'
        db.alter_column('redd_dataset', 'creation_date', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Adding field 'Upload.creation_date'
        db.add_column('redd_upload', 'creation_date', self.gf('django.db.models.fields.DateTimeField')(default=None), keep_default=False)

        # Adding field 'Upload.dataset'
        db.add_column('redd_upload', 'dataset', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['redd.Dataset']), keep_default=False)

        # Adding field 'Upload.data_type'
        db.add_column('redd_upload', 'data_type', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True), keep_default=False)

        # Adding field 'Upload.dialect'
        db.add_column('redd_upload', 'dialect', self.gf('redd.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Upload.columns'
        db.add_column('redd_upload', 'columns', self.gf('redd.fields.JSONField')(null=True), keep_default=False)

        # Adding field 'Upload.sample_data'
        db.add_column('redd_upload', 'sample_data', self.gf('redd.fields.JSONField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Dataset.dialect'
        db.add_column('redd_dataset', 'dialect', self.gf('redd.fields.JSONField')(default=None, null=True), keep_default=False)

        # Adding field 'Dataset.data_upload'
        db.add_column('redd_dataset', 'data_upload', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['redd.Upload'], null=True, blank=True), keep_default=False)

        # Deleting field 'Dataset.initial_upload'
        db.delete_column('redd_dataset', 'initial_upload_id')

        # Changing field 'Dataset.creation_date'
        db.alter_column('redd_dataset', 'creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True))

        # Deleting field 'Upload.creation_date'
        db.delete_column('redd_upload', 'creation_date')

        # Deleting field 'Upload.dataset'
        db.delete_column('redd_upload', 'dataset_id')

        # Deleting field 'Upload.data_type'
        db.delete_column('redd_upload', 'data_type')

        # Deleting field 'Upload.dialect'
        db.delete_column('redd_upload', 'dialect')

        # Deleting field 'Upload.columns'
        db.delete_column('redd_upload', 'columns')

        # Deleting field 'Upload.sample_data'
        db.delete_column('redd_upload', 'sample_data')


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
        'redd.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'redd.dataset': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Dataset'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'datasets'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['redd.Category']"}),
            'columns': ('redd.fields.JSONField', [], {'default': 'None', 'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'datasets'", 'to': "orm['auth.User']"}),
            'current_task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['redd.TaskStatus']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_upload': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'initial_upload_for'", 'null': 'True', 'to': "orm['redd.Upload']"}),
            'last_modification': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'row_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sample_data': ('redd.fields.JSONField', [], {'default': 'None', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256', 'db_index': 'True'})
        },
        'redd.notification': {
            'Meta': {'object_name': 'Notification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': "orm['auth.User']"}),
            'related_dataset': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['redd.Dataset']", 'null': 'True'}),
            'related_task': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['redd.TaskStatus']", 'null': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'info'", 'max_length': '16'})
        },
        'redd.taskstatus': {
            'Meta': {'object_name': 'TaskStatus'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'PENDING'", 'max_length': '50'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'traceback': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'redd.upload': {
            'Meta': {'object_name': 'Upload'},
            'columns': ('redd.fields.JSONField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['redd.Dataset']"}),
            'dialect': ('redd.fields.JSONField', [], {'null': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'sample_data': ('redd.fields.JSONField', [], {'null': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['redd']
