from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MonthlySalary',
            new_name='MonthlyIncome',
        ),
    ]
