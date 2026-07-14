import logging
from django.core.exceptions import ValidationError
from django.db import models

logger = logging.getLogger(__name__)


class FingerprintSlot(models.Model):
    """
    Maps a physical fingerprint scanner's numeric user_id (slot_id) to
    exactly one Member OR one StaffMember. slot_id is independently
    allocated (see apps.devices.services.allocate_lowest_free_slot) to
    mirror the device's own auto-compacting slot numbering — it is not
    Member.id/StaffMember.id.
    """
    slot_id = models.PositiveIntegerField(unique=True, db_index=True)
    member = models.OneToOneField(
        "members.Member", on_delete=models.CASCADE,
        null=True, blank=True, related_name="fingerprint_slot",
    )
    staff = models.OneToOneField(
        "staff.StaffMember", on_delete=models.CASCADE,
        null=True, blank=True, related_name="fingerprint_slot",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slot_id"]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(member__isnull=False, staff__isnull=True)
                    | models.Q(member__isnull=True, staff__isnull=False)
                ),
                name="fingerprintslot_exactly_one_owner",
            ),
        ]

    def __str__(self):
        owner = self.member.name if self.member_id else (self.staff.name if self.staff_id else "—")
        return f"Slot {self.slot_id} — {owner}"

    def clean(self):
        if bool(self.member_id) == bool(self.staff_id):
            logger.warning(
                f"FingerprintSlot validation failed: slot_id={self.slot_id} "
                f"member_id={self.member_id} staff_id={self.staff_id} — exactly one must be set"
            )
            raise ValidationError("A fingerprint slot must be linked to exactly one of Member or Staff.")
