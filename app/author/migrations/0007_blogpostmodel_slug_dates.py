from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0006_blogpostmodel_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpostmodel',
            name='slug',
            field=models.SlugField(blank=True, max_length=270, unique=True),
        ),
        migrations.AddField(
            model_name='blogpostmodel',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='blogpostmodel',
            name='scheduled_for',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
