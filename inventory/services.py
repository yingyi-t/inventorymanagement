from django.core.exceptions import ObjectDoesNotExist

from inventory.models import MaterialQuantity


def get_product_available_quantity(obj):
    material_quantities = MaterialQuantity.objects.filter(product=obj.product_id)
    material_quantities_list = []

    for material_quantity in material_quantities:
        quantity_needed = material_quantity.quantity
        quantity_available = 0

        try:
            stock = obj.store_set.get().material_stocks.get(
                material=material_quantity.ingredient
            )
            quantity_available = stock.current_capacity
        except ObjectDoesNotExist:
            pass

        material_quantities_list.append(int(quantity_available / quantity_needed))

    return min(material_quantities_list)
