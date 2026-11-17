(() => {
    "use strict";

    const API_BASE = "http://127.0.0.1:5000/api";

    const state = {
        user: null,
        items: [],
        claims: [],
        notifications: [],
        currentPage: "dashboard",
        loading: false
    };

    const app = document.getElementById("app") || document.body;

    async function api(path, options = {}) {
        const config = {
            credentials: "include",
            ...options,
            headers: {
                ...(options.body instanceof FormData
                    ? {}
                    : { "Content-Type": "application/json" }),
                ...(options.headers || {})
            }
        };

        const response = await fetch(API_BASE + path, config);

        let data = {};
        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (!response.ok) {
            throw new Error(
                data.message || data.error || `Request failed (${response.status})`
            );
        }

        return data;
    }

    function esc(value = "") {
        return String(value).replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        })[char]);
    }

    function toast(message, type = "info") {
        let container = document.getElementById("toast-container");

        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            document.body.appendChild(container);
        }

        const element = document.createElement("div");
        element.className = `toast ${type}`;
        element.textContent = message;
        container.appendChild(element);

        setTimeout(() => element.remove(), 3500);
    }

    function formatDate(value) {
        if (!value) return "Date unavailable";

        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return esc(value);

        return date.toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric"
        });
    }

    function setLoading(value) {
        state.loading = value;
        document.body.classList.toggle("loading", value);
    }

    function getItemId(item) {
        return item.id ?? item.item_id ?? "";
    }

    function getItemName(item) {
        return item.item_name || item.name || item.title || "Unnamed item";
    }

    function getItemDescription(item) {
        return item.description || item.details || "No description provided.";
    }

    function getItemLocation(item) {
        return item.location || item.place || "Location not specified";
    }

    function getItemImage(item) {
        if (!item.image) return "";
        if (item.image.startsWith("http")) return item.image;
        return `http://127.0.0.1:5000/${item.image.replace(/^\/+/, "")}`;
    }

    async function loadUser() {
        try {
            const data = await api("/auth/me");
            state.user = data.user || data;
            return true;
        } catch {
            state.user = null;
            return false;
        }
    }

    async function loadItems() {
        try {
            const data = await api("/items/");
            state.items = Array.isArray(data)
                ? data
                : data.items || data.reports || [];
            return true;
        } catch (error) {
            console.error("Unable to load items:", error);
            toast("Unable to load items from the server.", "error");
            return false;
        }
    }

    async function loadClaims() {
        try {
            const data = await api("/claims");
            state.claims = Array.isArray(data)
                ? data
                : data.claims || [];
            return true;
        } catch (error) {
            console.error("Unable to load claims:", error);
            return false;
        }
    }

    async function loadNotifications() {
        try {
            const data = await api("/notifications");
            state.notifications = Array.isArray(data)
                ? data
                : data.notifications || [];
            return true;
        } catch (error) {
            console.error("Unable to load notifications:", error);
            return false;
        }
    }

    function renderHeader() {
        return `
            <header class="app-header">
                <div class="brand">
                    <span class="brand-icon">✦</span>
                    <span>Findly</span>
                </div>

                <nav class="main-nav">
                    <a href="#dashboard">Dashboard</a>
                    <a href="#items">Browse Items</a>
                    <a href="#report">Report Item</a>
                    <a href="#claims">My Claims</a>
                    <a href="#notifications">Notifications</a>
                </nav>

                <div class="user-area">
                    <span>${esc(state.user?.name || "User")}</span>
                    <button id="logout-button" type="button">Logout</button>
                </div>
            </header>
        `;
    }

    function renderItemCard(item) {
        const image = getItemImage(item);
        const id = getItemId(item);

        return `
            <article class="item-card">
                ${image
                    ? `<img class="item-image" src="${esc(image)}" alt="${esc(getItemName(item))}">`
                    : `<div class="item-image placeholder">✦</div>`
                }

                <div class="item-card-content">
                    <span class="item-type">${esc(item.item_type || item.type || "Item")}</span>
                    <h3>${esc(getItemName(item))}</h3>
                    <p>${esc(getItemDescription(item))}</p>
                    <p class="item-location">📍 ${esc(getItemLocation(item))}</p>
                    <p class="item-date">${formatDate(item.item_date || item.date || item.created_at)}</p>
                    <button class="view-item-button" data-item-id="${esc(id)}">
                        View details
                    </button>
                </div>
            </article>
        `;
    }

    function renderDashboard() {
        return `
            <section class="page dashboard-page">
                <div class="welcome-section">
                    <h1>Welcome to Findly, ${esc(state.user?.name || "User")}!</h1>
                    <p>Helping lost belongings find their way home.</p>
                </div>

                <div class="dashboard-stats">
                    <div class="stat-card">
                        <h3>${state.items.length}</h3>
                        <p>Reported Items</p>
                    </div>
                    <div class="stat-card">
                        <h3>${state.claims.length}</h3>
                        <p>My Claims</p>
                    </div>
                    <div class="stat-card">
                        <h3>${state.notifications.length}</h3>
                        <p>Notifications</p>
                    </div>
                </div>

                <div class="section-heading">
                    <h2>Recently Reported Items</h2>
                    <a href="#items">View all</a>
                </div>

                <div class="items-grid">
                    ${state.items.slice(0, 6).map(renderItemCard).join("") ||
                        `<p>No items have been reported yet.</p>`}
                </div>
            </section>
        `;
    }function renderItemsPage() {
        return `
            <section class="page">
                <h1>Browse Items</h1>
                <p>Explore items reported as lost or found.</p>

                <div class="items-grid">
                    ${state.items.map(renderItemCard).join("") ||
                        `<p>No items available.</p>`}
                </div>
            </section>
        `;
    }

    function renderReportPage() {
        return `
            <section class="page">
                <h1>Report an Item</h1>

                <form id="report-form" class="app-form">
                    <label>Item name</label>
                    <input name="item_name" required placeholder="Enter item name">

                    <label>Item type</label>
                    <select name="item_type" required>
                        <option value="lost">Lost</option>
                        <option value="found">Found</option>
                    </select>

                    <label>Category</label>
                    <input name="category" required placeholder="Eg. Electronics">

                    <label>Colour</label>
                    <input name="colour" placeholder="Item colour">

                    <label>Description</label>
                    <textarea name="description" required></textarea>

                    <label>Location</label>
                    <input name="location" required placeholder="Where was it lost/found?">

                    <label>Date</label>
                    <input name="item_date" type="date" required>

                    <label>Image (optional)</label>
                    <input name="image" type="file" accept="image/*">

                    <button type="submit">Submit Report</button>
                </form>
            </section>
        `;
    }

    function renderClaimsPage() {
        return `
            <section class="page">
                <h1>My Claims</h1>

                <div class="claims-list">
                    ${state.claims.map(claim => `
                        <article class="claim-card">
                            <h3>Claim #${esc(claim.id || claim.claim_id || "")}</h3>
                            <p>${esc(claim.claim_description || claim.description || "")}</p>
                            <span class="status">
                                ${esc(claim.status || "Pending")}
                            </span>
                        </article>
                    `).join("") || "<p>You have not submitted any claims.</p>"}
                </div>
            </section>
        `;
    }

    function renderNotificationsPage() {
        return `
            <section class="page">
                <h1>Notifications</h1>

                <div class="notifications-list">
                    ${state.notifications.length
                        ? state.notifications.map(n => `
                            <div class="notification">
                                <div class="n-icon">✧</div>
                                <div>
                                    <strong>${esc(n.message || "Notification")}</strong>
                                    <p>${formatDate(n.created_at)}</p>
                                </div>
                            </div>
                        `).join("")
                        : "<p>You have no notifications.</p>"
                    }
                </div>
            </section>
        `;
    }

    function renderLoginPage() {
        return `
            <section class="auth-page">
                <div class="auth-card">
                    <h1>Welcome to Findly</h1>
                    <p>Sign in to continue.</p>

                    <form id="login-form" class="app-form">
                        <label>Email</label>
                        <input name="email" type="email" required>

                        <label>Password</label>
                        <input name="password" type="password" required>

                        <button type="submit">Login</button>
                    </form>

                    <p>New here?
                        <a href="#register">Create an account</a>
                    </p>
                </div>
            </section>
        `;
    }

    function renderRegisterPage() {
        return `
            <section class="auth-page">
                <div class="auth-card">
                    <h1>Create your Findly account</h1>

                    <form id="register-form" class="app-form">
                        <label>Full name</label>
                        <input name="name" required>

                        <label>Email</label>
                        <input name="email" type="email" required>

                        <label>Password</label>
                        <input name="password" type="password" minlength="8" required>

                        <button type="submit">Register</button>
                    </form>

                    <p>Already registered?
                        <a href="#login">Login</a>
                    </p>
                </div>
            </section>
        `;
    }

    function renderPage() {
        const page = location.hash.replace("#", "") || "dashboard";
        state.currentPage = page;

        if (!state.user && page !== "login" && page !== "register") {
            location.hash = "login";
            return;
        }

        if (page === "login") {
            app.innerHTML = renderLoginPage();
        } else if (page === "register") {
            app.innerHTML = renderRegisterPage();
        } else {
            let content = "";

            switch (page) {
                case "items":
                    content = renderItemsPage();
                    break;
                case "report":
                    content = renderReportPage();
                    break;
                case "claims":
                    content = renderClaimsPage();
                    break;
                case "notifications":
                    content = renderNotificationsPage();
                    break;
                default:
                    content = renderDashboard();
            }

            app.innerHTML = renderHeader() + content;
        }

        attachEvents();
    }

    async function refreshData() {
        await Promise.all([
            loadItems(),
            loadClaims(),
            loadNotifications()
        ]);
    }function attachEvents() {
        const logoutButton = document.getElementById("logout-button");

        if (logoutButton) {
            logoutButton.addEventListener("click", logout);
        }

        const loginForm = document.getElementById("login-form");

        if (loginForm) {
            loginForm.addEventListener("submit", async event => {
                event.preventDefault();

                const form = new FormData(loginForm);

                try {
                    setLoading(true);

                    await api("/auth/login", {
                        method: "POST",
                        body: JSON.stringify({
                            email: form.get("email"),
                            password: form.get("password")
                        })
                    });

                    await loadUser();

                    if (!state.user) {
                        throw new Error("Login succeeded, but user session could not be verified.");
                    }

                    await refreshData();
                    toast("Login successful!", "success");
                    location.hash = "dashboard";
                } catch (error) {
                    toast(error.message || "Login failed.", "error");
                } finally {
                    setLoading(false);
                }
            });
        }

        const registerForm = document.getElementById("register-form");

        if (registerForm) {
            registerForm.addEventListener("submit", async event => {
                event.preventDefault();

                const form = new FormData(registerForm);

                try {
                    setLoading(true);

                    await api("/auth/register", {
                        method: "POST",
                        body: JSON.stringify({
                            name: form.get("name"),
                            email: form.get("email"),
                            password: form.get("password")
                        })
                    });

                    toast("Registration successful. Please log in.", "success");
                    location.hash = "login";
                } catch (error) {
                    toast(error.message || "Registration failed.", "error");
                } finally {
                    setLoading(false);
                }
            });
        }

        const reportForm = document.getElementById("report-form");

        if (reportForm) {
            reportForm.addEventListener("submit", async event => {
                event.preventDefault();

                const form = new FormData(reportForm);
                const image = form.get("image");

                const report = {
                    item_name: form.get("item_name"),
                    item_type: form.get("item_type"),
                    category: form.get("category"),
                    colour: form.get("colour"),
                    description: form.get("description"),
                    location: form.get("location"),
                    item_date: form.get("item_date")
                };

                try {
                    setLoading(true);

                    const result = await api("/items/", {
                        method: "POST",
                        body: JSON.stringify(report)
                    });

                    const itemId = result.id || result.item_id;

                    if (image && image.size > 0 && itemId) {
                        const imageData = new FormData();
                        imageData.append("image", image);

                        await api(`/items/${itemId}/image`, {
                            method: "POST",
                            body: imageData
                        });
                    }

                    toast("Item report submitted!", "success");
                    await refreshData();
                    location.hash = "items";
                } catch (error) {
                    toast(error.message || "Unable to submit report.", "error");
                } finally {
                    setLoading(false);
                }
            });
        }

        document.querySelectorAll(".view-item-button").forEach(button => {
            button.addEventListener("click", () => {
                const id = button.dataset.itemId;
                const item = state.items.find(
                    entry => String(getItemId(entry)) === String(id)
                );

                if (!item) return;

                const description = [
                    `Item: ${getItemName(item)}`,
                    `Location: ${getItemLocation(item)}`,
                    `Description: ${getItemDescription(item)}`
                ].join("\n");

                alert(description);
            });
        });
    }

    async function logout() {
        try {
            await api("/auth/logout", {
                method: "POST"
            });
        } catch (error) {
            console.error("Logout request failed:", error);
        }

        state.user = null;
        state.items = [];
        state.claims = [];
        state.notifications = [];

        toast("You have been logged out.");
        location.hash = "login";
    }

    async function startApp() {
        setLoading(true);

        try {
            const loggedIn = await loadUser();

            if (loggedIn) {
                await refreshData();

                if (!location.hash || location.hash === "#login") {
                    location.hash = "dashboard";
                } else {
                    renderPage();
                }
            } else {
                location.hash = "login";
                renderPage();
            }
        } catch (error) {
            console.error("Application startup error:", error);
            toast("Unable to connect to the server.", "error");
            renderPage();
        } finally {
            setLoading(false);
        }
    }

    window.addEventListener("hashchange", renderPage);

    startApp();

})();