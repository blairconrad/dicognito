if ($Args.Count -eq 0) {
    $commands = 'clean', 'test', 'pack'
}
else {
    $commands = $Args
}

$env:PYTHONPATH = "${env:PYTHONPATH};$PWD"

$env:PYTHONPATH = "${env:PYTHONPATH};$PWD"

$actions = @{
    'clean'        = { 'build', 'dicognito.egg-info', 'dist' | Where-Object { Test-Path $_ } | Remove-Item -Force -Recurse  }
    'testpackage'  = { .\tools\test.ps1 }
    'testlocal'    = { Push-Location src; python -m pytest ..\tests; Pop-Location }
    'testforever'  = { Set-Location src; python -m pytest --looponfail ..\tests }
    'smoketest'    = { python smoketest\smoketest.py; code --diff smoketest\original.txt smoketest\anonymized.txt }
    'pack'         = { python setup.py sdist bdist_wheel }
    'publish'      = { python -m twine upload dist/* }
    'test-publish' = { python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* }
    'help'         = { Write-Output "Usage: `r`n  build command [command...]`r`n`r`nwhere commands are:`r`n  $(($actions.Keys | Sort-Object) -join "`r`n  ")`r`n" }
}

$commands | ForEach-Object {
    $command = $_
    $action = $actions[$command]
    if ($action) {
        Write-Output "$command starting..."
        & $action
        [int]$code = $LASTEXITCODE
        if ($code -ne 0) {
            throw "Command $command exited with code $code"
        }
        Write-Output "$command succeeded."
    }
    else {
        throw "Unknown command $command"
    }
}