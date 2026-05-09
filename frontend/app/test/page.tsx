export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-green-600 mb-4">
          🌱 VitaChain - Page de Test
        </h1>
        <p className="text-xl text-gray-700 mb-8">
          Le frontend fonctionne correctement !
        </p>
        <div className="bg-white p-8 rounded-lg shadow-lg">
          <h2 className="text-2xl font-semibold mb-4">Status du Système</h2>
          <div className="text-left space-y-2">
            <p>✅ Frontend Next.js: Actif</p>
            <p>✅ Page de test: Affichée</p>
            <p>✅ Styles: Fonctionnels</p>
            <p>✅ Navigation: Prête</p>
          </div>
          <div className="mt-6 space-x-4">
            <a href="/" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
              Accueil
            </a>
            <a href="/auth/register" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Inscription
            </a>
            <a href="/auth/login" className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">
              Login
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
