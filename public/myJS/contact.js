const selectElement = document.getElementById("mySelect");
const messageBox = document.getElementById("messageBox");
const submitButton = document.getElementById("formSubmit");
const formSide = document.querySelector(".form-side");

let donateOpion;

function resetFormHelpers() {
  donateOpion?.remove();
  donateOpion = undefined;

  if (messageBox) {
    messageBox.classList.remove("hidden");
    messageBox.value = "";
    messageBox.placeholder = "Message";
  }

  if (submitButton) {
    submitButton.classList.remove("hidden");
  }
}

// Add event listener for the select dropdown
selectElement.addEventListener("change", () => {
  const selectedOption = selectElement.value;

  resetFormHelpers();

  // Dynamically add new elements based on the selected option
  switch (selectedOption) {
    case "donate":
      donateOpion = document.createElement("p");
      donateOpion.className = "mt-3 text-sm text-slate-600";
      donateOpion.innerHTML =
        'For you to donate, we kindly ask you to visit our donate page <a href="https://www.globalgiving.org/projects/transformative-education-for-refugees-in-zimbabwe/" target="_blank" class="font-semibold text-brand-blue">here</a>.';
      formSide.append(donateOpion);

      if (messageBox) {
        messageBox.classList.add("hidden");
      }

      if (submitButton) {
        submitButton.classList.add("hidden");
      }
      break;

    case "volunteer":
      if (messageBox) {
        messageBox.placeholder =
          "Tell us your skills and the program for which you want to volunteer";
      }
      break;

    case "ask":
      if (messageBox) {
        messageBox.placeholder =
          "Feel free to ask your questions here, and don't be afraid to be as specific and elaborate as you can be...";
      }
      break;

    case "partner":
      if (messageBox) {
        messageBox.placeholder =
          "Tell us your organisation and why you need to partner with us...";
      }
      break;
  }
});
