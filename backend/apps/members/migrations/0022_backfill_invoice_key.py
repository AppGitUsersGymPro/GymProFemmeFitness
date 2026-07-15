import uuid

from django.db import migrations


def backfill_invoice_key(apps, schema_editor):
    Member = apps.get_model("members", "Member")
    for member in Member.objects.filter(invoice_key__isnull=True).iterator():
        member.invoice_key = uuid.uuid4()
        member.save(update_fields=["invoice_key"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0021_member_invoice_key'),
    ]

    operations = [
        migrations.RunPython(backfill_invoice_key, noop),
    ]
