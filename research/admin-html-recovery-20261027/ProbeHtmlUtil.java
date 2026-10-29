public class ProbeHtmlUtil {
    public static void main(String[] args) throws Exception {
        Class<?> helper = Class.forName("org.l2jmobius.gameserver.util.HtmlUtil", false, ClassLoader.getSystemClassLoader());
        boolean found = java.util.Arrays.stream(helper.getDeclaredMethods()).anyMatch(m -> m.getName().equals("buildHtmlActionCache"));
        if (!found) throw new IllegalStateException("buildHtmlActionCache missing");
        System.out.println("PASS: HtmlUtil loads from current GameServer.jar and buildHtmlActionCache resolves.");
        System.out.println(helper.getProtectionDomain().getCodeSource().getLocation());
    }
}
