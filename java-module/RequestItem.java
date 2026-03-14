public class RequestItem {

    private String firstName;
    private String phoneNumber;
    private String eventName;
    private String details;
    private String preferredDay;
    private String preferredDate;
    private String earliestTime;
    private String latestTime;

    public RequestItem(
            String firstName,
            String phoneNumber,
            String eventName,
            String details,
            String preferredDay,
            String preferredDate,
            String earliestTime,
            String latestTime) {
        this.firstName = firstName;
        this.phoneNumber = phoneNumber;
        this.eventName = eventName;
        this.details = details;
        this.preferredDay = preferredDay;
        this.preferredDate = preferredDate;
        this.earliestTime = earliestTime;
        this.latestTime = latestTime;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public String getEventName() {
        return eventName;
    }

    public String getDetails() {
        return details;
    }

    public String getPreferredDay() {
        return preferredDay;
    }

    public String getPreferredDate() {
        return preferredDate;
    }

    public String getEarliestTime() {
        return earliestTime;
    }

    public String getLatestTime() {
        return latestTime;
    }

    @Override
    public String toString() {
        return firstName + " | "
                + preferredDay + " " + preferredDate + " | "
                + earliestTime + " - " + latestTime;
    }
}
