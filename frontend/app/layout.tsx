import type {Metadata} from "next";
import "./globals.css";
import "./decision.css";
import "./decision-science.css";
import "./labs.css";
import "./runtime.css";
import "./thermalway-intel.css";
import "./thermal-history.css";
import "./system-readiness.css";
import AppShell from "@/components/AppShell";
import {DecisionProvider} from "@/components/DecisionContext";

export const metadata:Metadata={title:"HELIOS — Urban Heat Intervention OS",description:"Don't map the heat. Rewrite it."};

export default function RootLayout({children}:{children:React.ReactNode}){
 return <html lang="en"><body><DecisionProvider><AppShell>{children}</AppShell></DecisionProvider></body></html>
}
