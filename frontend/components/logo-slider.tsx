/**
 * LogoSlider — 2-row infinite scrolling logo carousel with real company logos.
 * Row 1 scrolls left, Row 2 scrolls right.
 * 72 real logos from /logos/ directory.
 */
import Image from "next/image";

interface LogoItem {
  name: string;
  file: string;
}

const ROW_1: LogoItem[] = [
  { name: "Razorpay", file: "razorpay.png" },
  { name: "Zerodha", file: "zerodha.png" },
  { name: "ONDC", file: "ondc.png" },
  { name: "Cashfree", file: "cashfree.png" },
  { name: "UPI / NPCI", file: "npci.png" },
  { name: "Setu", file: "setu.png" },
  { name: "GSTN", file: "gstn.png" },
  { name: "Juspay", file: "juspay.png" },
  { name: "Upstox", file: "upstox.png" },
  { name: "Zoho", file: "zoho.png" },
  { name: "Frappe", file: "frappe.png" },
  { name: "DigiLocker", file: "digilocker.png" },
  { name: "Bhashini", file: "bhashini.png" },
  { name: "Sarvam AI", file: "sarvam.png" },
  { name: "Next.js", file: "nextjs.png" },
  { name: "React", file: "react.png" },
  { name: "FastAPI", file: "fastapi.png" },
  { name: "Django", file: "django.png" },
  { name: "Flutter", file: "flutter.png" },
  { name: "Stripe", file: "stripe.png" },
  { name: "Supabase", file: "supabase.png" },
  { name: "Spring Boot", file: "springboot.png" },
  { name: "PayU", file: "payu.png" },
  { name: "Paytm", file: "paytm.png" },
  { name: "PhonePe", file: "phonepe.png" },
  { name: "Aadhaar", file: "aadhaar.png" },
  { name: "AngelOne", file: "angelone.png" },
  { name: "Groww", file: "groww.png" },
  { name: "Dhan", file: "dhan.png" },
  { name: "Ola Maps", file: "olamaps.png" },
  { name: "Node.js", file: "nodejs.png" },
  { name: "Express", file: "express.png" },
  { name: "Prisma", file: "prisma.png" },
  { name: "PostgreSQL", file: "postgresql.png" },
  { name: "Redis", file: "redis.png" },
  { name: "Tailwind", file: "tailwind.png" },
];

const ROW_2: LogoItem[] = [
  { name: "ABDM Health", file: "abdm.png" },
  { name: "Krutrim AI", file: "krutrim.png" },
  { name: "AI4Bharat", file: "ai4bharat.png" },
  { name: "Yellow.ai", file: "yellowai.png" },
  { name: "Slang Labs", file: "slanglabs.png" },
  { name: "Tally Prime", file: "tally.png" },
  { name: "SAP", file: "sap.png" },
  { name: "Freshworks", file: "freshworks.png" },
  { name: "Darwinbox", file: "darwinbox.png" },
  { name: "greytHR", file: "greythr.png" },
  { name: "MoEngage", file: "moengage.png" },
  { name: "CleverTap", file: "clevertap.png" },
  { name: "Exotel", file: "exotel.png" },
  { name: "MSG91", file: "msg91.png" },
  { name: "Shiprocket", file: "shiprocket.png" },
  { name: "Delhivery", file: "delhivery.png" },
  { name: "BillDesk", file: "billdesk.png" },
  { name: "CCAvenue", file: "ccavenue.png" },
  { name: "Instamojo", file: "instamojo.png" },
  { name: "5paisa", file: "5paisa.png" },
  { name: "ICICI Direct", file: "icicidirect.png" },
  { name: "Mappls", file: "mappls.png" },
  { name: "Shopify", file: "shopify.png" },
  { name: "AWS", file: "aws.png" },
  { name: "Cloudflare", file: "cloudflare.png" },
  { name: "Twilio", file: "twilio.png" },
  { name: "SendGrid", file: "sendgrid.png" },
  { name: "LangChain", file: "langchain.png" },
  { name: "LlamaIndex", file: "llamaindex.png" },
  { name: "Firebase", file: "firebase.png" },
  { name: "GraphQL", file: "graphql.png" },
  { name: "Laravel", file: "laravel.png" },
  { name: "React Native", file: "reactnative.png" },
  { name: "Drizzle", file: "drizzle.png" },
  { name: "tRPC", file: "trpc.png" },
  { name: "Fyers", file: "fyers.png" },
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
            className="flex items-center gap-2.5 px-3.5 py-2 bg-white/[0.03] border border-white/[0.06] rounded-lg whitespace-nowrap flex-shrink-0 hover:border-white/20 transition-colors group"
          >
            <Image
              src={`/logos/${logo.file}`}
              alt={logo.name}
              width={20}
              height={20}
              className="rounded-sm flex-shrink-0"
              unoptimized
            />
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
          Documentation for <span className="text-white font-medium">100+ APIs</span> — always
          fresh, always accurate
        </p>
      </div>
      <div className="flex flex-col gap-3">
        <LogoRow logos={ROW_1} direction="left" />
        <LogoRow logos={ROW_2} direction="right" />
      </div>
    </section>
  );
}
