# TODO: Fix BuscarTrabajo-v2-Gemini.json - First Email Issue

## Current Status
- [x] Analyzed documentation and workflows
- [x] Identified root causes (disabled node, DB ID typo, hardcoded emails, inactive)

## Implementation Plan
- [ ] 1. Enable "Code — Normalizar users (schedule)" node
- [ ] 2. Fix Notion Ofertas DB ID 
- [ ] 3. Make Brevo Email Confirmación dynamic
- [ ] 4. Activate workflow ("active": true)

## Testing
- [ ] Manual trigger → verify users loaded → ofertas created → first email sent to correct user.email
- [ ] Schedule 9am test
- [ ] Webhook /buscar-para-user test

## Completion Criteria
- First notification email arrives at user.email (not hardcoded)
- All Brevo nodes dynamic
- Workflow active and functional
