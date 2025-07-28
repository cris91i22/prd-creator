# Inditex

You are working for Inditex, the parent company of Zara, Pull&Bear, Massimo Dutti, Bershka, Stradivarius, Oysho, Lefties and Zara Home.

## Project Organization

- **Applications**: Functional assets identified by unique asset keys in the software catalog
- **Artifacts**: Tangible by-products linked to specific applications and identified by unique project keys in GitHub

## Repository Types

Repositories on Inditex are created using a prefix that identifies the type of repository.

| Type | Description                   |
| ---- | ----------------------------- |
| app  | Application parent repository |
| cac  | Configuration as code         |
| cli  | Desktop client                |
| clr  | Command line runner           |
| doc  | Documentation                 |
| fun  | Serverless Function           |
| iac  | Infrastructure as code        |
| job  | Batch job                     |
| lib  | Library                       |
| mic  | Microservice                  |
| mlb  | Mobile library                |
| mob  | Mobile application            |
| spa  | Single page application       |
| tst  | Test suite                    |
| wsc  | Web service                   |

## Repository Structure

Repositories follow a common structure across all types.

### Application Repositories

| Directory  | Purpose                        | Inditex Product Name |
| ---------- | ------------------------------ | -------------------- |
| api        | API specifications             | API                  |
| docs       | Documentation                  | Amiga Tech Docs      |
| escalation | Alert escalation configuration | Monin                |
| pumba      | Process automation scripts     | Pumba                |

### Artifact Repositories

| Directory  | Purpose                        | Inditex Product Name |
| ---------- | ------------------------------ | -------------------- |
| apigateway | Kong API gateway configuration | Janus                |
| code       | Source code                    | Amiga Framework      |
| database   | Database migration scripts     | Themis               |
| docs       | Documentation                  | Amiga Tech Docs      |
| horus      | Deployment control tool        | Horus                |
| icarus     | K6 load tests                  | Icarus               |
| jobs       | Batch as job configuration     | BatchAsCode          |
| monit      | Alerts configuration           | Alerthub             |
| paas       | Kubernetes configuration       | PaaS Sentinel        |
| pipe       | Kafka configuration            | Pipe                 |

