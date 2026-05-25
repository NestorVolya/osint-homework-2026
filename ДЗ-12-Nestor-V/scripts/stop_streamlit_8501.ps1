$Connections = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue

foreach ($Connection in $Connections) {
    if ($Connection.OwningProcess -and $Connection.OwningProcess -ne 0) {
        Stop-Process -Id $Connection.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
