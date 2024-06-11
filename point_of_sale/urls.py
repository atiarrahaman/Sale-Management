from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='core/user_login/')),
    path('',include('transaction.urls')),
    path('product/',include('product.urls')),
    path('inventory/',include('inventory.urls')),
    path('',include('pos.urls')),
    path('core/',include('core.urls')),
]
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
