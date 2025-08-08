import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импортирует ингредиенты из data/ingredients.json в базу"

    def handle(self, *args, **options):
        data_file = Path("/app/data/ingredients.json")

        if not data_file.exists():
            base_dir = Path(__file__).resolve().parents[5]
            data_file = base_dir / "data" / "ingredients.json"

        if not data_file.exists() or not data_file.is_file():
            raise CommandError(f"Файл не найден: {data_file}")

        try:
            raw = data_file.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise CommandError(f"Ошибка разбора JSON: {e}")
        except Exception as e:
            raise CommandError(f"Не удалось прочитать файл: {e}")

        ingredients = []
        for item in data:
            name = item.get("name")
            unit = item.get("measurement_unit") or item.get("measurement")
            if not name or not unit:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пропущена запись с некорректными данными: {item}"
                    )
                )
                continue
            ingredients.append(Ingredient(name=name, measurement_unit=unit))

        if not ingredients:
            self.stdout.write(
                self.style.WARNING("Нет корректных ингредиентов для импорта.")
            )
            return

        before_count = Ingredient.objects.count()
        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        after_count = Ingredient.objects.count()

        created = after_count - before_count
        self.stdout.write(
            self.style.SUCCESS(
                f"Импортировано {created} ингредиентов "
                f"out of {len(ingredients)}"
            )
        )
