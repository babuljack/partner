# Generated by Django 4.0.4 on 2022-04-19 11:48

import Account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0005_alter_user_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='picture',
            field=models.ImageField(default='img/default/profile.ppg', upload_to=Account.models.img_path),
        ),
    ]
