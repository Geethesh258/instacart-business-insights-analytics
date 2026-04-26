@echo off
setlocal

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Running Instacart analytics pipeline...
%PYTHON_EXE% run_project.py %*

if errorlevel 1 (
    echo.
    echo Project execution failed. Check database settings and dependencies.
    exit /b 1
)

echo.
echo Project execution completed.
endlocal
