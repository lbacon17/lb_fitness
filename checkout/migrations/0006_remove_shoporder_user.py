# Generated by Django 3.1.7 on 2021-03-26 22:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0005_shoporder_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoporder',
            name='user',
        ),
    ]