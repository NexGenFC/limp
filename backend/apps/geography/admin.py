from django.contrib import admin

from apps.geography.models import District, Hobli, Taluk, Village


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "state")
    search_fields = ("name",)


@admin.register(Taluk)
class TalukAdmin(admin.ModelAdmin):
    list_display = ("name", "district")
    list_filter = ("district",)
    search_fields = ("name",)


@admin.register(Hobli)
class HobliAdmin(admin.ModelAdmin):
    list_display = ("name", "taluk")
    list_filter = ("taluk__district",)
    search_fields = ("name",)


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ("name", "hobli")
    list_filter = ("hobli__taluk__district",)
    search_fields = ("name",)
