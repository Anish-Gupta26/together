# Generated by Django 4.0.4 on 2022-06-23 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_rename_updated_room_updted_remove_room_topic_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='updted',
            new_name='updated',
        ),
    ]
