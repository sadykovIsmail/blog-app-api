import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0013_notification_citation_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostVersion',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('version_number', models.PositiveIntegerField()),
                ('title_snapshot', models.CharField(max_length=255)),
                ('content_snapshot', models.TextField()),
                ('reason_for_change', models.TextField(blank=True)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='versions',
                    to='author.blogpostmodel',
                )),
            ],
            options={
                'ordering': ['version_number'],
                'unique_together': {('post', 'version_number')},
            },
        ),
    ]
