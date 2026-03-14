import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.io.PrintWriter;

public class RequestStore {

    // Path to the shared request file written by Django
    private static final String FILE_PATH = "../requests.txt";

    public static ArrayList<RequestItem> loadRequests() {

        ArrayList<RequestItem> requests = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(FILE_PATH))) {

            String line;

            while ((line = reader.readLine()) != null) {

                if (line.trim().isEmpty()) {
                    continue;
                }

                String[] parts = line.split("\\|");

                if (parts.length == 8) {

                    RequestItem request = new RequestItem(
                            parts[0], // first name
                            parts[1], // phone
                            parts[2], // event name
                            parts[3], // details
                            parts[4], // preferred day
                            parts[5], // preferred date
                            parts[6], // earliest time
                            parts[7] // latest time
                    );

                    requests.add(request);
                }
            }

        } catch (IOException e) {
            System.out.println("Error loading requests: " + e.getMessage());
        }

        return requests;
    }

    public static void saveRequests(ArrayList<RequestItem> requests) {

        try (PrintWriter writer = new PrintWriter(FILE_PATH)) {

            for (RequestItem r : requests) {

                String line = String.join("|",
                        r.getFirstName(),
                        r.getPhoneNumber(),
                        r.getEventName(),
                        r.getDetails(),
                        r.getPreferredDay(),
                        r.getPreferredDate(),
                        r.getEarliestTime(),
                        r.getLatestTime());

                writer.println(line);
            }

        } catch (Exception e) {
            System.out.println("Error saving requests: " + e.getMessage());
        }
    }
}