# Generated by Django 5.0.6 on 2024-05-13 06:16

import django.db.models.deletion
import django_ckeditor_5.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'verbose_name': 'Academic Year',
                'verbose_name_plural': 'Academic Years',
                'db_table': 'schools_academic_year',
            },
        ),
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=20)),
                ('max_point', models.PositiveSmallIntegerField()),
                ('description', django_ckeditor_5.fields.CKEditor5Field(verbose_name='Text')),
            ],
            options={
                'verbose_name': 'Criterion',
                'verbose_name_plural': 'Criterions',
            },
        ),
        migrations.CreateModel(
            name='EducationalSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Educational System',
                'verbose_name_plural': 'Educational Systems',
                'db_table': 'schools_educational_system',
            },
        ),
        migrations.CreateModel(
            name='TrainingPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('point', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Training Point',
                'verbose_name_plural': 'Training Points',
                'db_table': 'schools_training_point',
                'permissions': [('view_faculty_statistics', 'Can view faculty statistics'), ('export_faculty_statistics', 'Can export faculty statistics'), ('view_class_statistics', 'Can view class statistics'), ('export_class_statistics', 'Can export class statistics')],
            },
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('educational_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculties', to='schools.educationalsystem')),
            ],
            options={
                'verbose_name': 'Faculty',
                'verbose_name_plural': 'Faculties',
            },
        ),
        migrations.CreateModel(
            name='Major',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='majors', to='schools.faculty')),
            ],
            options={
                'verbose_name': 'Major',
                'verbose_name_plural': 'Majors',
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=50)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='schools.academicyear')),
                ('major', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='schools.major')),
            ],
            options={
                'verbose_name': 'Class',
                'verbose_name_plural': 'Classes',
            },
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('short_name', models.PositiveSmallIntegerField(choices=[(1, 'Học kỳ 1'), (2, 'Học kỳ 2'), (3, 'Học kỳ 3')])),
                ('code', models.CharField(blank=True, db_index=True, editable=False, max_length=3, null=True, unique=True)),
                ('academic_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semesters', to='schools.academicyear')),
            ],
            options={
                'verbose_name': 'Semester',
                'verbose_name_plural': 'Semesters',
            },
        ),
        migrations.CreateModel(
            name='SemesterOfStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schools.semester')),
            ],
            options={
                'verbose_name': 'Semester Of Student',
                'verbose_name_plural': 'Semester Of Student',
                'db_table': 'schools_semester_of_student',
            },
        ),
    ]
