## UI Design Guideline

- Using Tabler UI - looks great
- General idea is to reduce the number of clicks required to complete common tasks.

## Security Summary/Design Guideline

### Nothing can occur without a token (except for during the install process)

This simplifies the security of the app down to the internal permissions and the token generation and validation process. Limiting the attack surface to the tokens. An attacker must obtain a valid token to do anything. This puts the dependency more then on token checking/validation, how long they last and the login process. More on the login process below.

### The highest level of security (and an equal level) must be applied to the breakglass account, app database user and root database user

The root user is used briefly and deleted for the app to never remember it. The install process must never be run from an external computer over a network, if so the password will be transmitted in plaintext.

All 3 accounts provide the same level access (to access all information). And their security profile must be the same.

e.g. you can not change the breakglass account password without logging in with it first (no write up), or manually updating the table entry with the database user. No other user can, all other users will inheriently have a lower level of permissions and lower integrity level and should never be able to modify a higher level.

The system will be be read down, write down. A Clark-Wilson model is going to be followed throughout.

### Difficult logon process

The logon process must be computationally difficult but fast enough (and eventually use MFA).

### No expense spared on passwords (complex password policies are unnecessary and annoying, long passwords are enough until 2FA is set up). Where's that entropy calculator

They must be long, breakglass must be at least 30 characters.

2FA will be multi-channel, somthing you know, something you have. Standard stuff

### Cryptography

#### Aggressive suggestion of use of valid certs

The installation process does not include installing an SSL certificate, the app however, will aggressive suggest this until it's done. I may even disable certain features until it's done. The application security is undermined if this is not configured.

#### Token Generation

Will be random numbers, stored in a database. I don't want anything stateless like HMAC or JWT, or any other kind simply because I want the app to have very nuanced control over tokens, expiries, global non-user associated tokens with custom permissions etc.

I don't want to use a library for this, I wanted to come up with a solution myself for the fun and interest factor. Will perhaps look in to how to get a HMAC stateless style token working with a secret.

## Error Management and Logging

- print will be consistently used to write all exceptions to console
- when exceptions occur, after print, they are raised again futher up until a json object can be return to the client from the api call. That way the end user gets the error, and the server logs it in the console for full visiblity
- each exception message should by customised to easily located it in code - also should be closely related to the name of the function
- TODO: Need a log file