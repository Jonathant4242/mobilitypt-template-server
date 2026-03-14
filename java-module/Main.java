import java.util.ArrayList;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {

        // Path to the templates file in the repo root
        String templateFile = "../templates.txt";

        // Load templates using the TemplateLoader
        ArrayList<Template> templates = TemplateLoader.loadTemplates(templateFile);

        System.out.println("Loaded Templates:");
        System.out.println("-----------------");

        for (Template t : templates) {
            System.out.println("- " + t.getTitle());
        }

        System.out.println("\nTotal templates loaded: " + templates.size());

        // Load saved requests from request.txt (written by Django)
        ArrayList<RequestItem> requests = RequestStore.loadRequests();

        Scanner scanner = new Scanner(System.in);
        boolean running = true;

        while (running) {
            System.out.println("\nRequest Menu:");
            System.out.println("1. View requests");
            System.out.println("2. Generate message");
            System.out.println("3. Delete request");
            System.out.println("4. Exit");
            System.out.print("Choose an option: ");

            int choice = scanner.nextInt();
            scanner.nextLine();

            if (choice == 1) {
                System.out.println("\nSaved Requests:");
                System.out.println("-----------------");

                if (requests.isEmpty()) {
                    System.out.println("No requests found in request.txt");
                } else {
                    for (int i = 0; i < requests.size(); i++) {
                        System.out.println((i + 1) + ". " + requests.get(i));
                    }
                }

            } else if (choice == 2) {
                if (requests.isEmpty()) {
                    System.out.println("\nNo requests found in request.txt");
                } else {
                    System.out.println("\nSelect a request number to generate a message:");

                    for (int i = 0; i < requests.size(); i++) {
                        System.out.println((i + 1) + ". " + requests.get(i));
                    }

                    int requestChoice = scanner.nextInt();
                    scanner.nextLine();

                    if (requestChoice > 0 && requestChoice <= requests.size()) {
                        RequestItem selectedRequest = requests.get(requestChoice - 1);

                        System.out.println("\nGenerating Message For:");
                        System.out.println(selectedRequest);

                        String message = MessageGenerator.generateMessage(selectedRequest);

                        System.out.println("\nGenerated Message:");
                        System.out.println("-----------------");
                        System.out.println(message);
                    } else {
                        System.out.println("Invalid selection.");
                    }
                }

            } else if (choice == 3) {
                if (requests.isEmpty()) {
                    System.out.println("\nNo requests to delete.");
                } else {
                    System.out.println("\nSelect a request number to delete:");

                    for (int i = 0; i < requests.size(); i++) {
                        System.out.println((i + 1) + ". " + requests.get(i));
                    }

                    int deleteChoice = scanner.nextInt();
                    scanner.nextLine();

                    if (deleteChoice > 0 && deleteChoice <= requests.size()) {
                        RequestItem removedRequest = requests.remove(deleteChoice - 1);
                        RequestStore.saveRequests(requests);

                        System.out.println("\nDeleted Request:");
                        System.out.println(removedRequest);
                    } else {
                        System.out.println("Invalid selection.");
                    }
                }

            } else if (choice == 4) {
                running = false;
                System.out.println("\nExiting program.");

            } else {
                System.out.println("Invalid menu option.");
            }
        }

        scanner.close();
    }
}