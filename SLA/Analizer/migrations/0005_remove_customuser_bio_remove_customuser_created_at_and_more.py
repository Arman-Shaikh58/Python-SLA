# Generated by Django 5.2 on 2025-04-06 09:50

import Analizer.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Analizer', '0004_customuser_bio_customuser_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='location',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='profile_image',
        ),
        migrations.AlterField(
            model_name='questionpaper',
            name='pdf_file',
            field=models.FileField(upload_to='question_papers/%Y/%m/', validators=[Analizer.models.validate_image_size]),
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Analizer.question')),
            ],
        ),
    ]
