# Generated by Django 5.1.3 on 2024-11-14 14:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('SoftDesk', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_comment', to=settings.AUTH_USER_MODEL, to_field='uuid'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='issue',
            name='assigne',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_issue', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='issue',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_issue', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='SoftDesk.issue'),
        ),
        migrations.AddField(
            model_name='project',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_projects', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='SoftDesk.project'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributors', to='SoftDesk.project'),
        ),
        migrations.AddConstraint(
            model_name='contributor',
            constraint=models.UniqueConstraint(fields=('user', 'project'), name='unique_contributor_per_contribution'),
        ),
    ]
