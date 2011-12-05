# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TaskStatus'
        db.create_table('redd_taskstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(default='PENDING', max_length=50)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('traceback', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('redd', ['TaskStatus'])

        # Adding model 'Upload'
        db.create_table('redd_upload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('redd', ['Upload'])

        # Adding model 'Category'
        db.create_table('redd_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('redd', ['Category'])

        # Adding model 'Dataset'
        db.create_table('redd_dataset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('data_upload', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['redd.Upload'])),
            ('schema', self.gf('redd.fields.JSONField')(null=True, blank=True)),
            ('imported', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('row_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('sample_data', self.gf('redd.fields.JSONField')(null=True, blank=True)),
            ('current_task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['redd.TaskStatus'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('dialect', self.gf('redd.fields.JSONField')()),
        ))
        db.send_create_signal('redd', ['Dataset'])

        # Adding M2M table for field categories on 'Dataset'
        db.create_table('redd_dataset_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataset', models.ForeignKey(orm['redd.dataset'], null=False)),
            ('category', models.ForeignKey(orm['redd.category'], null=False))
        ))
        db.create_unique('redd_dataset_categories', ['dataset_id', 'category_id'])

        # Adding model 'Notification'
        db.create_table('redd_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', to=orm['auth.User'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(default='info', max_length=16)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('related_task', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['redd.TaskStatus'], null=True)),
            ('related_dataset', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['redd.Dataset'], null=True)),
        ))
        db.send_create_signal('redd', ['Notification'])


    def backwards(self, orm):
        
        # Deleting model 'TaskStatus'
        db.delete_table('redd_taskstatus')

        # Deleting model 'Upload'
        db.delete_table('redd_upload')

        # Deleting model 'Category'
        db.delete_table('redd_category')

        # Deleting model 'Dataset'
        db.delete_table('redd_dataset')

        # Removing M2M table for field categories on 'Dataset'
        db.delete_table('redd_dataset_categories')

        # Deleting model 'Notification'
        db.delete_table('redd_notification')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'redd.dataset': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Dataset'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'datasets'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['redd.Category']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'current_task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['redd.TaskStatus']", 'null': 'True', 'blank': 'True'}),
            'data_upload': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['redd.Upload']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dialect': ('redd.fields.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'row_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sample_data': ('redd.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'schema': ('redd.fields.JSONField', [], {'null': 'True', 'blank': 'True'})
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
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_filename': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['redd']
