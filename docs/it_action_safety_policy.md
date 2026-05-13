# IT Action Safety Policy

## Purpose

This policy defines which actions the IT Support Agent can perform automatically.

## Safe Read-Only Actions

The agent may automatically check VPN service status, application service status, user account status, user application permissions, software approval, and device health.

## Safe Write Actions

The agent may automatically create support tickets, access requests, software installation requests, security incidents, mock email notifications, and audit logs.

## Restricted Actions

The agent must not automatically grant sensitive access, unlock accounts without identity verification, reset passwords directly, disable accounts, delete files or records, change payroll data, change HR data, change finance data, or modify production systems.

## Approval Required Actions

Granting Finance Portal roles, granting admin access, account unlock, password reset, installing restricted software, and closing security incidents require human approval.

## Agent Instruction

Before performing any write action, the agent should ensure the action is allowed by this policy. If an action is restricted, the agent should create a request or ticket instead of performing the action directly.
