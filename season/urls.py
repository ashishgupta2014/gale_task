from rest_framework.routers import SimpleRouter

from season.api_resource.api_view import StatsViewSet

router = SimpleRouter()
router.register(r'stats', StatsViewSet, basename='season')
urlpatterns = router.urls
