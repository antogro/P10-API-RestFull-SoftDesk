# Generated by Django 5.1.2 on 2024-11-04 13:06

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('LOW', 'Faible'), ('MEDIUM', 'Moyen'), ('HIGH', 'Elevé')], default='LOW', max_length=6)),
                ('status', models.CharField(choices=[('TODO', 'À faire'), ('IN_PROGRESS', 'En cours'), ('FINISHED', 'Terminé')], default='TODO', max_length=11)),
                ('tag', models.CharField(choices=[('BUG', 'Bug'), ('Feature', 'Fonctionnalité'), ('TASK', 'Tâche')], default='Task', max_length=7)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('assigne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_issue', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_issue', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_comment', to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='SoftDesk.issue')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('BACKEND', 'Back-end'), ('FRONTEND', 'Front-end'), ('IOS', 'ios'), ('ANDROID', 'Android')], max_length=10)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='SoftDesk.project'),
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.CharField(choices=[('READ', 'Lecture'), ('WRITE', 'Écriture')], default='READ', max_length=5)),
                ('role', models.CharField(choices=[('AUTHOR', 'Auteur'), ('CONTRIBUTOR', 'Contributeur')], default='CONTRIBUTOR', max_length=11)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributors', to='SoftDesk.project')),
            ],
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('title', 'author'), name='unique_project_per_author'),
        ),
        migrations.AddConstraint(
            model_name='issue',
            constraint=models.UniqueConstraint(fields=('title', 'project'), name='unique_issue_title_per_project'),
        ),
        migrations.AddConstraint(
            model_name='contributor',
            constraint=models.UniqueConstraint(fields=('user', 'project'), name='unique_contributor_per_contribution'),
        ),
        migrations.AddConstraint(
            model_name='contributor',
            constraint=models.UniqueConstraint(condition=models.Q(('role', 'AUTHOR')), fields=('project',), name='one_author_per_project'),
        ),
    ]
