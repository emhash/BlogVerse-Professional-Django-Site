from django.urls import path, re_path
# from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from home import views



urlpatterns = [
    
    path('', views.home, name="homes"),
    path('<slug:slg>/', views.f404, name="homes"),
    path('registration/', views.Registration, name= "the_signup"),
    path('login/', views.the_login, name= "the_login"),
    path('logout/', views.the_logout, name= "logout"),
    path('dashboard/', views.the_dashb, name= "the_dashb"),
    path('dashboard/<str:option>/', views.dynamic_option, name="dynamic_option"),
    path('contact/', views.feedback, name= "the_about"),
    path('artical/<slug:the_artical>/', views.artical_view, name='artical'),
    path('dashboard/your_posts/<slug:key>/', views.edit_post, name='edit_post'),
    path('delete_post/<slug:slug>/', views.delete_post, name='delete_post'),
    path('dashboard/your_posts/', views.your_posts, name='your_posts'),
    


# -------- Not 404 hanlder But showing 404 by redirecting to 404 if none of page clicked here -------
    # path('404/', views.f404, name= "404"),
    # re_path(r'^.*$', RedirectView.as_view(url='/404/')),

# ------------------------------------------------------------------------------



]


if not settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
