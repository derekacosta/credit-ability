# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from core.models import *

admin.site.register(Account)
admin.site.register(Employment)
admin.site.register(Identification)
admin.site.register(FinancialInfo)
admin.site.register(Lease)
admin.site.register(Group)