# Executive Stakeholder Demonstration Script
**Duration:** 10 Minutes
**Goal:** Prove the platform handles intent, RAG, objection handling, booking, and CRM integration seamlessly.

## Setup Requirements
1. **Screen 1 (Left):** Split terminal showing LangGraph execution trace and Nginx access logs.
2. **Screen 2 (Right):** The web/mobile UI for the agent.
3. **Screen 3 (Background tabs):** Google Calendar, n8n Dashboard, CRM dashboard, Grafana metrics.

---

## 🎬 Scene 1: The Inbound Call (0:00 - 1:30)

**Presenter:** "We are going to simulate an inbound customer call to the AI agent. Watch the terminal trace on the left as the agent detects intent and routes the query."

*Presenter initiates the call.*

**Agent:** "Assalam o Alaikum! Main Zara hoon, NetixSol Real Estate ki AI Assistant. Aaj main aapki kya madad kar sakti hoon?"
**Customer (Presenter):** "Walikum Assalam. Mujhe DHA Lahore mein ek ghar kharidna hai."
**Agent:** "Zaroor sir, DHA Lahore ek behtareen choice hai. Aapka budget kitna hai aur kitne bedrooms chahiye?"

*👉 Presenter Action: Point to the terminal showing `Intent: property_search` and the CRM logging the new lead.*

---

## 🎬 Scene 2: RAG & Recommendation (1:30 - 3:00)

**Customer:** "Mera budget maximum 4 crore hai, aur mujhe 4 bedroom wala ghar chahiye."
**Agent:** "Sir, mere paas DHA Phase 6 mein ek shandar 4-bedroom house available hai 3.8 crore mein. Yeh park facing hai aur brand new construction hai. Kya main aapko iski mazeed details bataon?"

*👉 Presenter Action: Show the terminal where the `search_property_knowledge` tool was called. Show the JSON output from ChromaDB.*

---

## 🎬 Scene 3: Objection Handling (3:00 - 4:30)

**Customer:** "3.8 crore thora zyada hai... kya is mein negotiation ka margin hai? Aur builder kaisa hai?"
**Agent:** "Sir, market rates ke hisaab se yeh price bilkul reasonable hai kyunke material A-grade use hua hai. Lekin serious buyers ke liye thori bohat negotiation ho sakti hai. Kya aap property physically visit karna chahenge?"

*👉 Presenter Action: Highlight how the AI didn't just drop the price, but defended the value and pushed for a site visit (sales tactic).*

---

## 🎬 Scene 4: Appointment Booking (4:30 - 6:30)

**Customer:** "Haan theek hai, main Friday shaam 4 baje aana chahta hoon."
**Agent:** "Theek hai sir. Main aapki viewing Friday shaam 4 baje book kar rahi hoon. Ek confirmation email aapko bhej di jayegi. Apna khayal rakhiyega, Allah Hafiz!"

*👉 Presenter Action:*
1. *Open Google Calendar: Show the new event at 4 PM Friday.*
2. *Open Email Inbox: Show the automated n8n confirmation email.*
3. *Open CRM: Show the customer profile updated with `lead_score: 85` and status `appointment_booked`.*

---

## 🎬 Scene 5: Cancellation & Graceful Exit (6:30 - 8:00)

**Presenter:** "Now, let's simulate the customer calling back to cancel."
*Presenter initiates call.*
**Customer:** "Mera Friday 4 baje ka appointment tha, mujhe cancel karna hai."
**Agent:** "Koi masla nahi sir, main aapka appointment cancel kar deti hoon. Jab aap free hon toh dobara call kar lijiyega. Allah Hafiz."

*👉 Presenter Action:*
1. *Open Google Calendar: The event is gone.*
2. *Open CRM: Status updated back to `hot_lead`.*

---

## 🎬 Scene 6: Analytics & System Health (8:00 - 10:00)

**Presenter:** "Behind the scenes, we treat this as a mission-critical system."
*👉 Presenter Action: Open Grafana Dashboard.*
"Here you can see the end-to-end latency stays under 2 seconds. You can also see our active sessions, booking success rate, and any security violations blocked by our PromptGuard layer."

**End of Demo.**
