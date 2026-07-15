const fmt = (n) => Number(n || 0).toLocaleString("en-IN");

/** Builds the public invoice/statement link for a bill object. */
export function buildInvoiceLink(bill) {
  const base = `${window.location.origin}/invoice/${bill.invoice_key}`;
  return bill.isStatement ? base : `${base}?invoice=${encodeURIComponent(bill.invoice_number)}`;
}

/** Builds a short WhatsApp text summary for a bill, across both bill schemas. */
export function buildInvoiceMessage(bill, link) {
  const gymName = bill.gym_name || "our gym";

  if (bill.isStatement) {
    return (
      `Hi ${bill.member_name}, here is your account statement from ${gymName}.\n\n` +
      `View your statement: ${link}`
    );
  }

  const total = bill.total_with_gst ?? bill.total_amount;
  const label = bill.bill_type === "PT Renewal" ? "PT renewal receipt" : "invoice";
  const balanceLine = Number(bill.balance || 0) > 0
    ? `Balance Due: ₹${fmt(bill.balance)}`
    : "Status: Fully Paid";

  return (
    `Hi ${bill.member_name}, here is your ${label} from ${gymName}.\n` +
    `Invoice: ${bill.invoice_number}\n` +
    `Total: ₹${fmt(total)}\n` +
    `Paid: ₹${fmt(bill.amount_paid)}\n` +
    `${balanceLine}\n\n` +
    `View your ${label}: ${link}`
  );
}

/**
 * Opens WhatsApp's click-to-chat link with the given phone/message pre-filled.
 * Must be called synchronously from a click handler (no `await` first) so the
 * browser doesn't block the popup.
 */
export function openWhatsApp(phone, message) {
  let digits = String(phone || "").trim().replace(/\D/g, "");
  if (digits && !digits.startsWith("91")) digits = `91${digits}`;
  const url = `https://wa.me/${digits}?text=${encodeURIComponent(message)}`;
  window.open(url, "_blank");
}
