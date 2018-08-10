# Generated by Django 2.0.6 on 2018-08-15 12:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articles', '0011_articlelikes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_title', models.CharField(db_index=True, max_length=255)),
                ('notification_body', models.CharField(db_index=True, max_length=255)),
                ('read_status', models.BooleanField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('article_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article')),
                ('notification_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
