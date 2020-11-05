# Generated by Django 3.1.2 on 2020-11-05 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daraz', '0002_auto_20201105_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='people',
            fields=[
                ('Id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=1000)),
                ('email', models.CharField(max_length=100, unique=True)),
                ('gender', models.CharField(max_length=100)),
                ('dateOfBirth', models.DateField()),
                ('Address', models.CharField(max_length=1000)),
                ('zone', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('photo', models.CharField(max_length=1000)),
                ('method', models.CharField(max_length=100)),
            ],
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
