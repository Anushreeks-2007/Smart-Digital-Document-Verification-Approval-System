
// LOGIN
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function(e) {
        e.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email, password})
            });

            const data = await response.json();

            if (!response.ok) {
                alert(data.message || "Login failed");
                return;
            }

            localStorage.setItem("token", data.token);
            localStorage.setItem("role", data.role);

            window.location.href =
                data.role === "admin" ? "admin.html" : "dashboard.html";

        } catch (error) {
            alert("Cannot connect to server. Please try again.");
        }
    });
}


// LOGOUT
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "index.html";
}


// COMMON API REQUEST
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("token");

    const headers = {
        ...(options.headers || {})
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(API_BASE_URL + endpoint, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || "Request failed");
    }

    return data;
}


// UPLOAD DOCUMENT
const uploadForm = document.getElementById("uploadForm");

if (uploadForm) {
    uploadForm.addEventListener("submit", async function(e) {
        e.preventDefault();

        const formData = new FormData(uploadForm);

        try {
            const data = await apiRequest("/documents", {
                method: "POST",
                body: formData
            });

            document.getElementById("uploadMessage").textContent =
                data.message || "Document uploaded successfully!";

            uploadForm.reset();

        } catch (error) {
            alert(error.message);
        }
    });
}


// LOAD USER DOCUMENTS
async function loadDocuments() {
    const list = document.getElementById("documentList");

    if (!list) return;

    try {
        const data = await apiRequest("/documents");

        document.getElementById("total").textContent =
            data.documents.length;

        document.getElementById("pending").textContent =
            data.documents.filter(d => d.status === "Pending").length;

        document.getElementById("approved").textContent =
            data.documents.filter(d => d.status === "Approved").length;

        document.getElementById("rejected").textContent =
            data.documents.filter(d => d.status === "Rejected").length;

        list.innerHTML = "";

        data.documents.forEach(doc => {
            const row = document.createElement("tr");

            [doc.document_name, doc.document_type, doc.status]
                .forEach(value => {
                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);
                });

            list.appendChild(row);
        });

    } catch (error) {
        list.textContent = "Unable to load documents.";
    }
}

loadDocuments();


// VERIFY DOCUMENT
const verifyForm = document.getElementById("verifyForm");

if (verifyForm) {
    verifyForm.addEventListener("submit", async function(e) {
        e.preventDefault();

        const id = document.getElementById("verificationId").value;

        try {
            const data = await apiRequest(
                `/verify/${encodeURIComponent(id)}`
            );

            document.getElementById("verificationResult").textContent =
                data.message || "Verification completed.";

        } catch (error) {
            document.getElementById("verificationResult").textContent =
                error.message;
        }
    });
}
