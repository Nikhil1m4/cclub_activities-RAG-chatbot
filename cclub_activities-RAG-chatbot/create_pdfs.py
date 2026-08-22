import fitz  # PyMuPDF

PUBLIC_CONTENT = """JUGAAD Robotics Club - Public Knowledge Base & Activity Overview

1. ABOUT JUGAAD ROBOTICS CLUB
JUGAAD Robotics Club at UIET focuses on robotics, embedded systems, IoT, automation, and hands-on technical learning. The club organizes workshops, competitions, technical sessions, and project showcases to encourage innovation and practical engineering skills among students.

2. RECRUITMENT & MEMBERSHIP
- Annual recruitment drives occur at the beginning of the academic semester (September/October).
- Open to all undergraduate students interested in robotics, software development, hardware prototyping, and electronics.
- Selection process involves a basic logic test and a practical hands-on mini-project challenge.

3. PUBLIC EVENTS AND WORKSHOPS
- Linux Unleashed (30 September 2024): Beginner-friendly workshop introducing Linux OS, Ubuntu setup, terminal commands, and open-source computing.
- Tinker@JUGAAD 2025 - Semiconductor Workshop (28 February 2025): Guest lecture by Prof. Amanpreet Kaur (Oakland University, USA) on modern semiconductor design and chip manufacturing trends.
- Moonshot - Chandrayaan-3 Landing Celebration (23 August 2023): Live broadcast and technical discussion celebrating ISRO's lunar landing.
- JUGAAD Events at Goonj 2024 & Utsav 2024: Interactive activities including Patience Tester, Guess the Component, Circuit Tricks, and Robo-Soccer.

4. COMPETITIONS & AWARDS
- Line Follower Robot (LFR) Competition at Chandigarh University: Autonomous robot showcase featuring sensor navigation.
- Techzibition @ PEC (21 January 2024): Punjab Zonals for Cognizance 2024 IIT Roorkee. Selected for zonal representation.
- Cognizance 2024 at IIT Roorkee (14-17 March 2024): National tech competition featuring Nano Navigator and Faraday Station.

5. FEATURED PROJECTS (PUBLIC OVERVIEW)
- Nano Navigator: Autonomous micromouse maze-solving robot.
- Faraday Station: Mobile contactless wireless EV charging concept.
- Tesla Coil Project: High-frequency wireless power transfer demonstration.
- E-Conveyor: Industrial automated conveyor belt system.
- Line Follower Robot (LFR): Sensor-guided autonomous path tracking.
- RC Car: RF remote-controlled mobile platform.
"""

MEMBER_CONTENT = """JUGAAD Robotics Club - Internal Member Knowledge Base & Operations Manual

1. INTERNAL LOGISTICS & LAB OPERATIONS
- Lab Access & Location: UIET Robotics Lab 204, Second Floor, Block 2.
- Access Hours: Authorized core members have 24/7 RFID keycard access. General members have access 9:00 AM - 8:00 PM on weekdays.
- Equipment Checkout Protocol: All oscilloscopes, soldering stations, Jetson Nano modules, and 3D printers must be logged in the lab inventory register prior to use. High-value sensors require approval from the Hardware Lead.

2. FINANCIAL & BUDGET ALLOCATIONS (FY 2024-2025)
- Total Annual Allocated Budget: INR 4,50,000 (~$5,400 USD).
- Category Breakdown:
  * Component Procurement & PCB Fabrication: INR 2,00,000
  * Travel Grants (Cognizance IIT Roorkee & National Finals): INR 1,20,000
  * Workshop Hardware Kits (Linux Unleashed & Arduino Kits): INR 80,000
  * Emergency Maintenance & Tool Upgrades: INR 50,000
- Reimbursement Process: Submit original GST tax invoices to the Treasurer (Priya Sharma) within 14 days of purchase.

3. EXECUTIVE BOARD & TEAM DIRECTORY
- President: Rahul Verma (Contact: +91-9876543210, rahul.president@jugaadrobotics.org)
- Technical Lead / Software Head: Ananya Gupta (Contact: +91-9876543211, ananya.tech@jugaadrobotics.org)
- Hardware & Systems Lead: Vikram Singh (Contact: +91-9876543212, vikram.hardware@jugaadrobotics.org)
- Treasurer & Operations: Priya Sharma (Contact: +91-9876543213, priya.finance@jugaadrobotics.org)
- Weekly Core Team Standups: Wednesdays at 6:00 PM in Lab 204.

4. INTERNAL REPOSITORIES & API CREDENTIALS
- GitHub Organization: github.com/jugaad-robotics-internal
- Microcontroller Flashing & Codebase Guidelines: MicroMouse maze-solving algorithm (FloodFill v3) is maintained in repo nano-navigator-firmware.
- Testing Credentials & Wi-Fi: Lab Internal Wi-Fi SSID: JUGAAD_LAB_5G (Password: Jugaad@Robo2025!).

5. MEMBER EVALUATION & GRADING RUBRIC
- Internal Hackathons & Competition Selection Criteria:
  * Hardware Rigidity & Soldering Quality: 30%
  * Software Algorithm Efficiency & Real-Time Performance: 40%
  * Documentation & Git Commit Hygiene: 20%
  * Peer Collaboration & Lab Conduct: 10%
- Members scoring above 85% receive full travel grant sponsorships for outstation tech fests.
"""

def generate_pdf(filename, text_content):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size
    rect = fitz.Rect(40, 40, 555, 802)
    page.insert_textbox(rect, text_content, fontsize=10, fontname="helv")
    doc.save(filename)
    doc.close()
    print(f"Generated {filename} successfully.")

if __name__ == "__main__":
    generate_pdf("public.pdf", PUBLIC_CONTENT)
    generate_pdf("member.pdf", MEMBER_CONTENT)
