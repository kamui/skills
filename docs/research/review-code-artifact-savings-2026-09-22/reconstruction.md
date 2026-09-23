# Offline reconstruction proof, 2026-09-23

Only archive/ and docs/research/tools/savings_archive.py were copied into a new temporary directory, with a placeholder skill root. The script below ran there under `GIT_CEILING_DIRECTORIES=<tmp> unshare -rn sh proof.sh`: a user and network namespace whose only interface, loopback, is down, and no parent repository. The temporary path is shown as <tmp>.

```sh
set -u
echo "## network namespace"; ip -brief link 2>/dev/null
echo "## python / git"; python3 --version; git --version
echo "## verify"; python3 savings_archive.py verify archive; echo "exit $?"
echo "## fixture rebuild"; python3 savings_archive.py fixture archive --out rebuilt; echo "exit $?"
echo "## materialize"; python3 savings_archive.py materialize archive --root "$PWD/root" --skill-root "$PWD/skill"; echo "exit $?"
echo "## check"; python3 savings_archive.py check archive --root "$PWD/root"; echo "exit $?"
echo "## altered: one byte of the seeded record"; sed -i 's/"P1"/"P2"/' archive/tasks/continuation/review/record.json
python3 savings_archive.py verify archive; echo "exit $?"
echo "## missing: the continuation spec"; rm archive/tasks/continuation/inputs/spec.md
python3 savings_archive.py verify archive; echo "exit $?"
echo "## materialize refuses the altered archive"; python3 savings_archive.py materialize archive --root "$PWD/root2" --skill-root "$PWD/skill" > /dev/null; echo "exit $?"
```

```text
## network namespace
lo               DOWN           00:00:00:00:00:00 <LOOPBACK>
## python / git
Python 3.14.7
git version 2.34.1
## verify
archive verified: 59 files, manifest sha256 f7880b94071417ed440219ae8b8a21836d03760ed6cbd209848a156d9e5a9ca9
exit 0
## fixture rebuild
M0 2301c83ee0b2ba0248fe3d2d1f6cd481963545ab
A1 0eb283dfe715341548387bf65af857affedf5dfa
B1 e16a48c5856397ad320ae1092d821bcb87614801
B2 2ba40465ef91f15b2963a4b12e80f46ee0e9efae
C1 a13922e76f42d9757608530348200affbf3bde2f
D1 864eea86ab86bf5a3375898bc606933ea20696cc
D2 03ce7cd85d34afda4ae47f06d7958ea906b3fcc1
D3 b96a362e99ce4f5b6b1fe26ad02fda66e8343723
exit 0
## materialize
<tmp>/root/publishable
<tmp>/root/implementation-gate
<tmp>/root/required-verification
<tmp>/root/continuation
exit 0
## check
realization at <tmp>/root matches the archive
exit 0
## altered: one byte of the seeded record
tasks/continuation/review/record.json: altered (manifest sha256 584e6ce55abf6de0a3c35a68f7a44b1d049d948d1ffd895f3397cceaab37a18b)
exit 1
## missing: the continuation spec
tasks/continuation/inputs/spec.md: missing
tasks/continuation/review/record.json: altered (manifest sha256 584e6ce55abf6de0a3c35a68f7a44b1d049d948d1ffd895f3397cceaab37a18b)
exit 1
## materialize refuses the altered archive
exit 1
```
