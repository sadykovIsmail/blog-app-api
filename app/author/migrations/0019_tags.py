from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0018_blogpost_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=60, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='blogpostmodel',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='posts', to='author.tag'),
        ),
    ]
