import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = (
        "Импортирует ингредиенты из fixtures.json (если есть) или из "
        "data/ingredients.json"
    )

    def _read_json(self, path: Path):
        try:
            raw = path.read_text(encoding="utf-8")
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Ошибка разбора JSON: {exc}")
        except Exception as exc:
            raise CommandError(f"Не удалось прочитать файл: {exc}")

    def handle(self, *args, **options):
        fixtures_path = Path("/app/fixtures.json")
        data_dir = Path("/app/data")
        ingredients_path = data_dir / "ingredients.json"

        data = None
        source = None

        if fixtures_path.exists():
            all_items = self._read_json(fixtures_path)
            data = [
                {
                    "name": item.get("fields", {}).get("name"),
                    "measurement_unit": item.get("fields", {}).get(
                        "measurement_unit"
                    ),
                }
                for item in all_items
                if item.get("model") == "recipes.ingredient"
            ]
            source = "fixtures.json"

        # 2) Фолбэк к data/ingredients.json
        if not data:
            if not ingredients_path.exists():
                # попытка найти локально вне контейнера
                base_dir = Path(__file__).resolve().parents[5]
                fallback = base_dir / "data" / "ingredients.json"
                ingredients_path = fallback

            if not ingredients_path.exists() or not ingredients_path.is_file():
                raise CommandError(
                    "Не найден ни fixtures.json, ни data/ingredients.json"
                )

            data = self._read_json(ingredients_path)
            source = str(ingredients_path)

        ingredients_to_create = []
        for item in data:
            name = item.get("name")
            unit = item.get("measurement_unit") or item.get("measurement")
            if not name or not unit:
                self.stdout.write(
                    self.style.WARNING(
                        f"Пропущена некорректная запись: {item}"
                    )
                )
                continue
            ingredients_to_create.append(
                Ingredient(name=name, measurement_unit=unit)
            )

        if not ingredients_to_create:
            self.stdout.write(
                self.style.WARNING("Нет корректных ингредиентов для импорта.")
            )
            return

        before = Ingredient.objects.count()
        Ingredient.objects.bulk_create(
            ingredients_to_create, ignore_conflicts=True
        )
        after = Ingredient.objects.count()
        created = after - before

        self.stdout.write(
            self.style.SUCCESS(
                f"Источник: {source}. Импортировано {created} из "
                f"{len(ingredients_to_create)}"
            )
        )
