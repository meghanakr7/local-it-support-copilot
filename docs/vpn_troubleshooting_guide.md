# VPN Troubleshooting Guide

## Overview

The corporate VPN allows employees to access internal applications from outside the office network.

## Common Symptoms

Users may report:

- VPN not connecting.
- VPN connected but internal sites not loading.
- VPN disconnecting repeatedly.
- Authentication failure.
- Slow internal application performance.

## Basic Troubleshooting

Ask the user to try the following:

1. Confirm internet connection is working.
2. Restart the VPN client.
3. Restart the laptop.
4. Confirm username and password are correct.
5. Check whether multi-factor authentication was approved.
6. Try connecting from a different network if available.

## When VPN Is Connected but App Access Fails

If VPN is connected but a specific application says "Access Denied," the issue is probably not the VPN. The agent should check application permissions.

## Service-Wide VPN Problems

If many users are affected, the VPN monitoring service may show one of these statuses:

- healthy
- degraded
- down
- unknown

If VPN status is degraded or down, create a support ticket.

## Escalation Rules

Create a support ticket if:

- The user already restarted the VPN client and laptop.
- VPN service status is degraded or down.
- The user is blocked from urgent business work.
- The issue affects more than one user.
- The monitoring tool is unavailable.

## Agent Instruction

The agent should check VPN service status before creating a ticket, unless the monitoring tool is unavailable. If monitoring fails, the agent should create a ticket noting that service status could not be verified.
