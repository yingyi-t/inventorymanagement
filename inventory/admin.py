from django.contrib import admin

from inventory.models import (Material, MaterialQuantity, MaterialStock,
                              Product, Store)

admin.site.register(Store)
admin.site.register(Product)
admin.site.register(MaterialQuantity)
admin.site.register(Material)
admin.site.register(MaterialStock)
