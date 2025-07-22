#!/bin/bash

# Add test accounts to the keyring
echo "Setting up test accounts..."

# Add alice account (if not exists)
contribledgerd keys add alice --keyring-backend test --output json 2>/dev/null || echo "Alice account already exists"

# Add more test accounts for clients
contribledgerd keys add client001 --keyring-backend test --output json 2>/dev/null || echo "client001 account already exists"
contribledgerd keys add client002 --keyring-backend test --output json 2>/dev/null || echo "client002 account already exists"
contribledgerd keys add client003 --keyring-backend test --output json 2>/dev/null || echo "client003 account already exists"
contribledgerd keys add client004 --keyring-backend test --output json 2>/dev/null || echo "client004 account already exists"

echo "Test accounts created!"

# List all accounts
echo "Available accounts:"
contribledgerd keys list --keyring-backend test