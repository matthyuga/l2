from pathlib import Path
import shutil

root=Path('E:/l2-local')
backup=root/'backups/lab-service-repair-2026-10-12'
launcher=root/'Start-L2Local.ps1'
text=launcher.read_text(encoding='utf-8-sig')
old="    Write-Host 'Iniciando GameServer. Cargando mundo y scripts...'"
new="""    # Apply staged core fixes only when no GameServer process is using the JAR.
    $corePatchRoot = Join-Path $Root 'server\\pending-core-patches'
    if (Test-Path -LiteralPath $corePatchRoot) {
        foreach ($corePatch in Get-ChildItem -LiteralPath $corePatchRoot -Directory | Sort-Object Name) {
            $corePatchApplied = Join-Path $corePatch.FullName '.applied'
            if ((Test-Path -LiteralPath (Join-Path $corePatch.FullName 'org')) -and -not (Test-Path -LiteralPath $corePatchApplied)) {
                Write-Host ('Aplicando correccion pendiente: ' + $corePatch.Name)
                & (Join-Path $Root 'tools\\jdk-25.0.4.1+1\\bin\\jar.exe') --update --file (Join-Path $Root 'server\\libs\\GameServer.jar') -C $corePatch.FullName org
                if ($LASTEXITCODE -ne 0) { throw ('No se pudo aplicar la correccion: ' + $corePatch.Name) }
                Set-Content -LiteralPath $corePatchApplied -Value 'Applied before GameServer startup.' -Encoding Ascii
            }
        }
    }
    Write-Host 'Iniciando GameServer. Cargando mundo y scripts...'"""
assert text.count(old)==1
backup.mkdir(parents=True,exist_ok=True)
saved=backup/'Start-L2Local.ps1'
if not saved.exists():shutil.copy2(launcher,saved)
launcher.write_text(text.replace(old,new),encoding='utf-8-sig',newline='\r\n')

relative=Path('org/l2jmobius/gameserver/mechanics/sevensigns/SevenSigns.class')
pending=root/'server/pending-core-patches/20261012-lab-service-repair'/relative
pending.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(root/'build/lab-service-repair'/relative,pending)

src=root/'source/L2J_Mobius_CT_0_Interlude'
overlay=root/'cloud-repo/mobius-overlay/L2J_Mobius_CT_0_Interlude'
for f in [
 'java/org/l2jmobius/gameserver/mechanics/sevensigns/SevenSigns.java',
 'dist/game/config/AdminCommands.xml',
 'dist/game/data/scripts/handlers/MasterHandler.java',
 'dist/game/data/scripts/handlers/chat/commands/admin/AdminLabActions.java',
 'dist/game/data/scripts/handlers/chat/commands/voiced/ThreatCommand.java']:
    dest=overlay/f
    saved=backup/dest.relative_to(root)
    if dest.exists() and not saved.exists():
        saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(dest,saved)
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src/f,dest)
shutil.copy2(launcher,root/'cloud-repo/ops/windows/Start-L2Local.ps1')
print('Sources mirrored; SevenSigns core patch staged for next normal startup.')
