import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0011_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('url', models.URLField(max_length=2000)),
                ('title', models.CharField(blank=True, max_length=500)),
                ('publisher', models.CharField(blank=True, max_length=255)),
                ('published_at', models.DateField(blank=True, null=True)),
                ('accessed_at', models.DateField(auto_now_add=True)),
                ('http_status', models.IntegerField(blank=True, null=True)),
                ('checked_at', models.DateTimeField(blank=True, null=True)),
                ('canonical_url', models.URLField(blank=True, max_length=2000)),
                ('content_hash', models.CharField(blank=True, max_length=64)),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='citations',
                    to='author.blogpostmodel',
                )),
            ],
        ),
    ]
