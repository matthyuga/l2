"""Academy-only adaptation; never writes to Lab sources."""
from pathlib import Path

def patch(root):
    root = Path(root).resolve()
    assert root == Path('E:/l2-academy').resolve()
    folder = root / 'server/game/data/scripts/custom'
    telemetry = folder / 'LabTelemetry/LabTelemetry.java'
    text = telemetry.read_text(encoding='utf8')
    start = '\t\tThreadPool.schedule(this::runCleanClassCoverage, 10000);'
    end = '\t\tThreadPool.schedule(this::capturePhysicalRaceDiagnostics, 20000);'
    if 'ACADEMY_TELEMETRY_PASSIVE' not in text:
        a, b = text.index(start), text.index(end) + len(end)
        text = text[:a] + '\t\tLOGGER.info("ACADEMY_TELEMETRY_PASSIVE: automatic Lab benchmarks disabled; duel telemetry available.");' + text[b:]
        telemetry.write_text(text, encoding='utf8')
    roster = folder / 'NormalNpcRoster/NormalNpcRoster.java'
    text = roster.read_text(encoding='utf8')
    text = text.replace('if(!player.isGM()){player.sendMessage("Roster: acceso de laboratorio GM.");return true;}',
                        '// Academy is a local one-player profile: roster preparation is available to its player.')
    if 'prepareForAcademyVerification' not in text:
        marker = '    private NormalNpcRoster() {'
        text = text.replace(marker, '''    private static NormalNpcRoster academyInstance;
    public static void prepareForAcademyVerification() {
        RealHumanPilots.prepareOnDemand();
        academyInstance.prepareAndApply();
        if (!READY) throw new IllegalStateException("Academy roster incomplete");
        LOGGER.info("ACADEMY_ROSTER_TEST PASS: complete independent roster prepared.");
    }
''' + marker + '\n        academyInstance = this;')
        text = text.replace('        academyInstance = this;', '''        academyInstance = this;
        if (Boolean.getBoolean("academy.verify")) ThreadPool.schedule(() -> {
            try { prepareForAcademyVerification(); }
            catch (Exception e) { LOGGER.log(Level.SEVERE,"ACADEMY_ROSTER_TEST FAIL",e); }
        }, 25000);''')
    roster.write_text(text, encoding='utf8')

if __name__ == '__main__':
    patch('E:/l2-academy')
