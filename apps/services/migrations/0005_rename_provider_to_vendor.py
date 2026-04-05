from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_alter_service_created_at_alter_service_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='provider',
            new_name='vendor',
        ),
        migrations.AlterField(
            model_name='service',
            name='vendor',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='services',
                to=settings.AUTH_USER_MODEL,
                verbose_name='التاجر'
            ),
        ),
    ]
