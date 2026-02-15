import { useState } from "react";
import PolicyInput from "./components/PolicyInput";
import RiskDashboard from "./components/RiskDashboard";
import LoadingSpinner from "./components/LoadingSpinner";
import { analyzePolicy } from "./utils/api";

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (policyText, useAI) => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await analyzePolicy(policyText, useAI);
      setResults(data);
    } catch (err) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-4xl font-bold text-gray-900">
            Policy<span className="text-blue-600">X-Ray</span>
          </h1>
          <p className="text-gray-600 mt-2">
            AI-Powered Privacy Policy Risk Analysis
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <PolicyInput onAnalyze={handleAnalyze} loading={loading} />

        {loading && <LoadingSpinner />}

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {results && <RiskDashboard results={results} />}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-gray-600">
        <p>Built for HackNC 2025 • Track: The Agency</p>
      </footer>
    </div>
  );
}

export default App;
