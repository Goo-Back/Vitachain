import Header from "@/components/layout/Header";
import Hero from "@/components/sections/Hero";

export default function TestModernPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <Hero />
      <div className="p-8 bg-gradient-to-br from-green-50 to-emerald-50">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
            Modern Design Test
          </h1>
          <p className="text-lg text-gray-600">
            If you see this with modern styling, gradients, and animations, the new design is working!
          </p>
          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🌱</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Modern Card 1</h3>
              <p className="text-gray-600">This demonstrates the modern card design with hover effects.</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🛒</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Modern Card 2</h3>
              <p className="text-gray-600">This shows the modern UI components are working properly.</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🍽️</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Modern Card 3</h3>
              <p className="text-gray-600">All the modern styling and animations are functional.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
