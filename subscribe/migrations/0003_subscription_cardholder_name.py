# Generated by Django 3.1.7 on 2021-03-25 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0002_auto_20210323_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='cardholder_name',
            field=models.CharField(default='Test', max_length=60),
            preserve_default=False,
        ),
    ]