// Test file to verify modern components are working
import Header from "@/components/layout/Header";
import Hero from "@/components/sections/Hero";

console.log("Modern components loaded successfully");
export default function TestPage() {
  return (
    <div>
      <Header />
      <Hero />
      <div className="p-8 bg-green-100">
        <h1 className="text-3xl font-bold text-green-600">Modern Design Test</h1>
        <p>If you see this with green styling, the modern design is working!</p>
      </div>
    </div>
  );
}
