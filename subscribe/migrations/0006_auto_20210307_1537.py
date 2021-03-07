# Generated by Django 3.1.7 on 2021-03-07 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0005_subscription_member'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='package_in_cart',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='subscription',
            name='stripe_pid',
            field=models.CharField(default='', max_length=254),
        ),
    ]
