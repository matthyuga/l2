from pathlib import Path
s=Path(__file__).resolve().parent
t=(s/'VerifyRoundRooms.java').read_text().replace('VerifyRoundRooms','VerifyRoundRoomsV2')
t=t.replace('controller=new PvpRoundRooms(config,clock::get,0,false);','''
   Field loading=Class.forName("org.l2jmobius.gameserver.scripting.engine.ScriptExecutor").getDeclaredField("_currentExecutingScript");loading.setAccessible(true);
   Object previous=loading.get(null);check(previous==null,"Another script is loading");
   try{loading.set(null,s.resolve("src/custom/ElvenPvpRoom/PvpRoundRooms.java"));controller=new PvpRoundRooms(config,clock::get,0,false);}finally{loading.set(null,previous);}
''')
t=t.replace('server-verification.txt','server-verification-v2.txt')
(s/'VerifyRoundRoomsV2.java').write_text(t)
(s/'verify-v2.mf').write_text('Manifest-Version: 1.0\nAgent-Class: VerifyRoundRoomsV2\n\n')
