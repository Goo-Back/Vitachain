"use client"

export default function TestStylesPage() {
  return (
    <div style={{ 
      backgroundColor: '#f0fdf4', 
      minHeight: '100vh', 
      padding: '20px',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      <div style={{
        backgroundColor: '#22c55e',
        color: 'white',
        padding: '20px',
        borderRadius: '8px',
        textAlign: 'center',
        marginBottom: '20px'
      }}>
        <h1 style={{ margin: 0, fontSize: '32px' }}>CSS Test Page</h1>
        <p style={{ margin: '10px 0 0 0', fontSize: '16px' }}>Testing if styles are working</p>
      </div>
      
      <div style={{
        backgroundColor: 'white',
        padding: '20px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{ color: '#16a34a', marginBottom: '10px' }}>Tailwind Test</h2>
        <p>If you can see this white card with green text, then inline styles work but Tailwind doesn't.</p>
      </div>

      <div className="bg-blue-500 text-white p-4 rounded-lg">
        <h3 className="text-xl font-bold mb-2">Tailwind Classes Test</h3>
        <p>If this has blue background and white text, Tailwind is working.</p>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-4">
        <div className="bg-red-500 p-4 rounded text-white">Card 1</div>
        <div className="bg-green-500 p-4 rounded text-white">Card 2</div>
        <div className="bg-blue-500 p-4 rounded text-white">Card 3</div>
      </div>
    </div>
  )
}
