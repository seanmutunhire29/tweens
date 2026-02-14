const selectElement = document.getElementById("mySelect");

// Define variables to store references to dynamic elements
let donateOpion;
let volunteerText;
let volunteerButton;
let askButton;
let asktext;
let partnerButton;
let partnerText;

// Function to remove all dynamic elements
function removeChildren() {
  donateOpion?.remove();
  volunteerText?.remove();
  volunteerButton?.remove();
  askButton?.remove();
  asktext?.remove();
  partnerButton?.remove();
  partnerText?.remove();
}

// Add event listener for the select dropdown
selectElement.addEventListener("change", () => {
  const selectedOption = selectElement.value;

  // Remove all previously created elements
  removeChildren();

  // Dynamically add new elements based on the selected option
  switch (selectedOption) {
    case "donate":
      donateOpion = document.createElement("p");
      donateOpion.innerHTML =
        'For you to donate, we kindly ask you to visit our donate page <a href="https://www.globalgiving.org/projects/transformative-education-for-refugees-in-zimbabwe/" target="_blank">here</a>';
      document.querySelector(".form-side").append(donateOpion);
      break;

    case "volunteer":
      volunteerText = document.createElement("textarea");
      volunteerText.id = "textbox";
      volunteerText.placeholder =
        "Tell Us your skills and the program for which you want to volunteer";
      volunteerText.name = "message";

      volunteerButton = document.createElement("button");
      volunteerButton.id = "formSubmit";
      volunteerButton.type = "submit";
      volunteerButton.innerHTML = "Submit";

      document.querySelector(".form-side").append(volunteerText, volunteerButton);
      break;

    case "ask":
      asktext = document.createElement("textarea");
      asktext.id = "textbox";
      asktext.placeholder =
        "Feel free to ask your questions here, and don't be afraid to be as specific and elaborate as you can be...";
      asktext.name = "message";

      askButton = document.createElement("button");
      askButton.id = "formSubmit";
      askButton.type = "submit";
      askButton.innerHTML = "Submit";

      document.querySelector(".form-side").append(asktext, askButton);
      break;

    case "partner":
      partnerText = document.createElement("textarea");
      partnerText.id = "textbox";
      partnerText.placeholder =
        "Tell Us your organisation and why you need to partner with us...";
      partnerText.name = "message";

      partnerButton = document.createElement("button");
      partnerButton.id = "formSubmit";
      partnerButton.type = "submit";
      partnerButton.innerHTML = "Submit";

      document.querySelector(".form-side").append(partnerText, partnerButton);
      break;
  }
});
