export default function ClauseCard({ match, category }) {
  return (
    <div className="border-l-4 border-red-500 pl-4 py-2 bg-gray-50 rounded-r">
      <div className="text-sm text-gray-800 mb-2">
        <span className="font-semibold text-red-600">Matched: </span>
        <span className="bg-yellow-200 px-1 rounded">
          {match.matched_keyword}
        </span>
      </div>

      <p className="text-sm text-gray-700 leading-relaxed mb-3">{match.text}</p>

      {/* AI Validation (Phase 2) */}
      {match.ai_validation && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-2">
          <div className="flex items-start gap-2">
            <span className="text-lg">🤖</span>
            <div>
              <div className="font-semibold text-blue-900 text-sm">
                AI Analysis:
              </div>
              <p className="text-sm text-blue-800 mt-1">
                {match.ai_validation}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* GDPR Citation (Phase 2) */}
      {match.gdpr_citation && (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
          <div className="flex items-start gap-2">
            <span className="text-lg">⚖️</span>
            <div>
              <div className="font-semibold text-yellow-900 text-sm">
                Regulatory Issue:
              </div>
              <p className="text-sm text-yellow-800 mt-1 whitespace-pre-line">
                {match.gdpr_citation}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
