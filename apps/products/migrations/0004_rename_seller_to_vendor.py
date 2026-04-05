from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_productimage_alter_category_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Remove the index first, as it references the 'seller' field
        migrations.RemoveIndex(
            model_name='product',
            name='idx_prod_seller',
        ),
        # Now rename the field
        migrations.RenameField(
            model_name='product',
            old_name='seller',
            new_name='vendor',
        ),
        # Alter the field to change nullability and on_delete behavior
        migrations.AlterField(
            model_name='product',
            name='vendor',
            field=models.ForeignKey(
                blank=True,
                help_text='المستخدم المالك لهذا المنتج',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='products',
                to=settings.AUTH_USER_MODEL,
                verbose_name='التاجر'
            ),
        ),
        # Add the new index referencing the 'vendor' field
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['vendor'], name='idx_prod_vendor'),
        ),
    ]
