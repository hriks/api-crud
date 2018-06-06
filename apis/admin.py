# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "reference_no", "created_by", "modified", "created")
    search_fields = ("reference_no", "length", 'height', "width")
    list_filter = ('created_by',)
    raw_id_fields = ('created_by',)
    readonly_fields = ('reference_no', 'created_by',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super(InventoryAdmin, self).save_model(request, obj, form, change)
