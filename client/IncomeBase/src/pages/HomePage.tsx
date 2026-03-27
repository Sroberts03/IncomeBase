export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-emerald-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl px-8 py-12 max-w-xl w-full flex flex-col items-center">
        <h1 className="text-4xl font-extrabold text-blue-700 mb-4 tracking-tight">Welcome to IncomeBase</h1>
        <p className="text-lg text-gray-700 mb-2 text-center">Your one-stop solution for income verification and document analysis.</p>
        <p className="text-md text-gray-500 text-center">Please check your email for instructions on how to verify your zip code and upload your documents.</p>
      </div>
    </div>
  );
}