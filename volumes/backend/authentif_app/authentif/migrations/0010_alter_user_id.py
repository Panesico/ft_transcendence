# Generated by Django 4.2.16 on 2024-09-25 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentif', '0009_alter_user_avatar_alter_user_city_alter_user_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False, unique=True),
        ),
    ]
