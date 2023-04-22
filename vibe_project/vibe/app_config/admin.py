from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Variables, Refills, Cities, Schools, Questions, Administrators


class VariablesAdmin(admin.ModelAdmin):
    list_display = ['id', 'variable', 'value']
    list_display_links = ['id', 'variable', 'value']


class RefillsAdmin(admin.ModelAdmin):
    list_display = ['crystal', 'price', 'percent']
    list_display_links = ['crystal', 'price', 'percent']


class CitiesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']
    list_display_links = ['id', 'title']


class SchoolsAdmin(admin.ModelAdmin):
    list_display = ['id', 'city', 'title']
    list_display_links = ['id', 'city', 'title']


class QuestionsAdmin(admin.ModelAdmin):
    list_display = ['question', 'get_image']
    list_display_links = ['question', 'get_image']
    readonly_fields = ['get_image']
    fields = ['question', ('image', 'get_image')]

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="140" height="140"')

    get_image.short_description = 'Изображение'


class AdministratorsAdmin(admin.ModelAdmin):
    list_display = ['user_id']
    list_display_links = ['user_id']


admin.site.register(Variables, VariablesAdmin)
admin.site.register(Refills, RefillsAdmin)
admin.site.register(Cities, CitiesAdmin)
admin.site.register(Schools, SchoolsAdmin)
admin.site.register(Questions, QuestionsAdmin)
admin.site.register(Administrators, AdministratorsAdmin)


admin.site.site_header = 'VIBE'
admin.site.site_title = 'VIBE'
