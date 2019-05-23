from django.urls import path, reverse_lazy
from . import views
from django.views.generic import FormView


urlpatterns = [
    path('', views.SocialView.as_view()),
    path('social', views.SocialView.as_view(), name='social'),
    path('social/<int:pk>', views.SocialDetailView.as_view(), name='social_detail'),
    path('social/create',
        views.SocialCreateView.as_view(success_url=reverse_lazy('socials')), name='social_create'),
    path('social/<int:pk>/update',
        views.SocialUpdateView.as_view(success_url=reverse_lazy('socials')), name='social_update'),
    path('social/<int:pk>/delete',
        views.SocialDeleteView.as_view(success_url=reverse_lazy('socials')), name='social_delete'),
    path('social_picture/<int:pk>', views.stream_file, name='social_picture'),
    path('social/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('socials')), name='comment_delete'),
    path('social/<int:pk>/favorite',
        views.AddFavoriteView.as_view(), name='social_favorite'),
    path('social/<int:pk>/unfavorite',
        views.DeleteFavoriteView.as_view(), name='social_unfavorite'),

]