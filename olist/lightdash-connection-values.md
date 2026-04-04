# Lightdash connection values

Use the following values when configuring the Snowflake warehouse connection in Lightdash.

## Connection settings

- **Account:** `vrsugdf-gx74482`
- **User:** `LIGHTDASH`
- **Role:** `REPORTER`
- **Warehouse:** `COMPUTE_WH`
- **Database:** `OLIST`
- **Schema:** `DEV`

## Key files

- **Private key to paste into Lightdash:** `.secrets/lightdash/lightdash_rsa_key.p8`
- **Public key registered in Snowflake:** `.secrets/lightdash/lightdash_rsa_key.pub`
- **Snowflake SQL setup script:** `scripts/lightdash_user_setup.sql`

## Paste format

Paste the full contents of `lightdash_rsa_key.p8`, including:

```pem
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
```

This key is already in unencrypted PKCS8 PEM format, which is the cleanest format for Lightdash to accept.
