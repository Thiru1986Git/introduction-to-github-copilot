document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  let fetchCounter = 0; // used to discard out‑of‑order responses
  async function fetchActivities() {
    const thisFetch = ++fetchCounter;
    try {
      // disable cache so we always get fresh data after signup/unregister
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();

      // if another fetch started after this one, ignore the results
      if (thisFetch !== fetchCounter) return;

      // Clear loading message
      activitiesList.innerHTML = "";
      // clear dropdown too (otherwise options accumulate)
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        // generate participants section with delete icons
        let participantsSection = "";
        if (details.participants && details.participants.length > 0) {
          const items = details.participants
            .map(
              (p) => `<li><span class="participant-email">${p}</span> <span data-activity="${name}" data-email="${p}" class="delete-icon" title="Unregister">&times;</span></li>`
            )
            .join("");
          participantsSection = `
            <p><strong>Participants:</strong></p>
            <ul class="participants-list">
              ${items}
            </ul>
          `;
        } else {
          participantsSection = `
            <p><strong>Participants:</strong> <em>None yet</em></p>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsSection}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Event delegation for delete icons
  activitiesList.addEventListener("click", async (evt) => {
    if (evt.target.classList.contains("delete-icon")) {
      const activity = evt.target.dataset.activity;
      const email = evt.target.dataset.email;
      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
          {
            method: "POST",
          }
        );
        const result = await response.json();
        if (response.ok) {
          messageDiv.textContent = result.message;
          messageDiv.className = "success";
          fetchActivities();
        } else {
          messageDiv.textContent = result.detail || "Unable to unregister";
          messageDiv.className = "error";
        }
        messageDiv.classList.remove("hidden");
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } catch (error) {
        messageDiv.textContent = "Failed to unregister. Please try again.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        console.error("Error unregistering:", error);
      }
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // refresh the list so participants are updated
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
