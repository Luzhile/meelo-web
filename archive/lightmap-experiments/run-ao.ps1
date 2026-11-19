param(
  [string]$Prepared,
  [string]$Output,
  [int]$Samples=256,
  [double]$Distance=.25,
  [ValidateRange(8,16)][int]$Margin=8,
  [string]$Blender='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
)
$ErrorActionPreference='Stop'
$workspace=Split-Path $PSScriptRoot
if(!$Prepared){$Prepared=Join-Path $PSScriptRoot 'runs\study-04\blends\prepared-eight-rooms.blend'}
if(!$Output){$Output=Join-Path $PSScriptRoot ('runs\meal-ao-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))}
if(Test-Path -LiteralPath $Output){throw 'Output already exists. Use a new AO experiment directory.'}
$project=Get-ChildItem -LiteralPath $workspace -Directory | Where-Object Name -Like 'MEELO_*' | Select-Object -First 1
$package=Get-ChildItem -LiteralPath $project.FullName -Directory | Where-Object Name -Like '*_1116' | Select-Object -First 1
$app=Join-Path $package.FullName 'app'
$files=@(Get-ChildItem -LiteralPath (Join-Path $app 'models') -File)+@(Get-Item -LiteralPath (Join-Path $app 'index.html'))
$files+=@(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'runs\study-04') -Recurse -File)
$files+=@(Get-Item -LiteralPath (Join-Path $workspace 'meelo_unit_rooms_web-lighting.blend'))
$baseline=$files | Get-FileHash | Select-Object Path,Hash | ConvertTo-Json
& $Blender --background --python-exit-code 1 --python (Join-Path $PSScriptRoot 'meal_ao.py') -- --prepared $Prepared --out $Output --samples $Samples --distance $Distance --margin $Margin
if($LASTEXITCODE -ne 0){throw 'AO preparation/bake/export failed. No Diffuse fallback will be attempted.'}
$baseline | Set-Content -Encoding utf8 (Join-Path $Output 'reports\protected-inputs.json')
& $Blender --background --python-exit-code 1 --python (Join-Path $PSScriptRoot 'verify_ao_asset.py') -- $Output
if($LASTEXITCODE -ne 0){throw 'Saved AO working asset failed verification'}
& (Join-Path $project.FullName 'runtime\node.exe') (Join-Path $PSScriptRoot 'verify_ao.mjs') $Output
if($LASTEXITCODE -ne 0){throw 'Independent AO checks failed'}
Write-Output ('Meal AO experiment: '+$Output)
Write-Output 'Existing UVs reused; no Study Diffuse, GI or color bake executed. Strict browser A/B remains a separate visual gate.'
