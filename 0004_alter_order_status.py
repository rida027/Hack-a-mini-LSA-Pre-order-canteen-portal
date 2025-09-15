from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0003_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('ready', 'Ready'), ('collected', 'Collected'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
    ]
