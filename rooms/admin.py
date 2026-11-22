from django.contrib import admin

from .models import Building, Equipment, Lesson, Room


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ("name", "address")       
    search_fields = ("name",)                


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "building", "capacity", "is_active")
    list_filter = ("building", "is_active", "equipment")  
    search_fields = ("number",)
    filter_horizontal = ("equipment",)      


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("subject", "lesson_type", "room", "start", "end", "source")
    list_filter = ("source", "lesson_type", "room__building")
    search_fields = ("subject", "teacher", "groups", "room__number")
    date_hierarchy = "start"              
    autocomplete_fields = ("room",)         