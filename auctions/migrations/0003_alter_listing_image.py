# Generated by Django 4.1.5 on 2023-02-02 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_listing_comment_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.URLField(blank=True, default='https://t3.ftcdn.net/jpg/04/62/93/66/360_F_462936689_BpEEcxfgMuYPfTaIAOC1tCDurmsno7Sp.jpg'),
        ),
    ]
