# Finance Portal Support Guide

## Overview

The Finance Portal is an internal business-critical application used by Finance, Payroll, HR Operations, and approved managers. It is used for payroll processing, expense approvals, vendor payments, budget review, and monthly financial close activities.

## Common User Issues

### Access Denied

If a user sees "Access Denied" after reaching the Finance Portal login page, the most common causes are:

- The user does not have the required application role.
- The user's role assignment expired.
- The user recently changed departments and access was not re-approved.
- The user is attempting to access a restricted payroll or vendor payment module.
- The user's account is active but not mapped to a Finance Portal permission group.

Access Denied usually means the application is reachable, but the user is not authorized.

### Portal Not Loading

If the portal does not load at all, possible causes are:

- VPN is disconnected.
- Finance Portal service is unavailable.
- Internal DNS is not resolving the portal address.
- User is outside the corporate network without VPN.
- Browser cache or stale session issue.

### Login Loop

If the user repeatedly returns to the login screen, possible causes are:

- Expired single sign-on session.
- Browser cookies blocked.
- Identity provider token issue.
- User account requires password reset.

## Required Access Roles

Payroll-related work requires the FINANCE_PAYROLL role.

Finance Portal roles:

- FINANCE_VIEWER: Can view finance dashboards and reports.
- FINANCE_APPROVER: Can approve finance workflows.
- FINANCE_PAYROLL: Can access payroll processing modules.
- FINANCE_ADMIN: Can manage finance application configuration.

## Troubleshooting Steps

For access denied issues:

1. Confirm the user can connect to VPN.
2. Confirm the Finance Portal service is online.
3. Confirm the user's corporate account is active.
4. Check whether the user has the required Finance Portal role.
5. If the user lacks the required role, create an access request.
6. If the user has the correct role but still cannot access the portal, create a support ticket for the Finance Systems team.

## Escalation Rules

Create a high-priority support ticket if:

- Payroll processing is blocked.
- Month-end close is blocked.
- Multiple finance users are impacted.
- A director or payroll operator cannot complete time-sensitive work.

If the issue affects one user and involves payroll or financial close, classify it as at least P2.

## Agent Instruction

When a user reports Finance Portal access issues, the agent should not assume it is a VPN issue. The agent should check VPN status, Finance Portal status, user account status, and user application permissions.
