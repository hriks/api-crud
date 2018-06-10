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
    length = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    created_by = models.ForeignKey(User, null=True, blank=True)
    modified = models.DateTimeField(auto_now=True)
    volume = models.FloatField(default=0.0)
    area = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.reference_no is None:
            self.assignReferenceNumber()
        self.volume = self.getVolume()
        self.area = self.getAarea()
        super(Inventory, self).save(*args, **kwargs)

    @classmethod
    def addBox(cls, *args, **kwargs):
        return cls.objects.create(*args, **kwargs)

    def update(self, data):
        if data.get('height'):
            self.height = float(data.get('height'))
        if data.get('width'):
            self.width = float(data.get('width'))
        if data.get('length'):
            self.length = float(data.get('length'))
        self.save()

    def assignReferenceNumber(self):
        temp_ref = 'Inventory:' + get_random_string(
            10, allowed_chars=ALLOWED_CHARS)
        while Inventory.objects.filter(reference_no=temp_ref).exists():
            temp_ref = 'Inventory:' + get_random_string(
                10, allowed_chars=ALLOWED_CHARS)
        self.reference_no = temp_ref

    def getVolume(self):
        return self.length * self.width * self.height

    def getAarea(self):
        return 2 * ((
            self.length * self.width
        ) + (
            self.length * self.height
        ) + (
            self.height * self.width
        ))

    def __unicode__(self):
        return "%s : %s" % (self.created_by, self.created)
