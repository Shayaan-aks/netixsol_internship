# Conversation Flows

## 1. Buyer Inquiry Flow
```mermaid
graph TD
    Start[Greeting] --> IdentifyIntent[Ask requirement]
    IdentifyIntent -->|Buy Property| AskDetails[Ask budget, location, size]
    AskDetails --> CheckDB[Query RAG DB for options]
    CheckDB --> PresentOptions[Present top matches]
    PresentOptions --> HandleObjections{Any objections?}
    HandleObjections -->|Yes| ResolveObjection[Address concern using KB] --> PresentOptions
    HandleObjections -->|No| ProposeVisit[Propose site visit]
    ProposeVisit --> Schedule[Book Appointment via Calendar]
    Schedule --> Confirmation[Send Email & Confirm]
    Confirmation --> End[Warm Closing]
```

## 2. Rental Inquiry Flow
```mermaid
graph TD
    Start[Greeting] --> IdentifyIntent[Ask requirement]
    IdentifyIntent -->|Rent Property| AskDetails[Ask budget, location, family size]
    AskDetails --> CheckDB[Query RAG DB for rentals]
    CheckDB --> PresentOptions[Present options]
    PresentOptions --> ProposeVisit[Propose viewing]
    ProposeVisit --> Schedule[Book Appointment]
    Schedule --> End[Warm Closing]
```

## 3. Commercial Property Inquiry Flow
```mermaid
graph TD
    Start[Greeting] --> IdentifyIntent[Ask requirement]
    IdentifyIntent -->|Commercial| AskDetails[Ask business type, area, budget]
    AskDetails --> CheckDB[Query DB for shops/offices]
    CheckDB --> ExplainROI[Explain footfall, ROI, terms]
    ExplainROI --> ProposeMeeting[Propose expert consultation/visit]
    ProposeMeeting --> Schedule[Book Appointment]
    Schedule --> End[Warm Closing]
```

## 4. Investment Inquiry Flow
```mermaid
graph TD
    Start[Greeting] --> IdentifyIntent[Ask requirement]
    IdentifyIntent -->|Investment| AskDetails[Ask investment size, duration]
    AskDetails --> QueryProjects[Query upcoming/high-ROI projects]
    QueryProjects --> Pitch[Pitch ROI and Capital Gains]
    Pitch --> ProposeMeeting[Schedule call with Senior Consultant]
    ProposeMeeting --> Schedule[Book Appointment]
    Schedule --> End[Warm Closing]
```

## 5. Returning Customer Flow
```mermaid
graph TD
    Start[Call Answered] --> CheckCallerID[Look up phone number in CRM]
    CheckCallerID --> IdentifyCustomer{Found in CRM?}
    IdentifyCustomer -->|Yes| PersonalizedGreeting["Welcome back, [Name]!"]
    IdentifyCustomer -->|No| StandardGreeting[Standard Greeting]
    PersonalizedGreeting --> CheckContext[Check last conversation]
    CheckContext --> ContinueContext[Ask about previous property/visit]
    ContinueContext --> HandleRequest[Process new request or follow-up]
    HandleRequest --> End[Warm Closing]
```

## 6. Appointment Rescheduling Flow
```mermaid
graph TD
    Start[Greeting] --> IdentifyIntent[Intent: Reschedule]
    IdentifyIntent --> CheckExisting[Lookup current appointment]
    CheckExisting --> SuggestSlots[Suggest new available slots]
    SuggestSlots --> ConfirmNewSlot[Confirm new date/time]
    ConfirmNewSlot --> UpdateCalendar[Update Calendar API]
    UpdateCalendar --> SendEmail[Send Updated Email]
    SendEmail --> End[Warm Closing]
```

## 7. Appointment Cancellation Flow
```mermaid
graph TD
    Start[Greeting] --> IdentifyIntent[Intent: Cancel]
    IdentifyIntent --> CheckExisting[Lookup current appointment]
    CheckExisting --> AskReason[Politely ask reason for cancellation]
    AskReason --> CancelCalendar[Remove from Calendar]
    CancelCalendar --> OfferReschedule{Offer to reschedule later?}
    OfferReschedule -->|Yes| SendRescheduleLink[Send booking link via SMS/Email]
    OfferReschedule -->|No| Acknowledge[Acknowledge and close gracefully]
    Acknowledge --> End[Warm Closing]
```
