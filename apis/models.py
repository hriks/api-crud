# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.db import models
import uuid

ALLOWED_CHARS = '34HRIKS56789'


class Inventory(models.Model):
    """Add Unit"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_no = models.CharField(max_length=20, null=True, blank=True)
    length = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    created_by = models.ForeignKey(User)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.reference_no is None:
            self.assignReferenceNumber()
        super(Inventory, self).save(*args, **kwargs)

    @classmethod
    def addInventory(cls, *args, **kwargs):
        return cls.objects.create(*args, **kwargs)

    def assignReferenceNumber(self):
        temp_ref = 'Inventory:' + get_random_string(
            10, allowed_chars=ALLOWED_CHARS)
        while Inventory.objects.filter(reference_no=temp_ref).exists():
            temp_ref = 'Inventory:' + get_random_string(
                10, allowed_chars=ALLOWED_CHARS)
        self.reference_no = temp_ref

    def getVolume(self):
        return self.length * self.width * self.height

    def getArea(self):
        return
