# Generated by Django 4.2.13 on 2024-05-13 08:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingpoint',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='users.student'),
        ),
        migrations.AddField(
            model_name='semesterofstudent',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schools.semester'),
        ),
        migrations.AddField(
            model_name='semesterofstudent',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.student'),
        ),
        migrations.AddField(
            model_name='semester',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semesters', to='schools.academicyear'),
        ),
        migrations.AddField(
            model_name='semester',
            name='students',
            field=models.ManyToManyField(related_name='semesters', through='schools.SemesterOfStudent', to='users.student'),
        ),
        migrations.AddField(
            model_name='major',
            name='faculty',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='majors', to='schools.faculty'),
        ),
        migrations.AddField(
            model_name='faculty',
            name='educational_system',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faculties', to='schools.educationalsystem'),
        ),
        migrations.AddField(
            model_name='class',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='schools.academicyear'),
        ),
        migrations.AddField(
            model_name='class',
            name='major',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='schools.major'),
        ),
        migrations.AlterUniqueTogether(
            name='trainingpoint',
            unique_together={('semester', 'criterion', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='semesterofstudent',
            unique_together={('semester', 'student')},
        ),
    ]
