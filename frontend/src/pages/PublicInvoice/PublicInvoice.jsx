import { useState, useEffect } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import axios from "axios";
import MemberBill from "../../components/MemberBill";
import { buildStatementBill } from "../../utils/billHelpers";

// Public invoice page — unauthenticated, no JWT needed (mirrors Kiosk's axios instance).
const publicApi = axios.create({ baseURL: "/api" });

export default function PublicInvoice() {
  const { key } = useParams();
  const [searchParams] = useSearchParams();
  const invoiceNumber = searchParams.get("invoice") || "";

  const [bill, setBill] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(null);
    publicApi
      .get(`/members/invoice/${key}/`, { params: invoiceNumber ? { invoice: invoiceNumber } : {} })
      .then((res) => {
        const data = res.data;
        if (data.payments) {
          // Statement mode — aggregate the same way PaymentHistoryModal does.
          setBill(
            buildStatementBill(
              {
                member_name: data.member_name,
                member_id: data.member_id,
                phone: data.phone,
                email: data.email,
                invoice_key: data.invoice_key,
              },
              data.payments,
              {
                gym_name: data.gym_name,
                gym_address: data.gym_address,
                gym_phone: data.gym_phone,
                gym_email: data.gym_email,
                gym_gstin: data.gym_gstin,
              }
            )
          );
        } else {
          setBill(data);
        }
      })
      .catch(() => setError("This invoice link is invalid or no longer available."))
      .finally(() => setLoading(false));
  }, [key, invoiceNumber]);

  if (loading) {
    return (
      <div className="bill-page" style={{ alignItems: "center", color: "var(--text2)" }}>
        Loading invoice…
      </div>
    );
  }

  if (error || !bill) {
    return (
      <div className="bill-page" style={{ alignItems: "center", color: "var(--text2)" }}>
        {error || "Invoice not found."}
      </div>
    );
  }

  return <MemberBill bill={bill} standalone />;
}
