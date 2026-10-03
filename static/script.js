const welcomeButton = document.getElementById("welcomeButton");

if (welcomeButton) {
  welcomeButton.addEventListener("click", () => {
    window.alert("Welcome to StudentHub!");
  });
}
