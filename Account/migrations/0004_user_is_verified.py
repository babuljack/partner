# Generated by Django 4.0.4 on 2022-04-19 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0003_remove_profile_picture_user_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
