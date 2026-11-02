#!/usr/bin/env bash
set -euo pipefail
# Run on cloud/Linux only. Do not patch the upstream remote repository.
UPSTREAM="https://github.com/MCG-NJU/AutoTavern.git"
COMMIT="fb61201a557ddd36a411cf44aac51ce4d9b606ce"
PATCH="https://rizling.top/downloads/autotavern-observe2.patch"
SHA256="1e48a071cad63c284debbf917cb012595a405a4ef5ab66180eb2918e205aaac0"
mkdir -p vendor
if [[ ! -d vendor/AutoTavern/.git ]]; then git clone "$UPSTREAM" vendor/AutoTavern; fi
git -C vendor/AutoTavern fetch origin "$COMMIT"
git -C vendor/AutoTavern checkout --detach "$COMMIT"
curl --fail --location --silent --show-error "$PATCH" -o vendor/observe2.patch
printf '%s  %s\n' "$SHA256" vendor/observe2.patch | sha256sum -c -
git -C vendor/AutoTavern apply --check ../observe2.patch
git -C vendor/AutoTavern apply ../observe2.patch
python -m pip install vendor/AutoTavern
python -m tavern_ai.contract
