/**
 * Builds the synthetic "Full Statement" bill object consumed by <MemberBill>.
 * Shared between the authenticated Payment History view and the public
 * invoice page so the aggregation logic only lives in one place.
 *
 * @param {{member_name:string, member_id:string, phone?:string, email?:string, invoice_key?:string}} memberInfo
 * @param {Array} payments - MemberPayment-shaped objects, each with `installment_payments`.
 * @param {object} gymInfo - { gym_name, gym_address, gym_phone, gym_email, gym_gstin }
 */
export function buildStatementBill(memberInfo, payments, gymInfo = {}) {
  const sortedAsc = [...payments]
    .sort((a, b) => new Date(a.paid_date) - new Date(b.paid_date))
    .map(p => ({ ...p, cycle_installments: p.installment_payments || p.cycle_installments || [] }));

  return {
    isStatement: true,
    member_name: memberInfo.member_name,
    member_id: memberInfo.member_id,
    phone: memberInfo.phone || "",
    email: memberInfo.email || "",
    date: new Date().toISOString().slice(0, 10),
    invoice_number: "",
    plan_price: 0, gst_rate: 0, gst_amount: 0,
    total_with_gst: 0, amount_paid: 0, balance: 0,
    invoice_key: memberInfo.invoice_key,
    ...gymInfo,
    installments: sortedAsc,
  };
}
