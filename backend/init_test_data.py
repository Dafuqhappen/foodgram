import os
import sys
import django

from recipes.models import Tag, Ingredient


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')
django.setup()

def create_test_tags():
    """Создание тестовых тегов."""
    tags_data = [
        {"name": "Завтрак", "slug": "breakfast", "color": "#E26C2D"},
        {"name": "Обед", "slug": "lunch", "color": "#49B64E"},
        {"name": "Ужин", "slug": "dinner", "color": "#8775D2"},
    ]

    created_count = 0
    for tag_data in tags_data:
        tag, created = Tag.objects.get_or_create(**tag_data)
        if created:
            created_count += 1
            print(f"Создан тег: {tag.name}")
        else:
            print(f"Тег уже существует: {tag.name}")

    print(f"Создано тегов: {created_count}")
    return Tag.objects.count()


def create_test_ingredients():
    """Создание тестовых ингредиентов."""
    ingredients_data = [
        {"name": "Мука пшеничная", "measurement_unit": "г"},
        {"name": "Молоко", "measurement_unit": "мл"},
        {"name": "Яйцо куриное", "measurement_unit": "шт"},
        {"name": "Сахар", "measurement_unit": "г"},
        {"name": "Соль", "measurement_unit": "г"},
    ]

    created_count = 0
    for ingredient_data in ingredients_data:
        ingredient, created = Ingredient.objects.get_or_create(
            **ingredient_data
        )
        if created:
            created_count += 1
            print(f"Создан ингредиент: {ingredient.name}")
        else:
            print(f"Ингредиент уже существует: {ingredient.name}")
    
    print(f"Создано ингредиентов: {created_count}")
    return Ingredient.objects.count()


def main():
    """Основная функция инициализации данных."""
    print("Инициализация тестовых данных...")

    print("\n--- Создание тегов ---")
    total_tags = create_test_tags()

    print("\n--- Создание ингредиентов ---")
    total_ingredients = create_test_ingredients()

    print("\n--- Результат ---")
    print(f"Всего тегов в БД: {total_tags}")
    print(f"Всего ингредиентов в БД: {total_ingredients}")

    if total_tags >= 3 and total_ingredients >= 2:
        print("✅ Минимальные данные для тестов созданы успешно!")
    else:
        print("❌ Недостаточно данных для тестов")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
