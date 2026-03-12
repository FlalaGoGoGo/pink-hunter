# GitHub Pages Custom Subdomain Setup

## Goal
Host Pink Hunter on the custom subdomain `pinkhunter.flalaz.com` with GitHub Pages.

## Required Files
- `public/CNAME`
- `.github/workflows/deploy-pages.yml`

## DNS Record
- Type: `CNAME`
- Host: `pinkhunter`
- Target: `FlalaGoGoGo.github.io`

## GitHub Pages Settings
1. Repo: `FlalaGoGoGo/pink-hunter`
2. Pages source: `GitHub Actions`
3. Custom domain: `pinkhunter.flalaz.com`
4. Turn on `Enforce HTTPS` after GitHub finishes issuing the certificate.

## Notes
- The same deployed site is intended for both desktop and mobile access.
- If the domain changes later, update `public/CNAME`, GitHub Pages settings, and DNS together.
