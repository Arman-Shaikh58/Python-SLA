# Generated by Django 5.2 on 2025-04-10 06:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Analizer', '0008_remove_question_exam_question_question_paper_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='Analizer.subject'),
        ),
    ]
