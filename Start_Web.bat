@echo off
setlocal
pushd "%~dp0"
where node.exe >nul 2>nul
if errorlevel 1 (
  echo Install Node.js 20 or newer, then run this launcher again.
  pause
  popd
  exit /b 1
)
echo Open http://127.0.0.1:5173/ in your browser.
node tools/serve-static.cjs app 5173
popd
