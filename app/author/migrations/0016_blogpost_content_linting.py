from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0015_postreview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpostmodel',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='blogpostmodel',
            name='content',
            field=models.TextField(max_length=50000),
        ),
    ]
