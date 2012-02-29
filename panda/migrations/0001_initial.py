# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('panda_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=256, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('panda', ['Category'])

        # Adding model 'TaskStatus'
        db.create_table('panda_taskstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(default='PENDING', max_length=50)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('traceback', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('panda', ['TaskStatus'])

        # Adding model 'Dataset'
        db.create_table('panda_dataset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=256, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('initial_upload', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='initial_upload_for', null=True, to=orm['panda.DataUpload'])),
            ('columns', self.gf('panda.fields.JSONField')(default=None, null=True)),
            ('sample_data', self.gf('panda.fields.JSONField')(default=None, null=True)),
            ('row_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('current_task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['panda.TaskStatus'], null=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='datasets', to=orm['auth.User'])),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('last_modification', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('panda', ['Dataset'])

        # Adding M2M table for field categories on 'Dataset'
        db.create_table('panda_dataset_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataset', models.ForeignKey(orm['panda.dataset'], null=False)),
            ('category', models.ForeignKey(orm['panda.category'], null=False))
        ))
        db.create_unique('panda_dataset_categories', ['dataset_id', 'category_id'])

        # Adding model 'DataUpload'
        db.create_table('panda_dataupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data_uploads', null=True, to=orm['panda.Dataset'])),
            ('data_type', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('encoding', self.gf('django.db.models.fields.CharField')(default='utf-8', max_length=32)),
            ('dialect', self.gf('panda.fields.JSONField')(null=True)),
            ('columns', self.gf('panda.fields.JSONField')(null=True)),
            ('sample_data', self.gf('panda.fields.JSONField')(null=True)),
            ('imported', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('panda', ['DataUpload'])

        # Adding model 'Export'
        db.create_table('panda_export', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='exports', to=orm['panda.Dataset'])),
        ))
        db.send_create_signal('panda', ['Export'])

        # Adding model 'Notification'
        db.create_table('panda_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifications', to=orm['auth.User'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(default='Info', max_length=16)),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
            ('related_task', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['panda.TaskStatus'], null=True)),
            ('related_dataset', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['panda.Dataset'], null=True)),
        ))
        db.send_create_signal('panda', ['Notification'])

        # Adding model 'RelatedUpload'
        db.create_table('panda_relatedupload', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('original_filename', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related_uploads', to=orm['panda.Dataset'])),
        ))
        db.send_create_signal('panda', ['RelatedUpload'])

        # Adding model 'UserProfile'
        db.create_table('panda_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('activation_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('panda', ['UserProfile'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('panda_category')

        # Deleting model 'TaskStatus'
        db.delete_table('panda_taskstatus')

        # Deleting model 'Dataset'
        db.delete_table('panda_dataset')

        # Removing M2M table for field categories on 'Dataset'
        db.delete_table('panda_dataset_categories')

        # Deleting model 'DataUpload'
        db.delete_table('panda_dataupload')

        # Deleting model 'Export'
        db.delete_table('panda_export')

        # Deleting model 'Notification'
        db.delete_table('panda_notification')

        # Deleting model 'RelatedUpload'
        db.delete_table('panda_relatedupload')

        # Deleting model 'UserProfile'
        db.delete_table('panda_userprofile')


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
