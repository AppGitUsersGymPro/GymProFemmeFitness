import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0022_backfill_invoice_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='invoice_key',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
