from django.db import models
from django.db.models import F, Q


class Building(models.Model):
    name = models.CharField("название", max_length=100, unique=True)   
    address = models.CharField("адрес", max_length=255, blank=True)    

    class Meta:
        db_table = "buildings"            
        verbose_name = "корпус"           
        verbose_name_plural = "корпуса"
        ordering = ["name"]               

    def __str__(self):                    
        return self.name


class Equipment(models.Model):
    name = models.CharField("название", max_length=100, unique=True)

    class Meta:
        db_table = "equipment"
        verbose_name = "оборудование"
        verbose_name_plural = "оборудование"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    building = models.ForeignKey(
        Building, on_delete=models.PROTECT, related_name="rooms", verbose_name="корпус"
    )
    number = models.CharField("номер", max_length=32)          
    capacity = models.PositiveIntegerField("вместимость")
    equipment = models.ManyToManyField(
        Equipment, blank=True, related_name="rooms", verbose_name="оборудование",
        db_table="room_equipment",
    )
    description = models.TextField("описание", blank=True)
    is_active = models.BooleanField("доступна для брони", default=True)

    class Meta:
        db_table = "rooms"
        verbose_name = "аудитория"
        verbose_name_plural = "аудитории"
        ordering = ["building__name", "number"]
        constraints = [
            models.UniqueConstraint(fields=["building", "number"], name="uniq_room_number_in_building"),
        ]

    def __str__(self):
        return f"{self.building.name}, {self.number}"


class Lesson(models.Model):

    class Source(models.TextChoices):
        GROUP_SCRIPT = "group_script", "Скрипт расписания групп"
        TEACHER_SCRIPT = "teacher_script", "Скрипт расписания преподавателя"
        MANUAL = "manual", "Вручную"

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="lessons", verbose_name="аудитория")
    start = models.DateTimeField("начало")   
    end = models.DateTimeField("конец")
    subject = models.CharField("дисциплина", max_length=255)
    lesson_type = models.CharField("тип (ЛК, ПЗ, ЛР…)", max_length=16, blank=True)
    teacher = models.CharField("преподаватель", max_length=255, blank=True)
    groups = models.CharField("группы", max_length=500, blank=True)
    source = models.CharField("источник", max_length=20, choices=Source.choices, default=Source.MANUAL)

    class Meta:
        db_table = "lessons"
        verbose_name = "занятие"
        verbose_name_plural = "занятия"
        ordering = ["start"]
        constraints = [
            models.CheckConstraint(condition=Q(start__lt=F("end")), name="lesson_start_before_end"),
            models.UniqueConstraint(fields=["room", "start", "end"], name="uniq_lesson_slot"),
        ]

    def __str__(self):
        return f"{self.subject} ({self.room}, {self.start:%d.%m %H:%M})"