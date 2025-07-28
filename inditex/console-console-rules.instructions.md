# Console Usage Guidelines

## 🎯 Objective
This rule ensures that all shell commands executed by Cline are **non-interactive** and **cannot hang**, preventing the agent from becoming blocked.

---

## 🛡️ Core Principle: Never Block the Agent

Every command executed in the terminal **MUST** be non-interactive and finite. It should run to completion without requiring user input and without producing an excessive amount of output that could cause a buffer overflow.

### Best Practices

#### 1. Use Non-Interactive Flags
**ALWAYS** use flags to prevent commands from waiting for user input.

*   ✅ **Correct:**
    ```bash
    # Use non-interactive or batch flags
    sudo -n ls
    top -b -n 1
    apt-get install -y my-package
    ```
*   ❌ **Incorrect:**
    ```bash
    # These commands will hang waiting for input
    sudo ls
    top
    apt-get install my-package
    ```

#### 2. Avoid Interactive Tools
**NEVER** use interactive programs that take over the terminal session. Use non-interactive alternatives.

*   ✅ **Correct:**
    ```bash
    # Use non-interactive alternatives
    cat my-file.txt
    head -n 20 my-file.txt
    ```
*   ❌ **Incorrect:**
    ```bash
    # These tools will block the agent
    less my-file.txt
    vi my-file.txt
    nano my-file.txt
    ```

#### 3. Limit Command Output
**ALWAYS** pipe long outputs to a command like `head` to prevent buffer overflows.

*   ✅ **Correct:**
    ```bash
    # Limit output to a reasonable number of lines
    long-running-command | head -n 100
    ```
*   ❌ **Incorrect:**
    ```bash
    # This may produce thousands of lines and block the read
    long-running-command
    ```

#### 4. Use Timeouts for Risky Commands
If a command has the potential to run for too long, **SHOULD** be wrapped in a `timeout`.

*   ✅ **Correct:**
    ```bash
    # Ensure the command exits after 15 seconds
    timeout 15s some-unpredictable-command
    ```

#### 5. Suppress or Redirect `stderr`
To prevent failures from noisy `stderr` output, **SHOULD** redirect it, especially if the errors are not critical to the task.

*   ✅ **Correct:**
    ```bash
    # Suppress stderr completely
    command 2>/dev/null

    # Or, pipe both stdout and stderr to head
    command 2>&1 | head -n 50

#### 6. Handle `git` and `gh` Interactivity
Many `git` and `gh` commands open an editor or an interactive prompt by default. **ALWAYS** use flags or environment variables to prevent this.

*   ✅ **Correct:**
    ```bash
    # Provide a merge message directly
    git merge --no-ff --no-edit my-branch

    # Rebase the current branch onto main. This is non-interactive unless conflicts occur.
    git rebase main

    # Create a GitHub PR non-interactively
    gh pr create --title "My PR Title" --body "Description of my PR." --fill
    ```
*   ❌ **Incorrect:**
    ```bash
    # These will open an editor or interactive prompt
    git merge my-branch
    # Interactive rebase requires user input
    git rebase -i my-commit-hash
    gh pr create
    ```
