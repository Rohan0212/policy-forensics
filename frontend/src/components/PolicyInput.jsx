import { useEffect, useState } from "react";

export default function PolicyInput({ onAnalyze, loading }) {
  const [policyText, setPolicyText] = useState("");
  const [useAI, setUseAI] = useState(false);

  const handleSubmit = () => {
    if (policyText.trim().length < 100) {
      alert("Please paste a privacy policy (at least 100 characters)");
      return;
    }
    onAnalyze(policyText, useAI);
  };

  const loadSample = () => {
    const sample = `We may collect, use, and share your personal information for various purposes including marketing. 
    
We collect biometric data including facial recognition and fingerprints for security purposes.

Your data will be retained as long as necessary to fulfill our business purposes.

We may share your information with third-party partners and affiliates for commercial purposes.

We reserve the right to monetize user data in ways we deem appropriate.`;

    setPolicyText(sample);
  };

  useEffect(() => {
        fetch("http://127.0.0.1:5000/get_page")
            .then(res => res.json())
            .then(data => setPolicyText(data.page_text))
            .catch(err => console.error(err));
    }, []);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Paste Privacy Policy
      </h2>

      <textarea
        value={policyText}
        onChange={(e) => setPolicyText(e.target.value)}
        placeholder="Paste the privacy policy text here..."
        className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
      />

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={useAI}
              onChange={(e) => setUseAI(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">
              Enable AI Enhancement (Phase 2)
            </span>
          </label>

          <button
            onClick={loadSample}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Load Sample Policy
          </button>
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Analyzing..." : "Analyze Policy"}
        </button>
      </div>
    </div>
  );
}
