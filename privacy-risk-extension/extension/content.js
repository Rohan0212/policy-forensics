// function isPolicyPage() {
//     const keywords = [
//         "privacy",
//         "terms",
//         "policy",
//         "conditions",
//         "data retention"
//     ];

//     const text = document.body.innerText.toLowerCase();
//     return keywords.some(keyword => text.includes(keyword));
// }

function isPolicyPage() {
    const url = window.location.href.toLowerCase();
    return url.includes("privacy") || url.includes("terms");
}

function extractText() {
    return document.body.innerText;
}

// Listen for popup request
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractText") {
        const isPolicy = isPolicyPage();
        const text = extractText();

        sendResponse({
            isPolicyPage: isPolicy,
            pageText: text.substring(0, 50000)
        });

    }
});