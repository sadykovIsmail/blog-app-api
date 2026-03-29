from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0012_citation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=[
                    ('follow', 'Follow'),
                    ('comment', 'Comment'),
                    ('reply', 'Reply'),
                    ('new_post', 'New Post'),
                    ('citation_dead', 'Citation Dead'),
                    ('citation_drift', 'Citation Drift'),
                ],
                max_length=20,
            ),
        ),
    ]
