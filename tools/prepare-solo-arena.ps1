$ErrorActionPreference = 'Stop'

$root = Split-Path $PSScriptRoot -Parent
$clientRoot = Join-Path (Split-Path $root -Parent) 'l2\system-clean'
$db = Join-Path $root 'tools\mariadb-11.8.9-winx64\bin\mariadb.exe'
$dump = Join-Path $root 'tools\mariadb-11.8.9-winx64\bin\mariadb-dump.exe'
$backupDir = Join-Path $root 'backups\Hellkevin-before-solo-arena'
$charName = 'Hellkevin'
$database = 'l2jmobiusinterlude'

function Invoke-Database([string]$Sql, [switch]$Raw) {
    $args = @('--protocol=TCP','-h','127.0.0.1','-P','3307','-u','l2j','-pl2local','-D',$database,'--batch','--skip-column-names','--execute',$Sql)
    $result = & $db @args
    if ($LASTEXITCODE -ne 0) { throw "Fallo MariaDB al ejecutar: $Sql" }
    if ($Raw) { return $result }
}

if (-not (Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue)) {
    throw 'MariaDB no esta iniciado.'
}

# Stop the client and Game Server so the character cannot be saved over our changes.
Get-Process -Name 'L2','L2-solo' -ErrorAction SilentlyContinue | Stop-Process -Force
$gamePidFile = Join-Path $root 'run\game.pid'
if (Test-Path -LiteralPath $gamePidFile) {
    $gamePid = [int](Get-Content -LiteralPath $gamePidFile -Raw)
    Stop-Process -Id $gamePid -Force -ErrorAction SilentlyContinue
}
for ($i = 0; $i -lt 30; $i++) {
    if (-not (Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 7777 -State Listen -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Milliseconds 500
}

$charId = Invoke-Database "SELECT charId FROM characters WHERE char_name='$charName' LIMIT 1;" -Raw
if (-not $charId) { throw "No se encontro el personaje $charName." }
$charId = [long]($charId | Select-Object -First 1)

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
$dumps = @(
    @{ Table='characters'; Where="charId=$charId"; File='characters.sql' },
    @{ Table='character_skills'; Where="charId=$charId"; File='character_skills.sql' },
    @{ Table='items'; Where="owner_id=$charId"; File='items.sql' }
)
foreach ($entry in $dumps) {
    $target = Join-Path $backupDir $entry.File
    if (-not (Test-Path -LiteralPath $target)) {
        & $dump --protocol=TCP -h 127.0.0.1 -P 3307 -u l2j -pl2local --no-create-info --skip-triggers "--where=$($entry.Where)" "--result-file=$target" $database $entry.Table
        if ($LASTEXITCODE -ne 0) { throw "No se pudo respaldar $($entry.Table)." }
    }
}

# Human Fighter -> Warrior -> Gladiator -> Duelist. Keep the maximum learned
# level for every skill in the complete class lineage.
$skillTrees = @(
    'StartingClass\HumanFighter.xml',
    '1stClass\Warrior.xml',
    '2ndClass\Gladiator.xml',
    '3rdClass\Duelist.xml'
)
$skillRoot = Join-Path $root 'server\game\data\stats\players\skillTrees'
$skills = @{}
foreach ($relativePath in $skillTrees) {
    [xml]$tree = Get-Content -LiteralPath (Join-Path $skillRoot $relativePath) -Raw
    foreach ($skill in $tree.list.skillTree.skill) {
        if ([int]$skill.getLevel -le 80) {
            $id = [int]$skill.skillId
            $level = [int]$skill.skillLevel
            if ((-not $skills.ContainsKey($id)) -or ($level -gt $skills[$id])) {
                $skills[$id] = $level
            }
        }
    }
}

Invoke-Database "UPDATE characters SET level=80, exp=4200000000, sp=2000000000, accesslevel=100, classid=88, base_class=88, title='Arena Lab', x=149500, y=46700, z=-3400, heading=32768, curHp=99999, curMp=99999, curCp=99999, online=0 WHERE charId=$charId;"

$skillValues = $skills.GetEnumerator() | Sort-Object Name | ForEach-Object { "($charId,$($_.Key),$($_.Value),0)" }
$skillSql = 'INSERT INTO character_skills (charId,skill_id,skill_level,class_index) VALUES ' + ($skillValues -join ',') + ' ON DUPLICATE KEY UPDATE skill_level=GREATEST(skill_level,VALUES(skill_level));'
Invoke-Database $skillSql

# S-grade Duelist kit, placed in the inventory for manual equipping.
$kit = @(
    @{ Id=6580; Count=1; Enchant=10 }, # Tallum Blade*Dark Legion's Edge
    @{ Id=6373; Count=1; Enchant=10 }, # Imperial Crusader Breastplate
    @{ Id=6374; Count=1; Enchant=10 }, # Imperial Crusader Gaiters
    @{ Id=6375; Count=1; Enchant=10 }, # Imperial Crusader Gauntlets
    @{ Id=6376; Count=1; Enchant=10 }, # Imperial Crusader Boots
    @{ Id=6377; Count=1; Enchant=10 }, # Imperial Crusader Shield
    @{ Id=6378; Count=1; Enchant=10 }, # Imperial Crusader Helmet
    @{ Id=6656; Count=1; Enchant=10 }, # Earring of Antharas
    @{ Id=858; Count=1; Enchant=10 },  # Tateossian Earring
    @{ Id=6657; Count=1; Enchant=10 }, # Necklace of Valakas
    @{ Id=6658; Count=1; Enchant=10 }, # Ring of Baium
    @{ Id=889; Count=1; Enchant=10 }   # Tateossian Ring
)
$nextObjectId = [long](Invoke-Database 'SELECT COALESCE(MAX(object_id),0) FROM items;' -Raw | Select-Object -First 1) + 1
foreach ($item in $kit) {
    $exists = [int](Invoke-Database "SELECT COUNT(*) FROM items WHERE owner_id=$charId AND item_id=$($item.Id);" -Raw | Select-Object -First 1)
    if ($exists -eq 0) {
        Invoke-Database "INSERT INTO items (owner_id,object_id,item_id,count,enchant_level,loc,loc_data,time_of_use,custom_type1,custom_type2,mana_left,time) VALUES ($charId,$nextObjectId,$($item.Id),$($item.Count),$($item.Enchant),'INVENTORY',0,NULL,0,0,-1,-1);"
        $nextObjectId++
    }
}

foreach ($stack in @(@{Id=57; Count=100000000}, @{Id=1467; Count=5000})) {
    $objectId = Invoke-Database "SELECT object_id FROM items WHERE owner_id=$charId AND item_id=$($stack.Id) LIMIT 1;" -Raw
    if ($objectId) {
        Invoke-Database "UPDATE items SET count=GREATEST(count,$($stack.Count)) WHERE object_id=$($objectId | Select-Object -First 1);"
    } else {
        Invoke-Database "INSERT INTO items (owner_id,object_id,item_id,count,enchant_level,loc,loc_data,time_of_use,custom_type1,custom_type2,mana_left,time) VALUES ($charId,$nextObjectId,$($stack.Id),$($stack.Count),0,'INVENTORY',0,NULL,0,0,-1,-1);"
        $nextObjectId++
    }
}

& (Join-Path $root 'Start-L2Local.ps1')
$game = Start-Process -FilePath (Join-Path $clientRoot 'L2.exe') -ArgumentList 'L2Protocol' -WorkingDirectory $clientRoot -PassThru

[pscustomobject]@{
    Character = $charName
    CharacterId = $charId
    Class = 'Duelist'
    Level = 80
    SkillsGranted = $skills.Count
    OpponentNpcId = 900200
    PlayerArenaLocation = '149500 46700 -3400'
    OpponentLocation = '149500 46100 -3400'
    ClientProcessId = $game.Id
    Completed = (Get-Date).ToString('o')
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root 'solo-arena-status.json') -Encoding UTF8
