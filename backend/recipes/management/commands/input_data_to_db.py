class Command(BaseCommand):
    def handle(self, *args, **options):
        Ingredient.objects.all().delete()
        with open("./ingredients.json", encoding="utf-8") as file:
            reader = json.load(file)
            counter = 0
            for row in reader:
                Ingredient.objects.create(
                    name=row["name"],
                    measurement_unit=row["measurement_unit"]
                )
                counter += 1
        for elem in tag:
            Tag.objects.get_or_create(
                name=elem["name"],
                color=elem["color"],
                slug=elem["slug"],
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"В базу добавлено {counter} ингредиентов и теги"
            )
        )