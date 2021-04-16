from django.contrib import admin

from inventory.models import Store, Product, MaterialQuantity, Material, MaterialStock


admin.site.register(Store)
admin.site.register(Product)
admin.site.register(MaterialQuantity)
admin.site.register(Material)
admin.site.register(MaterialStock)
