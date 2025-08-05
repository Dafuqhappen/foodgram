from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


User = get_user_model()


class Command(BaseCommand):
    help = 'Настройка проекта для проверки ревьюером'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Настройка проекта для проверки ревьюером...')
        )
        self.stdout.write('=' * 50)

        self.create_review_user()
        self.stdout.write('')

        self.create_test_data()
        self.stdout.write('')

        # Статистика
        self.stdout.write('📊 Статистика:')
        self.stdout.write(f'   Пользователей: {User.objects.count()}')
        self.stdout.write(f'   Рецептов: {Recipe.objects.count()}')
        self.stdout.write(f'   Тегов: {Tag.objects.count()}')
        self.stdout.write(f'   Ингредиентов: {Ingredient.objects.count()}')

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('✅ Настройка завершена!')
        )
        self.stdout.write('')
        self.stdout.write('🔑 Данные для входа в админку:')
        self.stdout.write('   Логин: review')
        self.stdout.write('   Пароль: review1admin')
        self.stdout.write('   Email: review@admin.ru')

    def create_review_user(self):
        """Создает суперпользователя для ревьюера."""
        try:
            if not User.objects.filter(username='review').exists():
                user = User.objects.create_superuser(
                    username='review',
                    email='review@admin.ru',
                    password='review1admin',
                    first_name='Review',
                    last_name='Admin'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Создан суперпользователь: {user.username}')
                )
            else:
                self.stdout.write('ℹ️  Пользователь review уже существует')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка создания пользователя: {e}')
            )

    def create_test_data(self):
        """Создает тестовые данные: теги, ингредиенты, пользователей и рецепты."""
        # Создаем теги
        tags_data = [
            {'name': 'Завтрак', 'slug': 'breakfast'},
            {'name': 'Обед', 'slug': 'lunch'},
            {'name': 'Ужин', 'slug': 'dinner'},
            {'name': 'Десерт', 'slug': 'dessert'},
            {'name': 'Напитки', 'slug': 'drinks'},
        ]

        tags = {}
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults={'name': tag_data['name']}
            )
            tags[tag.slug] = tag
            if created:
                self.stdout.write(f'✅ Создан тег: {tag.name}')

        # Создаем ингредиенты
        ingredients_data = [
            {'name': 'Мука', 'measurement_unit': 'г'},
            {'name': 'Яйца', 'measurement_unit': 'шт'},
            {'name': 'Молоко', 'measurement_unit': 'мл'},
            {'name': 'Сахар', 'measurement_unit': 'г'},
            {'name': 'Сливочное масло', 'measurement_unit': 'г'},
            {'name': 'Соль', 'measurement_unit': 'г'},
            {'name': 'Перец', 'measurement_unit': 'г'},
            {'name': 'Помидоры', 'measurement_unit': 'шт'},
            {'name': 'Огурцы', 'measurement_unit': 'шт'},
            {'name': 'Лук', 'measurement_unit': 'шт'},
        ]

        ingredients = {}
        for ing_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ing_data['name'],
                defaults={'measurement_unit': ing_data['measurement_unit']}
            )
            ingredients[ingredient.name] = ingredient
            if created:
                self.stdout.write(f'✅ Создан ингредиент: {ingredient.name}')

        # Создаем пользователей
        users_data = [
            {
                'username': 'chef_master',
                'email': 'chef@example.com',
                'first_name': 'Шеф',
                'last_name': 'Мастер'
            },
            {
                'username': 'home_cook',
                'email': 'home@example.com',
                'first_name': 'Домашний',
                'last_name': 'Повар'
            },
        ]

        users = {}
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'✅ Создан пользователь: {user.username}')
            users[user.username] = user

        # Рецепты для chef_master (4 рецепта)
        chef_recipes = [
            {
                'name': 'Блины классические',
                'text': ('Традиционные русские блины на молоке. '
                        'Подавать с вареньем или сметаной.'),
                'cooking_time': 30,
                'tags': ['breakfast'],
                'ingredients': [
                    ('Мука', 200),
                    ('Яйца', 2),
                    ('Молоко', 500),
                    ('Сахар', 30),
                    ('Соль', 5),
                ]
            },
            {
                'name': 'Омлет с овощами',
                'text': ('Пышный омлет с помидорами и огурцами. '
                        'Отличный завтрак.'),
                'cooking_time': 15,
                'tags': ['breakfast'],
                'ingredients': [
                    ('Яйца', 3),
                    ('Молоко', 100),
                    ('Помидоры', 2),
                    ('Огурцы', 1),
                    ('Соль', 3),
                ]
            },
            {
                'name': 'Паста Карбонара',
                'text': 'Классическая итальянская паста с беконом и яйцом.',
                'cooking_time': 25,
                'tags': ['lunch', 'dinner'],
                'ingredients': [
                    ('Мука', 300),
                    ('Яйца', 4),
                    ('Соль', 5),
                    ('Перец', 3),
                ]
            },
            {
                'name': 'Тирамису',
                'text': 'Итальянский десерт с кофе и маскарпоне.',
                'cooking_time': 60,
                'tags': ['dessert'],
                'ingredients': [
                    ('Яйца', 6),
                    ('Сахар', 150),
                    ('Мука', 100),
                ]
            },
        ]

        # Рецепты для home_cook (3 рецепта)
        home_recipes = [
            {
                'name': 'Салат Цезарь',
                'text': ('Классический салат с курицей, сухариками '
                        'и соусом Цезарь.'),
                'cooking_time': 20,
                'tags': ['lunch'],
                'ingredients': [
                    ('Помидоры', 3),
                    ('Огурцы', 2),
                    ('Лук', 1),
                    ('Соль', 3),
                    ('Перец', 2),
                ]
            },
            {
                'name': 'Греческий салат',
                'text': 'Свежий салат с фетой, оливками и овощами.',
                'cooking_time': 15,
                'tags': ['lunch', 'dinner'],
                'ingredients': [
                    ('Помидоры', 4),
                    ('Огурцы', 2),
                    ('Лук', 1),
                    ('Соль', 3),
                ]
            },
            {
                'name': 'Горячий шоколад',
                'text': 'Домашний горячий шоколад с молоком.',
                'cooking_time': 10,
                'tags': ['drinks'],
                'ingredients': [
                    ('Молоко', 300),
                    ('Сахар', 50),
                    ('Сливочное масло', 20),
                ]
            },
        ]

        # Создаем рецепты
        all_recipes = chef_recipes + home_recipes

        for i, recipe_data in enumerate(all_recipes, 1):
            author = users['chef_master'] if i <= 4 else users['home_cook']

            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data['name'],
                author=author,
                defaults={
                    'text': recipe_data['text'],
                    'cooking_time': recipe_data['cooking_time'],
                }
            )

            if created:
                # Добавляем теги
                for tag_slug in recipe_data['tags']:
                    recipe.tags.add(tags[tag_slug])

                # Добавляем ингредиенты
                for ing_name, amount in recipe_data['ingredients']:
                    if ing_name in ingredients:
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient=ingredients[ing_name],
                            amount=amount
                        )

                self.stdout.write(
                    f'✅ Создан рецепт: {recipe.name} '
                    f'(автор: {recipe.author.username})'
                )
            else:
                self.stdout.write(f'ℹ️  Рецепт уже существует: {recipe.name}') 