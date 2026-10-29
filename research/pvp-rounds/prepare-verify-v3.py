from pathlib import Path
s=Path(__file__).resolve().parent
t=(s/'VerifyRoundRoomsV2.java').read_text().replace('VerifyRoundRoomsV2','VerifyRoundRoomsV3').replace('server-verification-v2.txt','server-verification-v3.txt')
t=t.replace('a.getAppearance().getVisibleTitle().equals(a.getTitle())','Objects.equals(a.getAppearance().getVisibleTitle(),a.getTitle())')
(s/'VerifyRoundRoomsV3.java').write_text(t)
(s/'verify-v3.mf').write_text('Manifest-Version: 1.0\nAgent-Class: VerifyRoundRoomsV3\n\n')
