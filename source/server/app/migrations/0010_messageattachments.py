from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_answerlogs_idx_answerlogs_student_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageAttachments',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='记录编号')),
                ('file', models.FileField(upload_to='message_attachments/', verbose_name='附件文件')),
                ('name', models.CharField(max_length=255, verbose_name='原文件名')),
                ('size', models.IntegerField(null=True, verbose_name='文件大小')),
                ('uploadTime', models.DateTimeField(auto_now_add=True, verbose_name='上传时间')),
                ('message', models.ForeignKey(db_column='message_id', on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='app.messages')),
            ],
            options={
                'db_table': 'fater_message_attachments',
            },
        ),
    ]


