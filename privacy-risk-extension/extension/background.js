chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "analyzeText") {
        // Placeholder for backend API call
        console.log("Received text for analysis");

        sendResponse({
            riskLevel: "Medium",
            biometric: true,
            location: false,
            retention: "Indefinite"
        });
    }
});
