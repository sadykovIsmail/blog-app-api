from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0004_blogpostmodel_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpostmodel',
            name='status',
            field=models.CharField(
                choices=[
                    ('DRAFT', 'Draft'),
                    ('SCHEDULED', 'Scheduled'),
                    ('PUBLISHED', 'Published'),
                    ('ARCHIVED', 'Archived'),
                ],
                default='DRAFT',
                max_length=10,
            ),
        ),
    ]
