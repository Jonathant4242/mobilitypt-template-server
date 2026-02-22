from django.shortcuts import render

def home(request):
    buttons = [
        "New Patient",
        "Follow-Up Visit",
        "Eval Scheduled",
        "Checking In (Non-Active Patients)",
        "Accidental Lake Forest Phone Call",
    ]

    return render(request, "templates_app/home.html", {
        "buttons": buttons
    })
