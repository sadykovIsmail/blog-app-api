from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('author', '0023_blogpost_pinned')]
    operations = [
        migrations.CreateModel(
            name='PostView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_hash', models.CharField(max_length=64)),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_views', to='author.blogpostmodel')),
            ],
            options={'unique_together': {('post', 'ip_hash')}},
        ),
    ]
