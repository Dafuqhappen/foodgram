# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='color',
        ),
    ] 