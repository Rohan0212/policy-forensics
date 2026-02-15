import axios from "axios";

const API_URL = "http://localhost:5000";

export async function analyzePolicy(policyText, useAI = false) {
  try {
    const response = await axios.post(`${API_URL}/analyze`, {
      policy: policyText,
      use_ai: useAI,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error || "Analysis failed");
  }
}
