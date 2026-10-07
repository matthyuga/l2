$ports = [ordered]@{
    'MariaDB' = 3307
    'Login Server' = 2106
    'Login/Game link' = 19014
    'Game Server' = 7777
}

foreach ($entry in $ports.GetEnumerator()) {
    $connection = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort $entry.Value -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) {
        Write-Host ('{0,-18} LISTO  127.0.0.1:{1}  PID {2}' -f $entry.Key, $entry.Value, $connection.OwningProcess) -ForegroundColor Green
    } else {
        Write-Host ('{0,-18} DETENIDO  127.0.0.1:{1}' -f $entry.Key, $entry.Value) -ForegroundColor Yellow
    }
}
