import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0016_blogpost_content_linting'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ModerationAuditLog',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('action', models.CharField(max_length=50)),
                ('target_type', models.CharField(blank=True, max_length=50)),
                ('target_id', models.PositiveIntegerField(blank=True, null=True)),
                ('note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='moderation_actions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID',
                )),
                ('target_type', models.CharField(
                    choices=[('post', 'Post'), ('comment', 'Comment')], max_length=10,
                )),
                ('reason', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reporter', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reports_filed',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('post', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reports',
                    to='author.blogpostmodel',
                )),
                ('comment', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reports',
                    to='author.comment',
                )),
            ],
        ),
    ]
