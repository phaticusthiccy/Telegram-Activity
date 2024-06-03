@echo off
for /f "usebackq tokens=* delims=" %%i in (".env") do (
    echo %%i | findstr /b /c:"#">nul && (
        goto :continue
    )
        echo %%i | findstr /r "^$">nul && (
        goto :continue
    )
        set %%i

    :continue
)

echo.
echo "Environment variables loaded"
set
pause
