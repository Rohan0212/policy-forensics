import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import ClauseCard from "./ClauseCard";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

export default function RiskDashboard({ results }) {
  const categories = [
    "data_resale",
    "biometric",
    "indefinite_retention",
    "vague_language",
  ];

  const categoryLabels = {
    data_resale: "Data Resale",
    biometric: "Biometric Collection",
    indefinite_retention: "Indefinite Retention",
    vague_language: "Vague Language",
  };

  const chartData = {
    labels: categories.map((c) => categoryLabels[c]),
    datasets: [
      {
        label: "Risk Score",
        data: categories.map((c) => results[c]?.score || 0),
        backgroundColor: categories.map((c) => {
          const score = results[c]?.score || 0;
          if (score < 30) return "rgba(34, 197, 94, 0.7)";
          if (score < 60) return "rgba(251, 191, 36, 0.7)";
          return "rgba(239, 68, 68, 0.7)";
        }),
        borderColor: categories.map((c) => {
          const score = results[c]?.score || 0;
          if (score < 30) return "rgb(34, 197, 94)";
          if (score < 60) return "rgb(251, 191, 36)";
          return "rgb(239, 68, 68)";
        }),
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: false },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: { callback: (value) => value + "%" },
      },
    },
  };

  const getRiskColor = (level) => {
    if (level === "low") return "text-green-600 bg-green-50 border-green-200";
    if (level === "medium")
      return "text-yellow-600 bg-yellow-50 border-yellow-200";
    return "text-red-600 bg-red-50 border-red-200";
  };

  return (
    <div className="mt-8 space-y-6">
      {/* Overall Score */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              Overall Risk Score
            </h2>
            <p className="text-gray-600 mt-1">
              Aggregated privacy risk assessment
            </p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold text-gray-900">
              {results.overall?.score}
            </div>
            <div
              className={`mt-2 px-4 py-1 rounded-full border ${getRiskColor(results.overall?.risk_level)}`}
            >
              {results.overall?.risk_level.toUpperCase()}
            </div>
          </div>
        </div>
      </div>

      {/* Risk Chart */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Risk Breakdown</h3>
        <Bar data={chartData} options={chartOptions} />
      </div>

      {/* Detailed Results by Category */}
      {categories.map((category) => {
        const data = results[category];
        if (!data || data.total_matches === 0) return null;

        return (
          <div key={category} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-900">
                {categoryLabels[category]}
              </h3>
              <div className="flex items-center gap-4">
                <span
                  className={`px-3 py-1 rounded-full border text-sm font-semibold ${getRiskColor(data.risk_level)}`}
                >
                  {data.score}% Risk
                </span>
                <span className="text-sm text-gray-600">
                  {data.total_matches} clause{data.total_matches > 1 ? "s" : ""}{" "}
                  flagged
                </span>
              </div>
            </div>

            <div className="space-y-4">
              {data.matches?.map((match, idx) => (
                <ClauseCard key={idx} match={match} category={category} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
