# Setting up a reviewing GitHub App

One app per person or organisation; each repository it reviews declares it in the Reviewing identity block of `docs/agents/issue-tracker.md`, and each machine that publishes holds the app's private key.

## 1. Create the app

GitHub Settings, Developer settings, GitHub Apps, New GitHub App. Pick a name: its lowercased, hyphenated form is the app's **slug**, and the app's login is `<slug>[bot]`. The homepage URL can be the repository.

**Webhook**: untick "Active", or the form demands a webhook URL.

**Permissions**, under Repository permissions:

- **Pull requests: Read and write.** Covers the review POST, its inline comments, dismissals, and GraphQL `resolveReviewThread`.
- **Issues: Read and write.** Covers the general-comment fallback in `review-code-publish`'s `publication.md` (`role=summary`, the issues-comments endpoint). Leave it at No access only if you accept that this fallback is unavailable to the app.
- **Metadata: Read** is granted automatically.
- **Contents** is not needed.

**Where can this GitHub App be installed?** Choose "Any account" when the app's owner is not the owner of every repository it will review; "Only on this account" cannot be installed elsewhere. Installing on an organisation may need an organisation owner's approval.

## 2. Note the Client ID

On the app's General page. It is the JWT issuer the script expects: `--client-id <Client ID>`. The App ID also works as a JWT issuer on GitHub's side, but the script accepts the client id only; the installation id is neither.

## 3. Install the app

Install App, pick the account, then "Only select repositories" and add **every** repository it will review. The token is minted for one repository and `GET /repos/{owner}/{repo}/installation` returns 404 for any the installation does not cover, which is the "app not installed on `<owner>/<repo>`" reason. Add a repository here later when a new one starts declaring the app.

## 4. Generate and place the key

General page, Private keys, Generate a private key. GitHub keeps no copy: the download is the only one, and a lost key means generating a new one. Place it and lock it down:

```sh
mkdir -p ~/.config/reviewbot && chmod 700 ~/.config/reviewbot
mv ~/Downloads/<app>.<date>.private-key.pem ~/.config/reviewbot/<Client ID>.pem
chmod 600 ~/.config/reviewbot/<Client ID>.pem
```

The script also accepts `~/.config/reviewbot/key.pem` when there is one app on the machine, and `--key` or `REVIEWBOT_KEY` for any other location. Never place the key in a repository or under the synced skills directory: anyone holding it can post as the app. On any exposure, generate a new key on the app's settings page and delete the old one there.

## 5. Check it

```sh
python3 scripts/review_token.py whoami --client-id <Client ID> <owner>/<repo>
```

prints the app name and slug, `rest login: <slug>[bot]`, `graphql login`, the installation id and its permissions, and the review-token command a publisher runs. The tracker doc needs only the app name and client id; `whoami` reports the login.

The `rest login` line always carries the `[bot]` suffix, which REST records carry and GraphQL `author{login}` omits. The `graphql login` line shows what the `viewer` query returned for the minted token, which on GitHub.com has been seen to carry the suffix as well, so the two lines may read the same. Consumers compare logins with a trailing `[bot]` ignored on both sides, and the Resolve entry point reports the bare slug from the `app:` line.

## 6. Declare it in the repository

Paste into `docs/agents/issue-tracker.md`:

```text
## Reviewing identity

- **Reviewing app**: <app name>
- **Client id**: <Client ID>
```

## GitHub Enterprise

Pass `--api https://<host>/api/v3` (or set `REVIEWBOT_API`); the GraphQL endpoint `https://<host>/api/graphql` is derived from it. On a python.org macOS build without root certificates, run `Install Certificates.command` from the Python application folder or point `SSL_CERT_FILE` at a CA bundle; the script names both on a TLS verification failure.
