# Findly — Frontend starter

Responsive frontend for the AI-Based Smart Lost-and-Found Item Recovery & Management System.

## 1. Run it
No build tools are required.

- Unzip the folder.
- Open `index.html` in a browser, or run a local server from this folder:
  - `python -m http.server 8000`
  - Visit `http://localhost:8000`

The interface includes a demo mode with sample reports and AI match cards. Demo submissions are validated in the browser but are **not persisted** until the Flask backend is connected.

## 2. Pages included
- Overview / dashboard
- Register and login
- User profile
- Report lost item
- Report found item
- My submitted reports
- Search found items with text, category and location filters
- Possible AI matches with similarity scores
- Ownership claim submission
- Notifications
- Recovery status tracker
- Admin dashboard preview

## 3. Connect to the Flask backend
Open `app.js` and change:

```js
const API_BASE = "";
```

to your backend URL, for example `http://127.0.0.1:5000/api`.

The frontend currently expects these example endpoints. Coordinate the exact names and request/response shapes with Member 2 before integration.

| Method | Example endpoint | Purpose |
|---|---|---|
| POST | `/auth/register` | Register user (JSON) |
| POST | `/auth/login` | Login user (JSON) |
| POST | `/auth/logout` | End session |
| GET | `/profile` | Load profile |
| PUT | `/profile` | Update profile (JSON) |
| POST | `/items` | Create lost/found report (`multipart/form-data`) |
| GET | `/items` | List/search reports |
| GET | `/matches` | Retrieve AI-ranked matches |
| POST | `/claims` | Submit ownership claim (JSON) |
| GET | `/claims` | List user's claims |
| GET | `/notifications` | List notifications |
| GET | `/recovery` | Retrieve recovery history |
| GET | `/admin/reports` | Admin report queue |
| PATCH | `/admin/reports/:id` | Approve/reject report |
| PATCH | `/admin/claims/:id` | Approve/reject claim |

The UI currently has working demo interactions for report form validation, claim form validation, search filtering and navigation. To finish integration, replace demo arrays with API data and render the returned data. The example `api()` helper uses `fetch` with credentials for Flask cookie sessions.

## 4. Suggested integration agreement
Ask the backend member to confirm:
1. The API base URL and endpoint paths.
2. Whether authentication uses Flask sessions/cookies or tokens.
3. Exact field names for item and claim payloads.
4. Image upload size/type limits and whether the server returns an image URL.
5. The response structure for AI matches (item details plus text/image/combined scores).
6. Admin role enforcement and error response format.

## 5. Important security notes
- Frontend role-based navigation is not security. Flask must enforce authentication, ownership and admin permissions on every protected endpoint.
- Validate file size/type on the server, not only in the browser.
- Escape user-generated text before rendering it.
- Do not expose private claim evidence or sensitive identifying details on public item pages.
- AI similarity scores are suggestions, not proof of ownership.
- Use HTTPS and secure, HttpOnly, SameSite cookies in deployment.

## 6. Suggested work checklist for Member 1
- [ ] Run the frontend locally and check every page.
- [ ] Replace demo text, logo and profile name with the project team's final details.
- [ ] Confirm API contract with Member 2.
- [ ] Connect report submission and image upload.
- [ ] Connect search and AI match results.
- [ ] Connect claims, notifications and recovery status.
- [ ] Test on mobile and desktop.
- [ ] Send the folder to the team and commit it to the shared GitHub repository.
