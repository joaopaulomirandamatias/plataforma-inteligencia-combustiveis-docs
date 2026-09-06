#!/usr/bin/env bash
set -euo pipefail
: "${CI_COMMIT_SHA:?Missing event commit}"
tested_sha="$(git rev-parse HEAD)"
if [ "${CI_PIPELINE_EVENT:?}" = pull_request ]; then
  # The clone plugin tests the integration with the target branch, as Actions did.
  git merge-base --is-ancestor "$CI_COMMIT_SHA" HEAD
else
  test "$tested_sha" = "$CI_COMMIT_SHA"
fi
printf 'Event SHA: %s\nTested SHA: %s\n' "$CI_COMMIT_SHA" "$tested_sha"
