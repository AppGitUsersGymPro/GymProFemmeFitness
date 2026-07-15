import { buildInvoiceLink, buildInvoiceMessage, openWhatsApp } from "../utils/whatsapp";

/**
 * "Send via WhatsApp" button — opens WhatsApp (click-to-chat) pre-filled with
 * an invoice/statement summary and a link to the public invoice page.
 * Works for any bill shape <MemberBill> already knows how to render
 * (membership invoice, statement, or PT renewal) as long as `bill.phone`
 * and `bill.invoice_key` are present.
 */
export default function WhatsAppButton({ bill }) {
  if (!bill?.phone || !bill?.invoice_key) return null;

  const handleClick = () => {
    // Must build the link/message and call openWhatsApp synchronously —
    // no awaits before this — so the popup isn't blocked by the browser.
    const link = buildInvoiceLink(bill);
    const message = buildInvoiceMessage(bill, link);
    openWhatsApp(bill.phone, message);
  };

  return (
    <button
      className="btn btn-sm"
      style={{ background: "rgba(37,211,102,.12)", color: "#25D366", border: "1px solid rgba(37,211,102,.3)" }}
      onClick={handleClick}
    >
      💬 Send via WhatsApp
    </button>
  );
}
