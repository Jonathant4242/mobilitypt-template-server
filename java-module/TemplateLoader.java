import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;

public class TemplateLoader {

    public static ArrayList<Template> loadTemplates(String filePath) {
        ArrayList<Template> templates = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            String line;
            String currentTitle = null;
            StringBuilder currentBody = new StringBuilder();

            while ((line = reader.readLine()) != null) {
                if (line.startsWith("{Button} = ")) {
                    // Save the previous template before starting a new one.
                    if (currentTitle != null) {
                        templates.add(new Template(currentTitle, currentBody.toString().trim()));
                        currentBody.setLength(0);
                    }

                    currentTitle = line.replace("{Button} = ", "").trim();
                } else if (line.trim().equals("---")) {
                    // Save the completed template block.
                    if (currentTitle != null) {
                        templates.add(new Template(currentTitle, currentBody.toString().trim()));
                        currentTitle = null;
                        currentBody.setLength(0);
                    }
                } else {
                    if (currentTitle != null) {
                        currentBody.append(line).append("\n");
                    }
                }
            }

            // Save the last template if the file does not end with ---
            if (currentTitle != null) {
                templates.add(new Template(currentTitle, currentBody.toString().trim()));
            }

        } catch (IOException e) {
            System.out.println("Error reading templates file: " + e.getMessage());
        }

        return templates;
    }
}
