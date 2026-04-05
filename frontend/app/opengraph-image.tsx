import { ImageResponse } from "next/og";

export const alt = "contextBharat — AI Documentation for Indian APIs";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default function OGImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          backgroundColor: "#05080f",
          padding: "60px 80px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Top-left gradient accent */}
        <div
          style={{
            position: "absolute",
            top: "-120px",
            left: "-120px",
            width: "400px",
            height: "400px",
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(245,158,28,0.25) 0%, transparent 70%)",
          }}
        />

        {/* Bottom-right gradient accent */}
        <div
          style={{
            position: "absolute",
            bottom: "-100px",
            right: "-100px",
            width: "500px",
            height: "500px",
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(15,110,86,0.3) 0%, transparent 70%)",
          }}
        />

        {/* Top bar with saffron accent line */}
        <div
          style={{
            display: "flex",
            width: "100%",
            height: "4px",
            background: "linear-gradient(90deg, #f59e1c 0%, #0f6e56 100%)",
            borderRadius: "2px",
            marginBottom: "48px",
          }}
        />

        {/* Logo text */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            marginBottom: "32px",
          }}
        >
          {/* Logo mark */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "56px",
              height: "56px",
              backgroundColor: "#f59e1c",
              borderRadius: "14px",
            }}
          >
            <span
              style={{
                fontSize: "30px",
                fontWeight: 800,
                color: "white",
                letterSpacing: "-1px",
              }}
            >
              CB
            </span>
          </div>
          <span
            style={{
              fontSize: "48px",
              fontWeight: 800,
              color: "#ffffff",
              letterSpacing: "-1px",
            }}
          >
            context
            <span style={{ color: "#f59e1c" }}>Bharat</span>
          </span>
        </div>

        {/* Tagline */}
        <div
          style={{
            display: "flex",
            fontSize: "36px",
            fontWeight: 600,
            color: "#e2e8f0",
            lineHeight: 1.3,
            marginBottom: "24px",
          }}
        >
          The Documentation Layer India's Developers Deserved
        </div>

        {/* Subtitle */}
        <div
          style={{
            display: "flex",
            fontSize: "22px",
            fontWeight: 400,
            color: "#94a3b8",
            lineHeight: 1.5,
            marginBottom: "auto",
          }}
        >
          Razorpay · Zerodha · ONDC · UPI · 100+ Indian APIs in your AI editor
        </div>

        {/* Bottom row */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            width: "100%",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
            }}
          >
            <div
              style={{
                display: "flex",
                width: "10px",
                height: "10px",
                borderRadius: "50%",
                backgroundColor: "#0f6e56",
              }}
            />
            <span
              style={{
                fontSize: "20px",
                fontWeight: 500,
                color: "#0f6e56",
              }}
            >
              Open Source MCP Server
            </span>
          </div>
          <span
            style={{
              fontSize: "20px",
              fontWeight: 600,
              color: "#64748b",
            }}
          >
            contextbharat.com
          </span>
        </div>
      </div>
    ),
    {
      ...size,
    },
  );
}
