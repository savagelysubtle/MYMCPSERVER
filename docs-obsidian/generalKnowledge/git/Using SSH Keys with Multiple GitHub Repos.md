---
created: 2024-04-01 # Placeholder, replace with actual date
updated: 2024-04-01 # Placeholder, replace with actual date
tags: [guide, git, ssh, authentication, github, general-knowledge]
parent: [[_index]] # Link to git index
up: [[_index]] # Link to git index
siblings: []
implements: []
references: []
related: ['[[../docsGuide/Linking Strategy]]'] # Example if needed
based_on_decision: []
informed_by_research: []
next: []
previous: []
---

# Using SSH Keys with Multiple GitHub Repos

## Overview

Once you have successfully generated an SSH key pair and added the public key to your GitHub account, you can easily configure multiple local Git repositories (both existing and new ones) to use this SSH key for authentication instead of HTTPS. This allows you to push and pull from private repositories without entering credentials.

## Key Points

- SSH authentication uses key pairs, avoiding the need for passwords or Personal Access Tokens (PATs) for each interaction.
- The core task is ensuring your local repository's remote URL uses the SSH format (`git@github.com:...`) instead of the HTTPS format (`https://github.com/...`).
- This change needs to be made on a per-repository basis.

## Procedure

Follow these steps for each local repository you want to configure for SSH access:

1.  **Navigate to the Repository:**
    Open your terminal (like Git Bash) and change directory (`cd`) into the root folder of your local repository.

    ```bash
    cd /path/to/your/local/repository
    ```

2.  **Check the Current Remote URL:**
    Use the `git remote -v` command to view the URLs associated with your remotes (usually named `origin`).

    ```bash
    git remote -v
    ```

    - **Output (HTTPS - Needs Changing):**
      ```
      origin  https://github.com/YourUsername/YourRepoName.git (fetch)
      origin  https://github.com/YourUsername/YourRepoName.git (push)
      ```
    - **Output (SSH - Already Correct):**
      ```
      origin  git@github.com:YourUsername/YourRepoName.git (fetch)
      origin  git@github.com:YourUsername/YourRepoName.git (push)
      ```

3.  **Change the Remote URL (If Necessary):**
    If your output from step 2 shows HTTPS URLs, use the `git remote set-url` command to change the `origin` remote's URL to the SSH format. **Replace `YourUsername` and `YourRepoName` with your actual GitHub username and the repository's name.**

    ```bash
    git remote set-url origin git@github.com:YourUsername/YourRepoName.git
    ```

    - **Note:** If your remote has a different name than `origin`, replace `origin` in the command with the correct name.

4.  **Verify the Change:**
    Run `git remote -v` again to confirm that both the fetch and push URLs now use the `git@github.com:` format.
    ```bash
    git remote -v
    ```
    - **Expected Output:**
      ```
      origin  git@github.com:YourUsername/YourRepoName.git (fetch)
      origin  git@github.com:YourUsername/YourRepoName.git (push)
      ```

## Cloning New Repositories with SSH

When cloning _new_ repositories from GitHub, make sure you copy the SSH clone URL from the GitHub repository page (usually available under the `<> Code` button) instead of the default HTTPS URL.

```bash
# Correct way to clone using SSH
git clone git@github.com:YourUsername/NewRepoName.git

# Incorrect way (will use HTTPS and likely prompt for credentials)
# git clone https://github.com/YourUsername/NewRepoName.git
```

## Troubleshooting

- **Permission Denied (publickey):** If you get this error, double-check:
  - Your public key is correctly added to your GitHub account ([[_index]](references)).
  - Your private key exists in the `~/.ssh/` directory (e.g., `id_ed25519`).
  - Your SSH agent is running (if you used a passphrase) or the key permissions are correct.
  - You are using the correct SSH URL format.
- **Still asked for Password/Username:** Ensure the remote URL was changed correctly using `git remote -v`.

## Relationships / Links

- References: [[_index]] (references)

## Related Documentation

- (Link to official GitHub SSH documentation if desired)

---

_Part of [[_index|Git Documentation]]_
