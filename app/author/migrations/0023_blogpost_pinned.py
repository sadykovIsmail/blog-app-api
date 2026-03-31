from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0022_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpostmodel',
            name='pinned',
            field=models.BooleanField(default=False),
        ),
    ]
