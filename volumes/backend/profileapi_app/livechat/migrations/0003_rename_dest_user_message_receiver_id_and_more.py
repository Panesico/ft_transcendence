# Generated by Django 4.2.16 on 2024-10-17 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('livechat', '0002_remove_message_user_message_dest_user_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='dest_user',
            new_name='receiver_id',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='send_user',
            new_name='sender_id',
        ),
    ]
