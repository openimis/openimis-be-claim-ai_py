# openimis-be-claim-ai_py
# openIMIS Backend Claim AI reference module
This repository holds the files of the openIMIS Backend Claim AI reference module.
It is dedicated to be deployed as a module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## ORM mapping:
None

## Listened Django Signals
None

## Services
### ClaimConsumer, websocket service responsible for AI evaluation
Websocket connection is available at `claim_ai/ws/Claim/<process_id>/`. It accepts bytes which payloads which after
decoding utf-8 decoding are in format:
```json
{
  'type': <type>,
  'content': <payload_content>
}
```
### Payload types: 
* ### 'claim.bundle.payload'

  ##### Request:
  ```json
  {
    'type': 'claim.bundle.payload',
    'content': <FHIR Claim Bundle>,
    'bundle_id': <bundle_id> // Optional argument with bundle id used for bundle distinction
  }
  ```
  ##### Response:
  ```json
  {
    'type': 'claim.bundle.payload',
    'content': <FHIR ClaimResponse Bundle>,
    'index': <bundle_id> // bundle_id if it was given in request, subsequent numbers otherwise
  }
  ```
  Used for claim evaluation, request payload have to contain claim bundle in FHIR format,
  after request was accepted `'claim.bundle.acceptance'` is sent. After evaluation
  proper 'claim.bundle.payload' response with evaluation result is sent.
  

* ### 'claim.bundle.acceptance'

  ##### Request:
  ```json
  {
    'type': 'claim.bundle.acceptance',
    'content': <bundle_id> // index receieved from claim.bundle.payload
  }
  ```
  ##### Response:
  ```json
  {
     'type': 'claim.bundle.acceptance', 
     'content': 'Accepted', 
     'index': <bundle_id> // bundle_id if it was given in request, subsequent numbers otherwise
  }
  ```
  Request is expected to be receieved from client after FHIR claim repsonse bundle was correctly
  receieved. Response is sent after claim.bundle.payload was receieved from the server.
  

* ### 'claim.bundle.authentication_exception'
  ##### Response:
  ```json
  {
    'type': 'claim.bundle.authentication_exception',
    'content': 'Invalid authentication token'
  }
  ```
  If token authentication is used and invalid token was provided by client this payload
  is sent and connection is closed immediately.
* ### 'claim.bundle.authentication_exception'
  ##### Response:
  ```json
  {
    'type': 'claim.bundle.evaluation_exception', 
    'content': <error_message>, 
    'index': <bundle_id>
  }
  ```
  If any exceptions occurred during the evaluation exception message is returned to client.

## Reports (template can be overloaded via report.ReportDefinition)
None

## GraphQL Queries
None

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)
None

## Configuration options (can be changed via core.ModuleConfiguration)
* authentication: list of allowed tokens, when new connection is established client have 
  to send token in auth-token header, if authentication is empty list then all connection
  request are allowed. Empty by default.
* claim_response_url: url used in FHIR response as resource 'fullUrl' prefix,
* claim_response_organization: organization used in FHIR response, by default 'openIMIS-Claim-AI',
* date_format: date format used in FHIR response, by default YYYY-mm-dd

## openIMIS Modules Dependencies
The module is independent of the others.
