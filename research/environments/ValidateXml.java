import java.io.File;
import javax.xml.XMLConstants;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.SchemaFactory;

public class ValidateXml
{
    public static void main(String[] args) throws Exception
    {
        SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI)
            .newSchema(new File(args[1])).newValidator().validate(new StreamSource(new File(args[0])));
        System.out.println("XSD PASS: " + args[0]);
    }
}
