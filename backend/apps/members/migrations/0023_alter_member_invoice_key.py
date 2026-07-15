import uuid

from django.db import migrations, models


def reassign_invoice_keys(apps, schema_editor):
    """
    Unconditionally reassign a fresh, distinct UUID to every Member row
    right before the unique constraint is added. 0021's AddField (callable
    default on a non-empty table) bakes ONE shared UUID into every
    pre-existing row via the ADD COLUMN ... DEFAULT clause -- Postgres
    applies a single computed default to all existing rows, it does not
    invoke the callable per row. 0022's isnull-filtered backfill therefore
    found nothing to fix. This step corrects that regardless of whatever
    state the column is currently in.
    """
    Member = apps.get_model("members", "Member")
    for member in Member.objects.all().iterator():
        member.invoice_key = uuid.uuid4()
        member.save(update_fields=["invoice_key"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0022_backfill_invoice_key'),
    ]

    operations = [
        migrations.RunPython(reassign_invoice_keys, noop),
        migrations.AlterField(
            model_name='member',
            name='invoice_key',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
