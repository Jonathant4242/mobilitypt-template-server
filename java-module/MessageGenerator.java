

public class MessageGenerator {

    // Generates a simple text message using the request information
    public static String generateMessage(RequestItem request) {

        String message = "Hello " + request.getFirstName() + ",\n\n" +
                "This is Mobility Physical Therapy. We are checking availability for an appointment.\n\n" +
                "Preferred Day: " + request.getPreferredDay() + "\n" +
                "Preferred Date: " + request.getPreferredDate() + "\n" +
                "Available Time Window: " + request.getEarliestTime() + " - " + request.getLatestTime() + "\n\n" +
                "Please let us know if this time works for you or call us at (714) 389-9306.\n\n" +
                "Thank you,\nMobility Physical Therapy";

        return message;
    }
}