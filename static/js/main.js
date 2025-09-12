// Main JavaScript file for Flask app

// Test API function
async function testAPI() {
  try {
    const response = await fetch("/api/hello");
    const data = await response.json();

    // Display the response
    document.getElementById("response-content").textContent = JSON.stringify(
      data,
      null,
      2
    );
    document.getElementById("api-response").style.display = "block";

    // Scroll to response
    document
      .getElementById("api-response")
      .scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    console.error("Error testing API:", error);
    alert("Error testing API: " + error.message);
  }
}

// Test echo API function
async function testEchoAPI() {
  const testData = {
    message: "Hello from frontend!",
    timestamp: new Date().toISOString(),
  };

  try {
    const response = await fetch("/api/echo", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(testData),
    });

    const data = await response.json();

    // Display the response
    document.getElementById("response-content").textContent = JSON.stringify(
      data,
      null,
      2
    );
    document.getElementById("api-response").style.display = "block";

    // Scroll to response
    document
      .getElementById("api-response")
      .scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    console.error("Error testing echo API:", error);
    alert("Error testing echo API: " + error.message);
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  console.log("Flask app loaded successfully!");
});
