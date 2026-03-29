from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0017_moderation'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='blogpostmodel',
            index=models.Index(fields=['status', 'visibility'], name='author_blog_status_vis_idx'),
        ),
        migrations.AddIndex(
            model_name='blogpostmodel',
            index=models.Index(fields=['-published_at'], name='author_blog_published_at_idx'),
        ),
    ]
