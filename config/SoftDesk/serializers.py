from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment
from authentication.models import User
from authentication.serializers import UserSerializer


class ContributorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=User.objects.all(),
        source='user'
    )

    class Meta:
        model = Contributor
        fields = [
            'id',
            'user',
            'user_id',
            'project',
            'permission',
            'role',
        ]
        read_only_fields = ['id']
        extra_kwargs = {'project': {'required': False}}

    def validate(self, data):

        if data.get('role') == 'AUTHOR' and data.get('permission') != 'WRITE':
            raise serializers.ValidationError(
                'Un auteur doit avoir la permission d\'écrire'
            )
        return data


class ProjectListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'author',
            'type',
            'created_time'
        ]
        read_only_fields = ['id', 'created_time']


class ProjectDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    contributors = ContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'type',
            'author',
            'contributors',
            'created_time',
        ]
        read_only_fields = ['id', 'created_time']

    def create(self, validated_data):
        project = super().create(validated_data)
        Contributor.objects.create(
            user=validated_data['author'],
            project=project,
            role='AUTHOR',
            permission='WRITE',
        )
        return project


class IssueListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assigne = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id',
            'title',
            'author',
            'assigne',
            'created_time',
            'status',
            'priority',
            ]
        read_only_fields = ['id', 'created_time']

    def validate_assigne(self, data):
        project = self.context['project']
        if not project.contributors.filter(user=data).exists():
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
            'id',
            'title',
            'description',
            'assigne',
            'project',
            'priority',
            'status',
            'created_time',
            'tag'
        ]
        read_only_fields = ['id', 'created_time']

    def validate_assigne(self, data):
        project = self.context['project']
        if not project.contributors.filter(user=data).exists():
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
            'id',
            'description',
            'author',
            'issue',
            'created_time',
            'uuid',
        ]
        read_only_fields = ['id', 'created_time', 'uuid']

    def validate_author(self, data):
        project = self.context['project']
        if not project.contributors.filter(user=data).exists():
            raise serializers.ValidationError(
                "L'auteur doit être un contributeur du projet"
            )
        return data
