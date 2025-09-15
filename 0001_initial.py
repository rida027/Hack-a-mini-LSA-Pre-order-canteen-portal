import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.IntegerField(default=0)),
                ('available', models.BooleanField(default=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='food_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('roll_no', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('scheduled_time', models.DateTimeField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('ready', 'Ready'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canteen.customerprofile')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('item_status', models.CharField(default='pending', max_length=20)),
                ('food', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canteen.food')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='canteen.order')),
            ],
        ),
        migrations.CreateModel(
            name='ShopOwnerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('shop_name', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='shop_owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canteen.shopownerprofile'),
        ),
        migrations.AddField(
            model_name='food',
            name='shop_owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='canteen.shopownerprofile'),
        ),
    ]
