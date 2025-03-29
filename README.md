🔒 Protected Resource Access
This release introduces restricted folder access:

Account/ folder → Only accessible via EtherealAccount.pyw
License/ folder → Only accessible via License_Key.bat
🛡️ Security Implementation

Folders are hidden by default (Windows-only)
Direct access attempts will fail without proper authentication
All access logs are recorded in secure_access.log
🚀 How to Use

Accounts: Run EtherealAccount.pyw to:

Register/login users
Access account data (stored in Account/accounts.json)
Licenses: Run License_Key.bat to:

Validate license keys
Modify License/keys.json
⚠️ Important Notes

Do not manually modify folder contents - use the provided launchers
Pre-release tag (v1.0.0-beta) used for testing feedback
