# Source and Ethics Policy

SentinelOSINT is a defensive research and situational-awareness project.

## Allowed collection

- official government and intergovernmental public feeds
- openly accessible news reporting
- public RSS and JSON feeds
- security advisories and vulnerability catalogs
- public disaster and hazard data

## Out of scope

- private or restricted accounts
- credential theft or session bypass
- scraping behind authentication without authorization
- doxxing or identifying private persons for targeting
- stalking or covert monitoring of individuals
- facial recognition or biometric identification
- deceptive personas or social engineering
- collection intended to facilitate harm

## Verification policy

A discovered item is not automatically verified. The data model preserves source type and confidence separately from priority. Open-web items should be corroborated before analyst verification or operational escalation.

## Synthetic scenarios

The built-in demonstration dataset is synthetic and explicitly marked with `synthetic=true`. Fictional assets use real city coordinates only to demonstrate geospatial relevance scoring; they do not represent a real employer's facilities.
