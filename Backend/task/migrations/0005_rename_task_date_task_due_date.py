# Generated by Django 5.0.1 on 2024-01-18 14:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_task_task_date_alter_task_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='task_date',
            new_name='due_date',
        ),
    ]