# Generated by Django 4.2.7 on 2024-12-11 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_faculty_exp_customlogentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='faculty',
            name='image',
            field=models.ImageField(null=True, upload_to='Faculty Image'),
        ),
    ]
