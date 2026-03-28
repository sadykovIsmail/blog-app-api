from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0005_blogpostmodel_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpostmodel',
            name='visibility',
            field=models.CharField(
                choices=[('PUBLIC', 'Public'), ('UNLISTED', 'Unlisted')],
                default='PUBLIC',
                max_length=10,
            ),
        ),
    ]
