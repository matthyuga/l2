// Static, focused Ghidra analysis. Does not execute or modify the source client.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.nio.file.*;
public class CameraNativeProbe extends GhidraScript {
    public void run() throws Exception {
        Path out = Path.of(getScriptArgs()[0]);
        Files.createDirectories(out);
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        try {
            for (String value : new String[]{"105a9600", "10592820"}) {
                Address address = toAddr(value);
                disassemble(address);
                Function function = getFunctionAt(address);
                if (function == null) function = createFunction(address, "camera_probe_" + value);
                if (function == null) throw new IllegalStateException("Cannot create function " + value);
                DecompileResults result = decomp.decompileFunction(function, 90, monitor);
                String text = result.decompileCompleted() ? result.getDecompiledFunction().getC() : "ERROR " + result.getErrorMessage();
                Files.writeString(out.resolve(value + ".c"), text);
                println("PROBE " + value + " completed=" + result.decompileCompleted());
            }
        } finally { decomp.dispose(); }
    }
}
