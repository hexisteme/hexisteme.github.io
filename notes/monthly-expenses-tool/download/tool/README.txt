monthly-expenses evaluation candidate
Requires Python 3.11+ and a filesystem supporting hard links.
Input: UTF-8/BOM CSV, headers 일자,항목,금액 in that order. ISO dates; signed plain decimals, max 12 integer digits and 2 decimals.
Output: UTF-8 BOM CSV, headers 월,항목,건수,합계, sorted by month/category.
python3 monthly-expenses.pyz --input expenses.csv --output monthly.csv
Exit 0: output created; 2: rejected input/output. Existing output is never replaced.
No network calls or telemetry in the converter. Download/browser/OS/cloud sync behavior is outside that claim.
Synthetic contract, no official NEIS/ERP support. Test sample first; keep source backup.
Annual organizational usage/support terms are proposed, not an active purchase. See https://hexisteme.github.io/notes/monthly-expenses-tool/licenses/annual.html.
