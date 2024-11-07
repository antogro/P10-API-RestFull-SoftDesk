from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint, Q
from django.core.exceptions import ValidationError
import uuid
# Create your models here.


class Project(models.Model):
    TYPE_CHOICES = [
        ('BACKEND', 'Back-end'),
        ('FRONTEND', 'Front-end'),
        ('IOS', 'ios'),
        ('ANDROID', 'Android'),
    ]
    title = models.CharField(
        max_length=200)
    description = models.TextField()
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_projects')
    created_time = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['title', 'author'],
                name='unique_project_per_author'
            )
        ]

    def __str__(self):
        return self.title


class Contributor(models.Model):
    PERMISSION_CHOICES = [
        ('READ', 'Lecture'),
        ('WRITE', 'Écriture')
    ]
    ROLE_CHOICE = [
        ('AUTHOR', 'Auteur'),
        ('CONTRIBUTOR', 'Contributeur')
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contributors'
    )
    permission = models.CharField(
        max_length=5,
        choices=PERMISSION_CHOICES,
        default='READ'
    )
    role = models.CharField(
        max_length=11,
        choices=ROLE_CHOICE,
        default='CONTRIBUTOR'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'project'],
                name='unique_contributor_per_contribution',
            ),
            UniqueConstraint(
                fields=['project'],
                condition=Q(role='AUTHOR'),
                name='one_author_per_project',
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"

    def clean(self):
        if self.role == 'AUTHOR' and self.permission != 'WRITE':
            raise ValidationError(
                'Un auteur doit avoir la permission d\'écrire'
                )


class Issue(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Elevé')
    ]
    STATUS_CHOICES = [
        ('TODO', 'À faire'),
        ('IN_PROGRESS', 'En cours'),
        ('FINISHED', 'Terminé')
    ]
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Fonctionnalité'),
        ('TASK', 'Tâche')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='issues'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_issue'
    )
    assigne = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_issue'
    )
    priority = models.CharField(
        max_length=6,
        choices=PRIORITY_CHOICES,
        default='LOW'
    )
    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default='TODO'
    )
    tag = models.CharField(
        max_length=7,
        choices=TAG_CHOICES,
        default='Task'
    )

    created_time = models.DateTimeField(
        auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['title', 'project'],
                name='unique_issue_title_per_project'
            )
        ]

    def clean(self):
        if not self.project.contributors.filter(user=self.assigne).exists():
            raise ValueError('l\'assignée doit être un contributeur du projet')

    def __str__(self):
        return f"{self.title} - {self.project.title}"


class Comment(models.Model):
    description = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_comment'
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_time = models.DateTimeField(
        auto_now_add=True
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    def clean(self):
        if not self.project.contributors.filter(user=self.author).exists():
            raise ValueError('l\'assignée doit être un contributeur du projet')

    def __str__(self):
        return f"Comment {self.uuid} on {self.issue.title}"
