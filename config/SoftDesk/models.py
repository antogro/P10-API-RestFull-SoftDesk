from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
import uuid


class Project(models.Model):
    """
    Projet SoftDesk regroupant des issues et contributeurs.

    L'auteur est unique et supprimé en cascade. Le type peut être
    BACKEND, FRONTEND, IOS ou ANDROID.
    """

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

    def __str__(self):
        return self.title


class Contributor(models.Model):
    """
    Association entre un utilisateur et un projet avec un rôle.

    Chaque projet a un unique auteur et peut avoir plusieurs contributeurs.
    Un utilisateur ne peut contribuer qu'une fois par projet.
    """
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

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'project'],
                name='unique_contributor_per_contribution',
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.title}"


class Issue(models.Model):
    """
    Problème ou tâche à réaliser dans un projet.

    Assignée à un contributeur du projet, avec une priorité (LOW/MEDIUM/HIGH),
    un statut (TODO/IN_PROGRESS/FINISHED) et un type (BUG/FEATURE/TASK).
    """

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
        default='TASK'
    )

    created_time = models.DateTimeField(
        auto_now_add=True)

    def clean(self):
        if not self.project.contributors.filter(user=self.assigne).exists():
            raise ValidationError(
                'l\'assignée doit être un contributeur du projet'
            )

    def __str__(self):
        return f"{self.title} - {self.project.title}"


class Comment(models.Model):
    """
    Commentaire sur une issue par un contributeur du projet.

    Identifié par un UUID unique et non modifiable.
    L'auteur doit être un contributeur du projet associé.
    """
    description = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_comment',
        to_field='uuid'
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
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    def clean(self):
        if not self.project.contributors.filter(user=self.author).exists():
            raise ValidationError(
                'l\'assignée doit être un contributeur du projet'
            )

    def __str__(self):
        return f"Comment {self.uuid} on {self.issue.title}"
