import type {Metadata} from "next";
import "./globals.css";
import AppShell from "@/components/AppShell";
export const metadata:Metadata={title:"HELIOS — Urban Heat Intervention OS",description:"Don't map the heat. Rewrite it."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><AppShell>{children}</AppShell></body></html>}
