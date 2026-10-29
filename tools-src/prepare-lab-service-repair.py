from pathlib import Path
import shutil

root=Path('E:/l2-local')
src=root/'source/L2J_Mobius_CT_0_Interlude'
backup=root/'backups/lab-service-repair-2026-10-12'
def edit(path,old,new):
    text=path.read_text(encoding='utf-8')
    assert text.count(old)==1,(path,old[:80],text.count(old))
    save=backup/path.relative_to(root)
    save.parent.mkdir(parents=True,exist_ok=True)
    if not save.exists():shutil.copy2(path,save)
    path.write_text(text.replace(old,new),encoding='utf-8',newline='\n')

seven=src/'java/org/l2jmobius/gameserver/mechanics/sevensigns/SevenSigns.java'
edit(seven,'''protected SevenSigns()
	{
		// Classic autonomous''','''protected SevenSigns()
	{
		// Dialogs and other native callers remain available with the event disabled.
		for (int seal : new int[] {SEAL_AVARICE, SEAL_GNOSIS, SEAL_STRIFE})
		{
			_signsSealOwners.put(seal, CABAL_NULL);
			_signsDuskSealTotals.put(seal, 0);
			_signsDawnSealTotals.put(seal, 0);
		}
		// Classic autonomous''')
for field,default in [('_signsSealOwners','CABAL_NULL'),('_signsDuskSealTotals','0'),('_signsDawnSealTotals','0')]:
    edit(seven,f'return {field}.get(seal);',f'return {field}.getOrDefault(seal, {default});')

for base in [src/'dist/game/data/scripts',root/'server/game/data/scripts']:
    master=base/'handlers/MasterHandler.java'
    edit(master,'import handlers.chat.commands.admin.AdminBuildLab;', 'import handlers.chat.commands.admin.AdminBuildLab;\nimport handlers.chat.commands.admin.AdminLabActions;')
    edit(master,'\t\t\tAdminBuildLab.class,','\t\t\tAdminBuildLab.class,\n\t\t\tAdminLabActions.class,')
    threat=base/'handlers/chat/commands/voiced/ThreatCommand.java'
    edit(threat,'".amenaza".equalsIgnoreCase(line.getCmd().trim())','(".amenaza".equalsIgnoreCase(line.getCmd().trim()) || "//amenaza".equalsIgnoreCase(line.getCmd().trim()))')
    edit(threat,'new MacroCmd(0, MacroType.TEXT, 0, 0, ".amenaza")','new MacroCmd(0, MacroType.TEXT, 0, 0, player.isGM() ? "//amenaza" : ".amenaza")')

for path in [root/'server/game/config/AdminCommands.xml',src/'dist/game/config/AdminCommands.xml']:
    edit(path,'</list>','''    <!-- Native aliases for laboratory macros; keep existing GM checks. -->
    <admin command="amenaza" description="Select last direct aggressor without ordinary chat." accessLevel="100" />
    <admin command="ia" description="Manual laboratory combat pilots." accessLevel="100" />
</list>''')

runtime=root/'server/game/data/scripts/handlers/chat/commands/admin/AdminLabActions.java'
shutil.copy2(src/'dist/game/data/scripts/handlers/chat/commands/admin/AdminLabActions.java',runtime)
print('Prepared neutral Seven Signs state and native GM macro aliases.')
