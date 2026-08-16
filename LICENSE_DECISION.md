# License Decision

## Decision: Apache License 2.0

EvidenceBound Core is infrastructure intended for broad reuse by companies, researchers and open-source agent frameworks. Apache-2.0 was selected because it is OSI-approved, permissive, permits commercial use, and includes an explicit contributor patent license and patent-termination mechanism useful for infrastructure adoption.

## Alternatives considered

**MIT** is shorter and highly permissive, and two reviewed EvidenceBound reference repositories use it. It does not contain Apache-2.0's explicit patent grant language.

**Apache-2.0** is longer but better expresses the project’s intended patent/contribution boundary. A reviewed EvidenceBound DataHub reference implementation already uses Apache-2.0; the core itself is nevertheless a clean implementation and does not depend on relicensing copied code.

Copyleft licenses were not selected for this initial infrastructure package because the adoption goal includes thin integration into otherwise differently licensed agent systems.

This document records an engineering/OSS licensing rationale, not legal advice. Contributor-license or trademark policy may be revisited before institutional funding or major external contributions.
