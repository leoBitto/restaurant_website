# Generated by Django 5.0 on 2023-12-09 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu_management', '0002_dish_remove_menu_dessert_remove_menu_entree_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Menu',
        ),
    ]
