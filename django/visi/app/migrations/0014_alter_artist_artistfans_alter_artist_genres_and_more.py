# Generated by Django 5.1.6 on 2025-05-24 07:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0013_alter_availability_options_booking"),
    ]

    operations = [
        migrations.AlterField(
            model_name="artist",
            name="artistfans",
            field=models.ManyToManyField(
                blank=True, related_name="artist_fans", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name="artist",
            name="genres",
            field=models.ManyToManyField(
                blank=True, related_name="artists", to="app.genre"
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="message",
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="events",
            name="authorized_doormen",
            field=models.ManyToManyField(
                blank=True, related_name="events", to="app.doorman"
            ),
        ),
        migrations.AlterField(
            model_name="fan",
            name="genres",
            field=models.ManyToManyField(
                blank=True, related_name="fans", to="app.genre"
            ),
        ),
        migrations.AlterField(
            model_name="venue",
            name="genres",
            field=models.ManyToManyField(
                blank=True, related_name="venues", to="app.genre"
            ),
        ),
        migrations.AlterField(
            model_name="venue",
            name="venuefans",
            field=models.ManyToManyField(
                blank=True, related_name="venue_fans", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
