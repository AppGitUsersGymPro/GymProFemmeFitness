import logging
from django.db import transaction

from .models import FingerprintSlot

logger = logging.getLogger(__name__)


def allocate_lowest_free_slot(*, member=None, staff=None):
    """
    Allocates the lowest-numbered free slot_id to `member` XOR `staff`.
    Concurrency-safe: locks all existing FingerprintSlot rows for the
    duration of the transaction so two concurrent enroll requests can't
    both compute the same "next free" number.
    """
    if bool(member) == bool(staff):
        raise ValueError("allocate_lowest_free_slot requires exactly one of member= or staff=")

    with transaction.atomic():
        taken = list(
            FingerprintSlot.objects.select_for_update()
            .order_by("slot_id")
            .values_list("slot_id", flat=True)
        )

        next_id = 1
        for slot_id in taken:
            if slot_id == next_id:
                next_id += 1
            elif slot_id > next_id:
                break

        slot = FingerprintSlot(slot_id=next_id, member=member, staff=staff)
        slot.full_clean()
        slot.save()
        logger.info(
            f"allocate_lowest_free_slot: allocated slot_id={next_id} to "
            f"{'member' if member else 'staff'} id={member.id if member else staff.id}"
        )
        return slot


def free_slot(*, member=None, staff=None):
    if bool(member) == bool(staff):
        raise ValueError("free_slot requires exactly one of member= or staff=")

    qs = FingerprintSlot.objects.filter(member=member) if member else FingerprintSlot.objects.filter(staff=staff)
    deleted, _ = qs.delete()
    logger.info(
        f"free_slot: deleted={deleted} for {'member' if member else 'staff'} "
        f"id={member.id if member else staff.id}"
    )
    return deleted > 0
