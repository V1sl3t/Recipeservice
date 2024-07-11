def create_shopping_list(ingredients_queryset):
    shopping_list = ['Список покупок:\n']
    for ingredient in ingredients_queryset:
        name = ingredient['ingredient__name']
        unit = ingredient['ingredient__measurement_unit']
        amount = ingredient['ingredient_amount']
        shopping_list.append(f'\n{name} - {amount}, {unit}')
    return shopping_list
