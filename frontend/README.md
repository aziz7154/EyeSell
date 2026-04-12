# EyeSell — Frontend

Static HTML/CSS frontend for EyeSell. All pages link to each other and are ready to be served through Nginx on EC2.

## Pages

| File | Route | Description |
|---|---|---|
| `index.html` | `/` | Landing page |
| `login.html` | `/login` | Login and sign up |
| `upload.html` | `/upload` | Image upload form — POSTs to Flask `/upload` |
| `results.html` | `/results` | Pricing results and similar listings |
| `generate.html` | `/generate` | Auto-generated listing editor |
| `dashboard.html` | `/dashboard` | Saved listings and stats |

## Shared

`shared.css` — CSS variables, nav, buttons, form elements used across all pages.

## Dev

Open any `.html` file with the Live Server extension in VS Code to preview locally.

## Notes

- `upload.html` POSTs to `/upload` on the Flask backend via `fetch()`
- On success Flask should return `{ "id": <listing_id> }` and the page redirects to `results.html?id=<id>`
- Google OAuth in `login.html` is a placeholder — wire to Flask backend when ready
