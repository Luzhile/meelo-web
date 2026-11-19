param(
  [string]$Source,
  [string]$Output,
  [ValidateSet(512,1024)][int]$Size=1024,
  [int]$Samples=32,
  [switch]$AllowArchivedDiffuse,
  [string]$Blender='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
)
$ErrorActionPreference='Stop'
if(!$AllowArchivedDiffuse){throw 'Study Diffuse is archived. Use run-ao.ps1. The existing UV/material preparation and study-04 results are preserved.'}
$workspace=Split-Path $PSScriptRoot
if(!$Source){$Source=Join-Path $workspace 'meelo_unit_rooms_web-lighting.blend'}
if(!$Output){$Output=Join-Path $PSScriptRoot ('runs\study-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))}
if(Test-Path -LiteralPath $Output){throw 'Output already exists. Use a new output directory.'}
$project=Get-ChildItem -LiteralPath $workspace -Directory | Where-Object Name -Like 'MEELO_*' | Select-Object -First 1
$package=Get-ChildItem -LiteralPath $project.FullName -Directory | Where-Object Name -Like '*_1116' | Select-Object -First 1
$app=Join-Path $package.FullName 'app'
$baseline=@(Get-ChildItem -LiteralPath (Join-Path $app 'models') -File)+@(Get-Item -LiteralPath (Join-Path $app 'index.html'))
$hashes=$baseline | Get-FileHash | Select-Object Path,Hash | ConvertTo-Json
& $Blender --background --python-exit-code 1 --python (Join-Path $PSScriptRoot 'pipeline.py') -- --source $Source --out $Output --size $Size --samples $Samples --allow-archived-diffuse
if($LASTEXITCODE -ne 0){throw 'Preparation/bake/export failed. See Blender output; no batch bake is attempted.'}
$hashes | Set-Content -Encoding utf8 (Join-Path $Output 'reports\production-hashes-before.json')
& $Blender --background --python-exit-code 1 --python (Join-Path $PSScriptRoot 'check_prepared.py') -- $Output --candidates-only
if($LASTEXITCODE -ne 0){throw 'Native UV diagnostics failed'}
& $Blender --background --python-exit-code 1 --python (Join-Path $PSScriptRoot 'exact_overlap.py') -- $Output
if($LASTEXITCODE -ne 0){throw 'Exact UV overlap check failed'}
& $Blender --background --python-exit-code 1 --python (Join-Path $PSScriptRoot 'check_prepared.py') -- $Output
if($LASTEXITCODE -ne 0){throw 'Prepared asset verification failed'}
& (Join-Path $project.FullName 'runtime\node.exe') (Join-Path $PSScriptRoot 'verify.mjs') $Output
if($LASTEXITCODE -ne 0){throw 'Independent output verification failed'}
Write-Output ('Study-only run verified: '+$Output)
Write-Output 'No other room was baked. Production HTML/models were not replaced. Browser visual acceptance remains a separate gate.'
