# Auth and resource-access matrix

Read the application's auth contract and JWT library/configuration first. Keep the real validation and authorization path for tests that claim to verify it. A fixture returning a fixed user is acceptable for unrelated behavior, but excludes auth from that test's coverage.

| Contract area | Cases and observable outcome |
| --- | --- |
| Token parsing and trust | Missing, malformed, invalid signature, wrong/disallowed algorithm; rejection must come from the intended validator |
| Expiration and activation | Before, at and after exp/nbf boundaries, with configured leeway and a controlled clock; do not sleep or invent a tolerance |
| Issuer and audience | Correct and incorrect values, and missing claims, when required by the contract |
| Permission | Valid token without required role/scope; actual error status, body and absence of forbidden side effects |
| Ownership | Valid user A reads/updates/deletes B's resource; include same-role users so a generic role check cannot mask a missing ownership check |
| Tenant | Cross-organization access when the domain supports tenancy |
| Account/token lifecycle | Disabled account or revoked token only when the application implements the policy |

Choose 401/403/404 and error details from the documented API contract; different products intentionally conceal resource existence differently. Do not migrate session/API-key auth to JWT or introduce revocation, issuer or audience requirements without a basis.

For an important permission regression, demonstrate that removing the ownership predicate causes the test to fail in an isolated reversible experiment when authorized. A rejected request should also leave the protected resource unchanged. Token helpers should mint controlled inputs, not bypass the validator under test.
