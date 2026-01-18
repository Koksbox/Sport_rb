# apps/core/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Кастомизация админ-сайта
admin.site.site_header = _('Административная панель СпортБаш')
admin.site.site_title = _('СпортБаш Админ')
admin.site.index_title = _('Управление системой')
