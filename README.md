<div align="center">

# Netflix Checker

### Netflix Session Analysis & Account Metadata Utility

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Requests-HTTP%20Client-20232A?style=for-the-badge&logo=python&logoColor=white" alt="Requests">
  <img src="https://img.shields.io/badge/Threads-30%20Default-6C5CE7?style=for-the-badge" alt="Threads">
  <img src="https://img.shields.io/badge/Status-Research-00A67E?style=for-the-badge" alt="Status">
</p>

<p>
  A high-performance Python utility for <b>authorized security testing</b>,
  session validation, and structured account-metadata analysis.
</p>

<br>

</div>

---

## ⚡ Overview

**Netflix Checker** is a Python-based session analysis utility designed for controlled security research and authorized testing environments.

It processes exported session-cookie data, establishes authenticated HTTP sessions, analyzes the resulting account response, and organizes the collected metadata into structured output categories.

The project focuses on:

* ⚡ Concurrent processing
* 🍪 Multiple cookie formats
* 🔎 Session validation
* 📊 Account metadata extraction
* 🗂️ Automatic result organization
* 🔁 Duplicate detection
* 📡 Optional notification integrations
* 🧩 Configurable output fields

> **Important:** This project is intended only for accounts, sessions, and data that you own or are explicitly authorized to test.

---

## ✦ Feature Set

<table>
<tr>
<td width="50%" valign="top">

### 🍪 Cookie Processing

Supports multiple common cookie representations:

* Netscape cookie format
* `key=value` strings
* JSON cookie objects
* Line-based cookie files
* Automatic normalization
* Duplicate detection

</td>
<td width="50%" valign="top">

### 🔍 Session Analysis

Authenticated sessions can be analyzed for available account information, including:

* Account status
* Membership information
* Country
* Billing information
* Profile information
* Account identifiers
* Subscription metadata

</td>
</tr>

<tr>
<td width="50%" valign="top">

### ⚡ Concurrent Engine

Uses Python's `ThreadPoolExecutor` for concurrent processing.

Configurable:

```python
THREADS = 30
TIMEOUT = 15
```

This allows the processing engine to be tuned for different controlled testing environments.

</td>
<td width="50%" valign="top">

### 🗂️ Automatic Organization

Results are separated into logical categories such as:

* Active accounts
* Free accounts
* Invalid sessions
* Expired sessions
* On-hold accounts
* Duplicate entries
* Other detected account states

</td>
</tr>
</table>

---

# 🧠 How It Works

```text
                    ┌──────────────────────┐
                    │     Input Cookies    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Parse & Normalize  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Duplicate Detection  │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌─────────────────────────────┐
                 │ Concurrent Session Analysis │
                 └──────────────┬──────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Account Information  │
                    │      Extraction      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Result Classification│
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        ┌────────────────┐          ┌────────────────┐
        │ Local Results  │          │ Notifications │
        └────────────────┘          └────────────────┘
```

---

# 🧰 Supported Analysis

Depending on what the authenticated response exposes, the utility can identify fields such as:

| Category      | Examples                           |
| ------------- | ---------------------------------- |
| Account       | Name, email, country               |
| Membership    | Status, member-since date          |
| Subscription  | Plan, quality, stream limits       |
| Billing       | Next billing information           |
| Profiles      | Profile count and profile metadata |
| Security      | Email verification state           |
| Account State | Active, expired, held, etc.        |
| Identifiers   | Account/user GUID information      |
| Payment       | Available payment metadata         |
| Extras        | Additional membership information  |

The individual fields can be enabled or disabled through the configuration section.

---

# ⚙️ Configuration

The main configuration is located near the top of `Netflix-checker.py`.

### Processing

```python
THREADS = 30
TIMEOUT = 15
```

### Output directories

```python
COOKIE_FOLDER = "cookies"
OUTPUT_FOLDER = "output"
FAILED_FOLDER = "failed"
BROKEN_FOLDER = "broken"
```

### Account fields

The script exposes configuration switches for fields such as:

```text
SHOW_NAME
SHOW_EMAIL
SHOW_PLAN
SHOW_PRICE
SHOW_COUNTRY
SHOW_STREAMS
SHOW_QUALITY
SHOW_PROFILES
SHOW_MEMBER_SINCE
SHOW_NEXT_BILLING
SHOW_PAYMENT
SHOW_PHONE
SHOW_HOLD
SHOW_EXTRA_MEMBERS
SHOW_EMAIL_VERIFIED
SHOW_MEMBERSHIP_STATUS
SHOW_USER_GUID
```

This makes the output configurable without changing the processing architecture.

---

# 📁 Project Structure

```text
Netflix-Checker/
│
├── Netflix-checker.py
│
├── cookies/
│   └── *.txt / *.json
│
├── output/
│   └── processed results
│
├── failed/
│   └── failed sessions
│
└── broken/
    └── malformed or unusable input
```

The required directories are created automatically when the program starts.

---

# 🚀 Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/Hidden-Rhythm/Netflix-Checker.git
cd Netflix-Checker
```

## 2. Install the dependency

```bash
pip install requests
```

## 3. Prepare authorized test data

Place session data belonging to accounts you are authorized to test inside:

```text
cookies/
```

Supported input representations are handled by the parser.

## 4. Run

```bash
python Netflix-checker.py
```

The program will initialize its folders, process the available inputs, and organize the resulting classifications.

---

# 📊 Processing Pipeline

### `01` — Input

Cookie/session data is loaded from the configured input directory.

### `02` — Parsing

The parser normalizes supported cookie representations into a consistent internal structure.

### `03` — Validation

Required session cookies are checked before attempting analysis.

### `04` — Session

An HTTP session is created and the supplied cookies are attached to the relevant domain.

### `05` — Analysis

The application response is inspected for available account and membership metadata.

### `06` — Classification

The session is assigned to the appropriate result category.

### `07` — Output

Results are written into the appropriate output directories.

### `08` — Notification

If explicitly configured for an authorized environment, optional notification integrations can report processing results.

---

# 📡 Optional Notifications

The project includes optional integrations for:

* Discord webhooks
* Telegram bots

Notification behavior can be configured according to the available result information.

Supported notification modes include different levels of result detail.

> Keep webhook URLs, bot tokens, chat identifiers, and any session material private. Never commit them to Git.

---

# 🛡️ Security & Responsible Use

This project interacts with authenticated session material. Treat that material as **highly sensitive authentication data**.

### Never:

* Use cookies belonging to another person without authorization.
* Attempt to access accounts you do not own.
* Distribute harvested session credentials.
* Upload session data to public repositories.
* Commit webhook tokens or bot credentials.
* Use the tool to bypass account security.
* Use the project against systems without permission.

### Recommended:

* Use synthetic or personally owned test accounts.
* Run the project locally.
* Keep input/output directories private.
* Remove sensitive data after testing.
* Rotate credentials if accidental exposure occurs.
* Use isolated testing environments whenever possible.

---

# 🔐 Sensitive Data Warning

Session cookies can provide authenticated access to services.

For that reason:

```text
cookies/
output/
failed/
broken/
```

should generally be treated as **private directories**.

A suitable `.gitignore` should include sensitive runtime data, for example:

```gitignore
cookies/
output/
failed/
broken/
__pycache__/
*.pyc
```

---

# 🧪 Intended Use Cases

This project can be useful for legitimate scenarios such as:

* Security research
* Personal account testing
* Controlled session validation
* HTTP/session parsing experiments
* Automation research
* Cookie-format parsing
* Concurrent request testing
* Account metadata analysis in authorized environments

---

# 📈 Performance

The checker uses a thread pool to process multiple inputs concurrently.

Default:

```text
Workers: 30
Timeout: 15 seconds
```

The worker count can be adjusted according to the size of the authorized test set and the capabilities of the environment.

More threads do **not** automatically mean better performance. Excessive concurrency can increase resource usage and cause unnecessary request pressure.

---

# 🧩 Technical Stack

<div align="center">

|       Technology      | Purpose                  |
| :-------------------: | ------------------------ |
|       🐍 Python       | Core application         |
|      🌐 Requests      | HTTP communication       |
| 🧵 ThreadPoolExecutor | Concurrent processing    |
|        📦 JSON        | Structured data handling |
|  🔐 Base64 / Hashlib  | Data processing          |
| 📡 Discord / Telegram | Optional notifications   |

</div>

---

# 🗺️ Project Architecture

```text
                    Netflix-checker.py
                           │
             ┌─────────────┴─────────────┐
             │                           │
        Configuration                Utilities
             │                           │
             ├──────────────┐            │
             │              │            │
          Parsers        Validators    Formatters
             │              │            │
             └──────────────┴────────────┘
                           │
                           ▼
                  Session Processing
                           │
                           ▼
                  Account Analysis
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           Active       Invalid       Other
              │            │            │
              └────────────┼────────────┘
                           ▼
                       Output
                           │
                           ▼
                    Notifications
```

---

# ⚠️ Limitations

The output depends on the information exposed by the service response and the validity of the supplied session data.

Results may vary because of:

* Session expiration
* Account state changes
* Service-side changes
* Response format changes
* Network failures
* Rate limiting
* Invalid or incomplete cookies
* Changes to authentication mechanisms

This project should therefore **not** be treated as a permanent compatibility guarantee.

---

# 👤 Author

<div align="center">

### Hidden-Rhythm

Building small tools, experiments, and automation projects.

<br>

<a href="https://github.com/Hidden-Rhythm">
  <img src="https://img.shields.io/badge/GitHub-Hidden--Rhythm-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>

</div>

---

# 📜 License

No explicit open-source license is currently included in this repository.

Unless a license is added, the repository should **not** be assumed to grant permission to redistribute, modify, or commercially use the code.

---

<div align="center">

### Built for authorized research & experimentation.

**Use responsibly. 🔐**

<br>

<sub>Hidden-Rhythm · Netflix Checker</sub>

</div>
