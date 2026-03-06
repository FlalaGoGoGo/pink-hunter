# GitHub Pages Custom Subdomain Setup

## Goal
Host Pink Hunter on a subdomain such as `pinkhunter.yourdomain.com` using GitHub Pages.

## What is already prepared
- GitHub Pages deployment workflow: `.github/workflows/deploy-pages.yml`
- Static site build: `npm run build`
- Public data files are already committed under `public/data/`

## Final setup steps after the repo is on GitHub
1. Choose the exact subdomain.
   - Example: `pinkhunter.example.com`
2. Create a `public/CNAME` file with only that hostname on one line.
   - Example content: `pinkhunter.example.com`
3. Push that change to `main`.
4. In GitHub, open the repo settings and enable Pages with `GitHub Actions` as the source.
5. In your DNS provider, create a `CNAME` record:
   - Host: the subdomain part, for example `pinkhunter`
   - Target: `<your-github-username>.github.io`
6. Wait for DNS to propagate, then confirm the custom domain inside GitHub Pages settings.
7. If GitHub offers `Enforce HTTPS`, turn it on after the certificate is issued.

## Notes
- This app is already responsive, so the same deployed URL works on desktop and mobile.
- If you later change the subdomain, update `public/CNAME` and the DNS record together.
