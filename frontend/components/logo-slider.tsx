/**
 * LogoSlider — 2-row infinite scrolling logo carousel of ALL supported APIs.
 * Row 1 scrolls left, Row 2 scrolls right for visual depth.
 * Pure CSS animation, pauses on hover.
 */

interface LogoItem {
  name: string;
  abbr: string;
  color: string;
}

// All 100+ libraries from api-catalog.md — grouped into 2 rows
const ROW_1: LogoItem[] = [
  { name: "Razorpay", abbr: "Rz", color: "#3395FF" },
  { name: "Zerodha Kite", abbr: "Ze", color: "#387ED1" },
  { name: "ONDC", abbr: "ON", color: "#1A73E8" },
  { name: "Cashfree", abbr: "Cf", color: "#6C3CE9" },
  { name: "UPI / NPCI", abbr: "UP", color: "#4CAF50" },
  { name: "Setu", abbr: "Se", color: "#00BFA5" },
  { name: "GSTN", abbr: "GS", color: "#F44336" },
  { name: "Juspay", abbr: "Jp", color: "#FF6F00" },
  { name: "Upstox", abbr: "Ux", color: "#7B1FA2" },
  { name: "Zoho CRM", abbr: "Zo", color: "#E42527" },
  { name: "Frappe", abbr: "Fr", color: "#0089FF" },
  { name: "DigiLocker", abbr: "DL", color: "#1565C0" },
  { name: "Bhashini", abbr: "Bh", color: "#FF9800" },
  { name: "Sarvam AI", abbr: "Sa", color: "#8BC34A" },
  { name: "Next.js", abbr: "Nx", color: "#FFFFFF" },
  { name: "React", abbr: "Re", color: "#61DAFB" },
  { name: "FastAPI", abbr: "FA", color: "#009688" },
  { name: "Django", abbr: "Dj", color: "#092E20" },
  { name: "Flutter", abbr: "Fl", color: "#02569B" },
  { name: "Stripe", abbr: "St", color: "#635BFF" },
  { name: "Supabase", abbr: "Sb", color: "#3ECF8E" },
  { name: "Spring Boot", abbr: "SB", color: "#6DB33F" },
  { name: "PayU", abbr: "Pu", color: "#54B948" },
  { name: "Paytm PG", abbr: "Pt", color: "#002970" },
  { name: "PhonePe", abbr: "PP", color: "#5F259F" },
  { name: "Account Aggregator", abbr: "AA", color: "#00897B" },
  { name: "Aadhaar eKYC", abbr: "Aa", color: "#F57F17" },
  { name: "AngelOne", abbr: "AO", color: "#FF5722" },
  { name: "Groww", abbr: "Gw", color: "#5AC8FA" },
  { name: "Dhan", abbr: "Dn", color: "#2196F3" },
  { name: "Ola Maps", abbr: "Om", color: "#1B5E20" },
  { name: "Node.js", abbr: "No", color: "#339933" },
  { name: "Express.js", abbr: "Ex", color: "#BDBDBD" },
  { name: "Prisma", abbr: "Pr", color: "#2D3748" },
  { name: "PostgreSQL", abbr: "Pg", color: "#336791" },
  { name: "Redis", abbr: "Rd", color: "#DC382D" },
  { name: "Tailwind", abbr: "Tw", color: "#06B6D4" },
  { name: "Drizzle ORM", abbr: "Dr", color: "#C5F74F" },
  { name: "GraphQL", abbr: "GQ", color: "#E535AB" },
  { name: "Laravel", abbr: "Lv", color: "#FF2D20" },
  { name: "React Native", abbr: "RN", color: "#61DAFB" },
  { name: "Firebase", abbr: "Fb", color: "#FFCA28" },
  { name: "tRPC", abbr: "tR", color: "#2596BE" },
];

const ROW_2: LogoItem[] = [
  { name: "ABDM Health", abbr: "AB", color: "#E91E63" },
  { name: "BBPS", abbr: "BB", color: "#FF6D00" },
  { name: "NACH / eMandate", abbr: "NA", color: "#0277BD" },
  { name: "FASTag", abbr: "FT", color: "#2E7D32" },
  { name: "Krutrim AI", abbr: "Kr", color: "#FF3D00" },
  { name: "AI4Bharat", abbr: "A4", color: "#673AB7" },
  { name: "Yellow.ai", abbr: "Ya", color: "#FDD835" },
  { name: "Slang Labs", abbr: "SL", color: "#00BCD4" },
  { name: "Zoho Books", abbr: "ZB", color: "#E42527" },
  { name: "Tally Prime", abbr: "Tp", color: "#FFEB3B" },
  { name: "SAP B1", abbr: "SA", color: "#0FAAFF" },
  { name: "Freshworks", abbr: "Fw", color: "#F36C21" },
  { name: "Darwinbox", abbr: "Db", color: "#6A1B9A" },
  { name: "greytHR", abbr: "gH", color: "#43A047" },
  { name: "MoEngage", abbr: "Mo", color: "#3F51B5" },
  { name: "CleverTap", abbr: "CT", color: "#F44336" },
  { name: "Exotel", abbr: "Et", color: "#1E88E5" },
  { name: "MSG91", abbr: "M9", color: "#FF8F00" },
  { name: "Shiprocket", abbr: "Sr", color: "#7C4DFF" },
  { name: "Delhivery", abbr: "Dv", color: "#D50000" },
  { name: "2Factor", abbr: "2F", color: "#00C853" },
  { name: "BillDesk", abbr: "BD", color: "#1A237E" },
  { name: "CCAvenue", abbr: "CC", color: "#8D6E63" },
  { name: "Instamojo", abbr: "Im", color: "#00B0FF" },
  { name: "Pine Labs", abbr: "PL", color: "#263238" },
  { name: "Fyers", abbr: "Fy", color: "#4DB6AC" },
  { name: "5paisa", abbr: "5p", color: "#F50057" },
  { name: "ICICI Direct", abbr: "IC", color: "#B71C1C" },
  { name: "Mappls", abbr: "Mp", color: "#FF6F00" },
  { name: "ISRO Bhuvan", abbr: "IS", color: "#01579B" },
  { name: "Shopify", abbr: "Sh", color: "#7AB55C" },
  { name: "AWS SDK", abbr: "AW", color: "#FF9900" },
  { name: "Cloudflare", abbr: "CF", color: "#F48120" },
  { name: "Twilio", abbr: "Tw", color: "#F22F46" },
  { name: "SendGrid", abbr: "SG", color: "#1A82E2" },
  { name: "LangChain", abbr: "LC", color: "#1C3C3C" },
  { name: "LlamaIndex", abbr: "LI", color: "#A855F7" },
  { name: "Springworks", abbr: "Sw", color: "#4DD0E1" },
  { name: "MCA21", abbr: "MC", color: "#5D4037" },
  { name: "Income Tax", abbr: "IT", color: "#C62828" },
  { name: "Agristack", abbr: "Ag", color: "#33691E" },
  { name: "Pinelabs POS", abbr: "Px", color: "#455A64" },
];

function LogoRow({ logos, direction }: { logos: LogoItem[]; direction: "left" | "right" }) {
  const animClass = direction === "left" ? "animate-scroll" : "animate-scroll-reverse";
  const doubled = [...logos, ...logos];

  return (
    <div className="overflow-hidden relative">
      {/* Fade edges */}
      <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-[#05080f] to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-[#05080f] to-transparent z-10 pointer-events-none" />
      <div className={`flex gap-3 w-max ${animClass}`}>
        {doubled.map((logo, i) => (
          <div
            key={`${logo.name}-${i}`}
            className="flex items-center gap-2 px-3 py-2 bg-white/[0.03] border border-white/[0.06] rounded-lg whitespace-nowrap flex-shrink-0 hover:border-white/20 transition-colors group"
          >
            <div
              className="w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold flex-shrink-0 text-black"
              style={{ backgroundColor: logo.color }}
            >
              {logo.abbr}
            </div>
            <span className="text-gray-500 text-xs font-medium group-hover:text-gray-300 transition-colors">
              {logo.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function LogoSlider() {
  return (
    <section className="py-8">
      <div className="text-center mb-5">
        <p className="text-gray-500 text-sm">
          Documentation for <span className="text-white font-medium">100+ APIs</span> — always fresh, always accurate
        </p>
      </div>
      <div className="flex flex-col gap-3">
        <LogoRow logos={ROW_1} direction="left" />
        <LogoRow logos={ROW_2} direction="right" />
      </div>
    </section>
  );
}
