/**
 * LogoSlider — infinite scrolling logo carousel of supported APIs.
 * Pure CSS animation, no JS dependencies.
 */

const LOGOS = [
  { name: "Razorpay", color: "#3395FF" },
  { name: "Zerodha", color: "#387ED1" },
  { name: "ONDC", color: "#1A73E8" },
  { name: "Cashfree", color: "#6C3CE9" },
  { name: "UPI", color: "#4CAF50" },
  { name: "Setu", color: "#00BFA5" },
  { name: "GSTN", color: "#F44336" },
  { name: "Juspay", color: "#FF6F00" },
  { name: "Upstox", color: "#7B1FA2" },
  { name: "Zoho", color: "#E42527" },
  { name: "Frappe", color: "#0089FF" },
  { name: "DigiLocker", color: "#1565C0" },
  { name: "Bhashini", color: "#FF9800" },
  { name: "Sarvam AI", color: "#8BC34A" },
  { name: "Next.js", color: "#FFFFFF" },
  { name: "React", color: "#61DAFB" },
  { name: "FastAPI", color: "#009688" },
  { name: "Django", color: "#092E20" },
  { name: "Flutter", color: "#02569B" },
  { name: "Stripe", color: "#635BFF" },
  { name: "Supabase", color: "#3ECF8E" },
  { name: "Spring Boot", color: "#6DB33F" },
];

export function LogoSlider() {
  return (
    <section className="py-10 overflow-hidden">
      <div className="text-center mb-6">
        <p className="text-gray-500 text-sm">Powering documentation for 100+ APIs including</p>
      </div>
      {/* Double the logos for seamless infinite scroll */}
      <div className="relative">
        <div className="flex animate-scroll gap-8 w-max">
          {[...LOGOS, ...LOGOS].map((logo, i) => (
            <div
              key={`${logo.name}-${i}`}
              className="flex items-center gap-2 px-4 py-2.5 bg-white/[0.03] border border-white/[0.06] rounded-lg whitespace-nowrap flex-shrink-0 hover:border-white/20 transition-colors"
            >
              <div
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ backgroundColor: logo.color }}
              />
              <span className="text-gray-400 text-sm font-medium">{logo.name}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
