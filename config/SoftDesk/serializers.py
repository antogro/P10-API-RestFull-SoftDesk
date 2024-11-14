from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment
from authentication.models import User
from authentication.serializers import UserSerializer


class ContributorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=User.objects.all(), source="user"
    )

    class Meta:
        model = Contributor
        fields = [
            "id",
            "user",
            "user_id",
            "role"]
        read_only_fields = ["id"]
        extra_kwargs = {"project": {"required": False}}

    def validate(self, data):
        if data.get("role") == "AUTHOR":
            raise serializers.ValidationError(
                "Un auteur doit avoir la permission d'écrire"
            )

        # Vérifier si l'utilisateur est déjà contributeur
        existing_contributor = Contributor.objects.filter(
            user=data['user'],
            project=self.context['view'].kwargs['project_pk']
        ).exists()

        if existing_contributor:
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur du projet"
            )

        return data


class ProjectListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "author",
            "type",
            "created_time"
        ]
        read_only_fields = ["id", "created_time"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    contributors = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "type",
            "author",
            "contributors",
            "created_time",
        ]
        read_only_fields = [
            "id",
            "created_time"
        ]

    def get_contributors(self, obj):
        # Exclure l'auteur de la liste des contributeurs
        return ContributorSerializer(
            obj.contributors.exclude(user=obj.author),
            many=True
        ).data


class IssueListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assigne = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "author",
            "assigne",
            "created_time",
            "status",
            "project",
            "priority",
        ]
        read_only_fields = [
            "id",
            "created_time"
        ]

    def validate_assigne(self, data):
        project = self.context.get("project")
        if project and not project.contributors.filter(user=data).exists():
            raise serializers.ValidationError(
                "L'utilisateur assigné doit être un contributeur du projet"
            )
        return data


class IssueCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assigned_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigne'
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "author",
            "assigned_user",
            "priority",
            "status",
            "created_time",
            "tag",
        ]
        read_only_fields = ["id", "created_time"]

    def validate_assigned_user(self, data):
        project = self.context.get("project")
        if project and not project.contributors.filter(user=data).exists():
            raise serializers.ValidationError(
                "L'utilisateur assigné doit être un contributeur du projet"
            )
        return data


class IssueDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assigne = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            'author',
            "assigne",
            "project",
            "priority",
            "status",
            "created_time",
            "tag",
        ]
        read_only_fields = ["id", "created_time"]

    def validate_assigne(self, data):
        project = self.context.get("project")
        if project and not project.contributors.filter(user=data).exists():
            raise serializers.ValidationError(
                "L'utilisateur assigné doit être un contributeur du projet"
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    issue = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "description",
            "author",
            "issue",
            "created_time",
            "uuid"
        ]
        read_only_fields = ["id", "created_time", "uuid"]

    def validate_author(self, data):
        project = self.context.get("project")
        if project and not project.contributors.filter(user=data).exists():
            raise serializers.ValidationError(
                "L'auteur doit être un contributeur du projet"
            )
        return data
