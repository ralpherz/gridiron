<#
Hits every endpoint and prints the status code. Two missing SQL constants
reached production because nothing checked all the endpoints at once.

    .\scripts\smoke.ps1
    .\scripts\smoke.ps1 -BaseUrl https://gridiron-api-70gh.onrender.com
#>
param([string]$BaseUrl = "http://localhost:8000")

$paths = @(
  "/health",
  "/teams",
  "/players?search=hurts",
  "/players/00-0036389",
  "/players/00-0036389/stats?season=2025",
  "/players/00-0036389/snaps?season=2025",
  "/players/00-0036389/injuries?season=2025",
  "/teams/PHI",
  "/teams/PHI/schedule",
  "/teams/PHI/roster",
  "/games/2025_01_DAL_PHI",
  "/leaders?season=2025&limit=3"
)

$failed = 0
foreach ($p in $paths) {
  $code = curl.exe -s -o NUL -w "%{http_code}" "$BaseUrl$p"
  $colour = if ($code -eq "200") { "Green" } else { "Red"; }
  if ($code -ne "200") { $failed++ }
  Write-Host "$code  $p" -ForegroundColor $colour
}

if ($failed -gt 0) {
  Write-Host "`n$failed endpoint(s) failed" -ForegroundColor Red
  exit 1
}
Write-Host "`nAll $($paths.Count) endpoints OK" -ForegroundColor Green
