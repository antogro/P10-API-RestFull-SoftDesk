from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers
from authentication.views import UserViewSet, RegisterViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from SoftDesk.views import (
    ContributorViewSet,
    ProjectViewset,
    IssueViewSet,
    CommentViewSet,
)

# Routeur principal pour les projets
router = routers.SimpleRouter()
router.register(r"projects", ProjectViewset, basename="projects")
router.register(r"users", UserViewSet)

# Routeur imbriqué pour les contributeurs et les issues
project_router = routers.NestedSimpleRouter(
    router,
    r"projects",
    lookup="project")
project_router.register(
    r"contributors", ContributorViewSet, basename="project-contributors"
)
project_router.register(r"issues", IssueViewSet, basename="project-issues")

# Routeur imbriqué pour les commentaires
issue_router = routers.NestedSimpleRouter(
    project_router,
    r"issues",
    lookup="issue")
issue_router.register(r"comments", CommentViewSet, basename="issue-comments")

urlpatterns = [
    path("signup/", RegisterViewSet.as_view(), name="signup"),
    path("api/", include(router.urls)),
    path("api/", include(project_router.urls)),
    path("api/", include(issue_router.urls)),
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path("admin/", admin.site.urls),
    path(
        'issues/<uuid:issue_pk>/comments/<uuid:uuid>/',
        CommentViewSet.as_view({'get': 'retrieve'}),
        name='comment-detail'
    ),
]
