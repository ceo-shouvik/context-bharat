/**
 * Pricing page — modern, competitive with Context7.
 * Monthly/annual toggle, feature comparison, FAQ, dynamic library count.
 */
import { PricingClient } from "./pricing-client";

export const metadata = {
  title: "Pricing — contextBharat",
  description:
    "Free to start. ₹399/month for unlimited access to all Indian APIs. Annual plans save 20%.",
};

export default function PricingPage() {
  return <PricingClient />;
}
