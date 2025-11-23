export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">FitFlow Pro</h1>
        <p className="text-xl text-gray-600 mb-8">
          Enterprise Gym Management SaaS Platform
        </p>
        <div className="space-x-4">
          <a
            href="/dashboard"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Go to Dashboard
          </a>
          <a
            href="/login"
            className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition"
          >
            Login
          </a>
        </div>
      </div>
    </main>
  )
}
