// popup.js

document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultsContainer = document.getElementById("results");
    function showSpinner(message) {
        resultsContainer.innerHTML = `<div class="spinner"></div> ${message}`;
    }

    analyzeBtn.addEventListener("click", async () => {
        // resultsContainer.innerHTML = "Analyzing policy... ⏳";
        
        try {
            // Get active tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            showSpinner("Analyzing page...");
            
            // Request text from content script
            chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (response) => {
                if (!response || !response.isPolicyPage) {
                    resultsContainer.innerText = "This does not appear to be a privacy or terms page.";
                    return;
                }

                const pageText = response.pageText;

                try {
                    const res = await fetch("http://127.0.0.1:8000/analyze", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text: pageText })
                    });

                    const data = await res.json();

                    if (!data.analysis) {
                        resultsContainer.innerText = "Failed to get analysis from backend.";
                        return;
                    }

                    renderAnalysis(data.analysis);

                } catch (err) {
                    console.error("Error during fetch:", err);
                    resultsContainer.innerText = "Error contacting analysis server.";
                }
            });

        } catch (err) {
            console.error("Error accessing tab:", err);
            resultsContainer.innerText = "Error accessing current tab.";
        }
    });

    // Function to render the analysis nicely
    function renderAnalysis(analysis) {
        resultsContainer.innerHTML = ""; // clear previous

        const createLine = (label, value) => {
            const line = document.createElement("div");
            line.style.marginBottom = "5px";
            line.innerHTML = `${value ? "✅" : "❌"} <strong>${label}</strong>`;
            return line;
        };

        resultsContainer.appendChild(createLine("Biometric Data Mentioned", analysis.mentions_biometric_data));
        resultsContainer.appendChild(createLine("Location Tracking Mentioned", analysis.mentions_location_tracking));
        resultsContainer.appendChild(createLine("Camera / Microphone Mentioned", analysis.mentions_camera_or_microphone));
        resultsContainer.appendChild(createLine("Data Retention Policy Present", analysis.data_retention_policy_present));
        resultsContainer.appendChild(createLine("Retention Duration Specified", analysis.retention_duration_specified));

        // Risk notes
        if (analysis.risk_reason && analysis.risk_reason.length > 0) {
            const riskBox = document.createElement("div");
            riskBox.style.marginTop = "10px";
            riskBox.style.padding = "8px";
            riskBox.style.background = "#f9f9f9";
            riskBox.style.border = "1px solid #ddd";
            riskBox.style.borderRadius = "5px";
            riskBox.style.maxHeight = "150px";
            riskBox.style.overflowY = "auto";
            riskBox.style.fontSize = "13px";
            riskBox.innerHTML = `<strong>Notes:</strong><br>${analysis.risk_reason}`;
            resultsContainer.appendChild(riskBox);
        }
    }
});


document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("sendPageBtn");
    const resultsDiv = document.getElementById("results");

    sendBtn.addEventListener("click", async () => {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        chrome.tabs.sendMessage(tab.id, { action: "extractText" }, async (response) => {
            if (!response || !response.isPolicyPage) {
                resultsDiv.innerText = "This does not appear to be a privacy or terms page.";
                return;
            }

            const pageText = response.pageText;
            resultsDiv.innerText = "Sending page data... ⏳";

            try {
                const res = await fetch("http://127.0.0.1:5000/receive_data", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ page_text: pageText })
                });

                if (!res.ok) throw new Error("Failed to send page text");

                window.open("http://localhost:5173/", "_blank");
                resultsDiv.innerText = "Page data sent! ✅";
            } catch (err) {
                console.error(err);
                resultsDiv.innerText = "Failed to send page data.";
            }
        });
    });
});