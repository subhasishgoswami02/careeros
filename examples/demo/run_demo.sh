#!/usr/bin/env bash
# See the kit's scripts working in one minute, on a fictional user (Meera, a payments PM).
# Uses a temporary folder: nothing is written to my-data/ or to this repo.
#   bash examples/demo/run_demo.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cp examples/demo/*.yaml "$WORK/"
export CAREEROS_DATA="$WORK"
T="$PY scripts/tracker.py"

echo "=================  1. SCORE five roles  ================="
for f in examples/demo/ratings/*.json; do
  $PY scripts/score.py "$f" --save | sed '/saved:/d'
  echo
done

echo "=================  2. TRACK applications and warm asks  ================="
$T --today 2026-10-05 add --company "Fieldstone Bank" --role "Senior PM, Cards" --route company_portal --score 76 --p 0.15 --prediction "cold portal, good domain"
$T --today 2026-10-08 add --company "Copperleaf" --role "Lead PM, Merchant Risk" --route named_human_plus_portal --score 81 --contact "Arjun K, Group PM" --p 0.35 --prediction "named HM, strong match"
$T --today 2026-10-12 add --company "Tidewater Commerce" --role "Senior PM, Checkout" --route referral --score 84 --contact "Sana P, ex-colleague" --p 0.6 --prediction "referral + exact checkout match"
$T --today 2026-10-19 add --company "Quillpay" --role "Senior PM, Payouts" --route company_portal --score 77 --p 0.1 --prediction "portal only, no person yet"
$T --today 2026-10-12 ask --company "Tidewater Commerce" --person "Sana P" --type referral --app 3
$T --today 2026-10-15 update 3 --status screen --round "recruiter screen" --note "call booked; asked their range"
$T --today 2026-10-24 ask --company "Northwind Pay" --person "Ravi S" --type referral
echo
echo "=================  3. FOLLOW-UPS due on 2026-10-26  ================="
$T --today 2026-10-26 due
echo
echo "=================  4. PIPELINE  ================="
$T --today 2026-10-26 list --all
echo
echo "=================  5. FUNNEL  ================="
$T --today 2026-10-26 stats
