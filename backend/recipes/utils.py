def table_recipes(ingredients):
    str_ing = "Ингредиенты |  Количество | Единицы измерения \n\n"
    str_ing += "________________________________________________"
    for i in ingredients:
        str_ing += f"\n{i['ingredient__name']} | " \
                   f"{i['amount__sum']} | " \
                   f"{i['ingredient__measurement_unit']} \n"
    return str_ing
