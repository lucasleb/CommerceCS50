# Generated by Django 4.1.5 on 2023-02-04 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_listing_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, default='thing', max_length=100),
            preserve_default=False,
        ),
    ]
